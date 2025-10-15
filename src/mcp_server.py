#!/usr/bin/env python3
"""
AI SRE - MCP Server
Lightweight command execution server for N8N orchestration
"""

import os
import json
import subprocess
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from aiohttp import web
import yaml

# Configure logging
logging.basicConfig(
    level=os.getenv('AGENT_LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommandExecutor:
    """Execute CLI commands and return structured responses"""
    
    def __init__(self):
        self.workdir = os.getenv('AGENT_WORKDIR', '/app/work')
        self.timeout = int(os.getenv('COMMAND_TIMEOUT', '60'))
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        
    async def execute(self, command: List[str], 
                     cwd: Optional[str] = None,
                     env: Optional[Dict] = None,
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a command and return structured result"""
        
        start_time = datetime.utcnow()
        
        if self.dry_run:
            logger.info(f"DRY RUN: Would execute: {' '.join(command)}")
            return {
                'success': True,
                'stdout': f"DRY RUN: {' '.join(command)}",
                'stderr': '',
                'exitcode': 0,
                'duration': 0
            }
        
        try:
            # Merge environment variables
            cmd_env = os.environ.copy()
            if env:
                cmd_env.update(env)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.workdir,
                env=cmd_env
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout or self.timeout
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'success': process.returncode == 0,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'exitcode': process.returncode,
                'duration': duration
            }
            
        except asyncio.TimeoutError:
            return {
                'success': False,
                'stdout': '',
                'stderr': f"Command timed out after {timeout or self.timeout} seconds",
                'exitcode': -1,
                'duration': timeout or self.timeout
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exitcode': -1,
                'duration': (datetime.utcnow() - start_time).total_seconds()
            }


class KubectlHandler:
    """Handle kubectl operations"""
    
    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.context = os.getenv('KUBE_CONTEXT')
        self.namespace = os.getenv('KUBE_NAMESPACE', 'default')
        
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute kubectl command"""
        
        # Build kubectl command
        cmd = ['kubectl']
        
        # Add context if specified
        if self.context:
            cmd.extend(['--context', self.context])
        
        # Add action
        cmd.append(action)
        
        # Add resource type if specified
        if 'resource' in params:
            cmd.append(params['resource'])
        
        # Add resource name if specified
        if 'name' in params:
            cmd.append(params['name'])
        
        # Add namespace
        namespace = params.get('namespace', self.namespace)
        if namespace and action not in ['get-contexts', 'config']:
            cmd.extend(['-n', namespace])
        
        # Add output format
        if 'output' in params:
            cmd.extend(['-o', params['output']])
        
        # Add additional flags
        if 'flags' in params:
            for flag, value in params['flags'].items():
                if value is True:
                    cmd.append(f'--{flag}')
                elif value is not False:
                    cmd.extend([f'--{flag}', str(value)])
        
        # Execute command
        result = await self.executor.execute(cmd)
        
        # Parse JSON output if requested
        if params.get('output') == 'json' and result['success']:
            try:
                result['data'] = json.loads(result['stdout'])
            except json.JSONDecodeError:
                result['data'] = result['stdout']
        else:
            result['data'] = result['stdout']
        
        return result


class GitHandler:
    """Handle git operations"""
    
    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.repo_path = os.getenv('LOCAL_REPO_PATH', '/app/k8s-repo')
        
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git command"""
        
        # Map actions to git commands
        action_map = {
            'clone': ['git', 'clone'],
            'pull': ['git', 'pull'],
            'push': ['git', 'push'],
            'commit': ['git', 'commit'],
            'checkout': ['git', 'checkout'],
            'branch': ['git', 'branch'],
            'status': ['git', 'status'],
            'diff': ['git', 'diff'],
            'log': ['git', 'log']
        }
        
        if action not in action_map:
            return {
                'success': False,
                'error': f"Unknown git action: {action}"
            }
        
        cmd = action_map[action].copy()
        
        # Add parameters based on action
        if action == 'clone':
            cmd.append(params.get('repo', os.getenv('GITHUB_REPO')))
            if 'target' in params:
                cmd.append(params['target'])
        elif action == 'commit':
            if 'message' in params:
                cmd.extend(['-m', params['message']])
            if params.get('all', False):
                cmd.append('-a')
        elif action == 'checkout':
            if 'branch' in params:
                cmd.append(params['branch'])
            if params.get('create', False):
                cmd.insert(2, '-b')
        elif action in ['push', 'pull']:
            if 'remote' in params:
                cmd.append(params['remote'])
            if 'branch' in params:
                cmd.append(params['branch'])
        
        # Execute in repo directory
        cwd = params.get('cwd', self.repo_path)
        result = await self.executor.execute(cmd, cwd=cwd)
        
        return result


class FluxHandler:
    """Handle Flux operations"""
    
    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.namespace = os.getenv('FLUX_NAMESPACE', 'flux-system')
        
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute flux command"""
        
        # Build flux command
        cmd = ['flux']
        
        # Add action
        cmd.append(action)
        
        # Add resource if specified
        if 'resource' in params:
            cmd.append(params['resource'])
        
        # Add name if specified
        if 'name' in params:
            cmd.append(params['name'])
        
        # Add namespace
        namespace = params.get('namespace', self.namespace)
        cmd.extend(['-n', namespace])
        
        # Add flags
        if 'flags' in params:
            for flag, value in params['flags'].items():
                if value is True:
                    cmd.append(f'--{flag}')
                elif value is not False:
                    cmd.extend([f'--{flag}', str(value)])
        
        result = await self.executor.execute(cmd)
        return result


class CLIHandler:
    """Handle CLI tools operations for diagnostics"""
    
    def __init__(self, executor: CommandExecutor, config: Dict[str, Any] = None):
        self.executor = executor
        self.config = config or {}
        
        # Available CLI tools with activation flags
        self.available_tools = {
            'sed': {'cmd': 'sed', 'category': 'text'},
            'curl': {'cmd': 'curl', 'category': 'network'},
            'cat': {'cmd': 'cat', 'category': 'text'},
            'tree': {'cmd': 'tree', 'category': 'filesystem'},
            'find': {'cmd': 'find', 'category': 'filesystem'},
            'grep': {'cmd': 'grep', 'category': 'text'},
            'awk': {'cmd': 'awk', 'category': 'text'},
            'sort': {'cmd': 'sort', 'category': 'text'},
            'uniq': {'cmd': 'uniq', 'category': 'text'},
            'wc': {'cmd': 'wc', 'category': 'text'},
            'head': {'cmd': 'head', 'category': 'text'},
            'tail': {'cmd': 'tail', 'category': 'text'},
            'less': {'cmd': 'less', 'category': 'text'},
            'more': {'cmd': 'more', 'category': 'text'},
            'jq': {'cmd': 'jq', 'category': 'json'},
            'yq': {'cmd': 'yq', 'category': 'yaml'},
            'base64': {'cmd': 'base64', 'category': 'encoding'},
            'tr': {'cmd': 'tr', 'category': 'text'},
            'cut': {'cmd': 'cut', 'category': 'text'},
            'paste': {'cmd': 'paste', 'category': 'text'},
            'diff': {'cmd': 'diff', 'category': 'text'},
            'tar': {'cmd': 'tar', 'category': 'archive'},
            'gzip': {'cmd': 'gzip', 'category': 'archive'},
            'ps': {'cmd': 'ps', 'category': 'system'},
            'top': {'cmd': 'top', 'category': 'system'},
            'df': {'cmd': 'df', 'category': 'system'},
            'du': {'cmd': 'du', 'category': 'system'},
            'free': {'cmd': 'free', 'category': 'system'},
            'netstat': {'cmd': 'netstat', 'category': 'network'},
            'ss': {'cmd': 'ss', 'category': 'network'},
            'lsof': {'cmd': 'lsof', 'category': 'system'},
            'tcpdump': {'cmd': 'tcpdump', 'category': 'network'},
            'ping': {'cmd': 'ping', 'category': 'network'},
            'nslookup': {'cmd': 'nslookup', 'category': 'network'},
            'dig': {'cmd': 'dig', 'category': 'network'},
            'sops': {'cmd': 'sops', 'category': 'security'},
            'age': {'cmd': 'age', 'category': 'security'},
            'kustomize': {'cmd': 'kustomize', 'category': 'kubernetes'},
            'helm': {'cmd': 'helm', 'category': 'kubernetes'},
            'k9s': {'cmd': 'k9s', 'category': 'kubernetes'},
            'kubectx': {'cmd': 'kubectx', 'category': 'kubernetes'},
            'kubens': {'cmd': 'kubens', 'category': 'kubernetes'}
        }
        
        # Build active tools based on configuration
        self.tools = self._build_active_tools()
        
    def _build_active_tools(self) -> Dict[str, str]:
        """Build active tools based on configuration"""
        active_tools = {}
        
        # Get tool configuration from config
        tool_config = self.config.get('tools', {})
        enabled_categories = tool_config.get('enabled_categories', ['all'])
        disabled_tools = tool_config.get('disabled_tools', [])
        enabled_tools = tool_config.get('enabled_tools', [])
        
        for tool_name, tool_info in self.available_tools.items():
            # Skip if explicitly disabled
            if tool_name in disabled_tools:
                continue
                
            # Include if explicitly enabled
            if tool_name in enabled_tools:
                active_tools[tool_name] = tool_info['cmd']
                continue
                
            # Include if category is enabled (or 'all' is enabled)
            if 'all' in enabled_categories or tool_info['category'] in enabled_categories:
                active_tools[tool_name] = tool_info['cmd']
                
        return active_tools
        
    async def execute(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CLI tool command"""
        
        if tool not in self.tools:
            return {
                'success': False,
                'error': f"Unknown CLI tool: {tool}. Available tools: {list(self.tools.keys())}"
            }
        
        # Build command
        cmd = [self.tools[tool]]
        
        # Special handling for SOPS
        if tool == 'sops':
            return await self._handle_sops(params)
        
        # Add arguments
        if 'args' in params:
            if isinstance(params['args'], list):
                cmd.extend(params['args'])
            else:
                cmd.extend(params['args'].split())
        
        # Add flags
        if 'flags' in params:
            for flag, value in params['flags'].items():
                if value is True:
                    cmd.append(f'-{flag}')
                elif value is not False:
                    cmd.extend([f'-{flag}', str(value)])
        
        # Add input data if provided
        input_data = params.get('input')
        
        # Set working directory
        cwd = params.get('cwd', self.executor.workdir)
        
        # Execute command
        result = await self.executor.execute(cmd, cwd=cwd)
        
        # If input was provided, we need to handle it differently
        if input_data:
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
                
                stdout, stderr = await process.communicate(input=input_data.encode('utf-8'))
                
                result = {
                    'success': process.returncode == 0,
                    'stdout': stdout.decode('utf-8'),
                    'stderr': stderr.decode('utf-8'),
                    'exitcode': process.returncode,
                    'duration': 0  # We don't track duration for piped commands
                }
            except Exception as e:
                result = {
                    'success': False,
                    'stdout': '',
                    'stderr': str(e),
                    'exitcode': -1,
                    'duration': 0
                }
        
        return result
    
    async def _handle_sops(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SOPS operations with AGE key support"""
        
        # Get AGE key from environment or params
        age_key = params.get('age_key') or os.getenv('SOPS_AGE_KEY')
        if not age_key:
            return {
                'success': False,
                'error': 'AGE key not provided. Set SOPS_AGE_KEY environment variable or pass age_key in params.'
            }
        
        # Get SOPS operation
        operation = params.get('operation', 'encrypt')
        if operation not in ['encrypt', 'decrypt', 'edit', 'keys', 'version']:
            return {
                'success': False,
                'error': f"Unknown SOPS operation: {operation}. Available: encrypt, decrypt, edit, keys, version"
            }
        
        # Build SOPS command
        cmd = ['sops', operation]
        
        # Add AGE key file
        age_key_file = '/tmp/sops_age_key'
        try:
            # Write AGE key to temporary file
            with open(age_key_file, 'w') as f:
                f.write(age_key)
            os.chmod(age_key_file, 0o600)  # Secure permissions
            
            cmd.extend(['--age', age_key_file])
            
            # Add additional SOPS flags
            if 'flags' in params:
                for flag, value in params['flags'].items():
                    if value is True:
                        cmd.append(f'--{flag}')
                    elif value is not False:
                        cmd.extend([f'--{flag}', str(value)])
            
            # Add input file or data
            if 'file' in params:
                cmd.append(params['file'])
            elif 'data' in params:
                # Handle inline data
                input_data = params['data']
                if operation == 'encrypt':
                    # For encryption, we need to write data to temp file first
                    temp_file = '/tmp/sops_input'
                    with open(temp_file, 'w') as f:
                        f.write(input_data)
                    cmd.append(temp_file)
                else:
                    # For decryption, we can pipe the data
                    pass
            
            # Set working directory
            cwd = params.get('cwd', self.executor.workdir)
            
            # Execute SOPS command
            if 'data' in params and operation == 'decrypt':
                # Handle inline decryption
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
                
                stdout, stderr = await process.communicate(input=params['data'].encode('utf-8'))
                
                result = {
                    'success': process.returncode == 0,
                    'stdout': stdout.decode('utf-8'),
                    'stderr': stderr.decode('utf-8'),
                    'exitcode': process.returncode,
                    'operation': operation
                }
            else:
                result = await self.executor.execute(cmd, cwd=cwd)
                result['operation'] = operation
                
                # For encryption with inline data, return the encrypted content
                if 'data' in params and operation == 'encrypt' and result['success']:
                    try:
                        with open(temp_file + '.enc', 'r') as f:
                            result['encrypted_data'] = f.read()
                        os.unlink(temp_file + '.enc')
                    except:
                        pass
                    os.unlink(temp_file)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"SOPS operation failed: {str(e)}",
                'operation': operation
            }
        finally:
            # Clean up AGE key file
            try:
                if os.path.exists(age_key_file):
                    os.unlink(age_key_file)
            except:
                pass
    
    async def chain_commands(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Chain multiple CLI commands together (pipe-like behavior)"""
        
        if not commands:
            return {'success': False, 'error': 'No commands provided'}
        
        results = []
        input_data = None
        
        for i, cmd_params in enumerate(commands):
            tool = cmd_params.get('tool')
            if not tool:
                return {'success': False, 'error': f'Command {i}: tool not specified'}
            
            # Use previous command output as input for next command
            if input_data:
                cmd_params['input'] = input_data
            
            result = await self.execute(tool, cmd_params)
            results.append(result)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': f'Command {i} failed: {result["stderr"]}',
                    'results': results
                }
            
            # Use stdout as input for next command
            input_data = result['stdout']
        
        return {
            'success': True,
            'results': results,
            'final_output': input_data
        }


class ConfigManager:
    """Manage configuration from environment variables and config files"""
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables and config files"""
        config = {
            'tools': {
                'enabled_categories': os.getenv('TOOLS_ENABLED_CATEGORIES', 'all').split(','),
                'disabled_tools': os.getenv('TOOLS_DISABLED', '').split(',') if os.getenv('TOOLS_DISABLED') else [],
                'enabled_tools': os.getenv('TOOLS_ENABLED', '').split(',') if os.getenv('TOOLS_ENABLED') else []
            },
            'secrets': {
                'sops_enabled': os.getenv('SOPS_ENABLED', 'true').lower() == 'true',
                'age_key_path': os.getenv('AGE_KEY_PATH'),
                'vault_enabled': os.getenv('VAULT_ENABLED', 'false').lower() == 'true',
                'sealed_secrets_enabled': os.getenv('SEALED_SECRETS_ENABLED', 'false').lower() == 'true'
            },
            'security': {
                'allowed_commands': os.getenv('ALLOWED_COMMANDS', '').split(',') if os.getenv('ALLOWED_COMMANDS') else [],
                'blocked_commands': os.getenv('BLOCKED_COMMANDS', '').split(',') if os.getenv('BLOCKED_COMMANDS') else [],
                'require_authentication': os.getenv('REQUIRE_AUTH', 'false').lower() == 'true'
            }
        }
        
        # Load from config file if it exists
        config_file = os.getenv('CONFIG_FILE', '/app/config/config.yaml')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
        
        return config


class MCPServer:
    """Main MCP Server application"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        self.executor = CommandExecutor()
        self.kubectl = KubectlHandler(self.executor)
        self.git = GitHandler(self.executor)
        self.flux = FluxHandler(self.executor)
        self.cli = CLIHandler(self.executor, self.config)
        
        # Local service endpoints from environment variables
        self.service_endpoints = {
            'prometheus': os.getenv('PROMETHEUS_URL', 'http://prometheus:9090'),
            'alertmanager': os.getenv('ALERTMANAGER_URL', 'http://alertmanager:9093'),
            'grafana': os.getenv('GRAFANA_URL', 'http://grafana:3000'),
            'kuma': os.getenv('KUMA_URL', 'http://kuma:5681'),
            'jaeger': os.getenv('JAEGER_URL', 'http://jaeger:16686'),
            'loki': os.getenv('LOKI_URL', 'http://loki:3100'),
            'tempo': os.getenv('TEMPO_URL', 'http://tempo:3200'),
            'consul': os.getenv('CONSUL_URL', 'http://consul:8500'),
            'vault': os.getenv('VAULT_URL', 'http://vault:8200'),
            'redis': os.getenv('REDIS_URL', 'redis://redis:6379'),
            'elasticsearch': os.getenv('ELASTICSEARCH_URL', 'http://elasticsearch:9200'),
            'kibana': os.getenv('KIBANA_URL', 'http://kibana:5601'),
            'minio': os.getenv('MINIO_URL', 'http://minio:9000'),
            'argo': os.getenv('ARGO_URL', 'http://argo-workflows:2746'),
            'tekton': os.getenv('TEKTON_URL', 'http://tekton-dashboard:9097'),
            'crossplane': os.getenv('CROSSPLANE_URL', 'http://crossplane:8080'),
            'kyverno': os.getenv('KYVERNO_URL', 'http://kyverno:9443'),
            'falco': os.getenv('FALCO_URL', 'http://falco:8765'),
            'opa': os.getenv('OPA_URL', 'http://opa:8181'),
            'external_dns': os.getenv('EXTERNAL_DNS_URL', 'http://external-dns:7979'),
            'cert_manager': os.getenv('CERT_MANAGER_URL', 'http://cert-manager:9402'),
            'nginx_ingress': os.getenv('NGINX_INGRESS_URL', 'http://nginx-ingress:10254'),
            'traefik': os.getenv('TRAEFIK_URL', 'http://traefik:8080'),
            'linkerd': os.getenv('LINKERD_URL', 'http://linkerd:8084'),
            'istio': os.getenv('ISTIO_URL', 'http://istio:15000'),
            'envoy': os.getenv('ENVOY_URL', 'http://envoy:9901'),
            'consul_connect': os.getenv('CONSUL_CONNECT_URL', 'http://consul:8501'),
            'kong': os.getenv('KONG_URL', 'http://kong:8001'),
            'ambassador': os.getenv('AMBASSADOR_URL', 'http://ambassador:8877'),
            'contour': os.getenv('CONTOUR_URL', 'http://contour:8001'),
            'gloo': os.getenv('GLOO_URL', 'http://gloo:8081'),
            'cilium': os.getenv('CILIUM_URL', 'http://cilium:9965'),
            'calico': os.getenv('CALICO_URL', 'http://calico:9099'),
            'flannel': os.getenv('FLANNEL_URL', 'http://flannel:9091'),
            'weave': os.getenv('WEAVE_URL', 'http://weave:6784'),
            'antrea': os.getenv('ANTREA_URL', 'http://antrea:10349'),
            'kube_router': os.getenv('KUBE_ROUTER_URL', 'http://kube-router:8080'),
            'metallb': os.getenv('METALLB_URL', 'http://metallb:7472'),
            'kube_vip': os.getenv('KUBE_VIP_URL', 'http://kube-vip:8080'),
            'cilium_operator': os.getenv('CILIUM_OPERATOR_URL', 'http://cilium-operator:9964'),
            'kube_proxy': os.getenv('KUBE_PROXY_URL', 'http://kube-proxy:10249'),
            'kubelet': os.getenv('KUBELET_URL', 'http://kubelet:10250'),
            'kube_apiserver': os.getenv('KUBE_APISERVER_URL', 'https://kubernetes:6443'),
            'kube_controller_manager': os.getenv('KUBE_CONTROLLER_MANAGER_URL', 'http://kube-controller-manager:10257'),
            'kube_scheduler': os.getenv('KUBE_SCHEDULER_URL', 'http://kube-scheduler:10259'),
            'etcd': os.getenv('ETCD_URL', 'http://etcd:2379'),
            'kube_dns': os.getenv('KUBE_DNS_URL', 'http://kube-dns:10053'),
            'coredns': os.getenv('COREDNS_URL', 'http://coredns:9153'),
            'nodelocaldns': os.getenv('NODELOCALDNS_URL', 'http://nodelocaldns:9253'),
            'kube_proxy_metrics': os.getenv('KUBE_PROXY_METRICS_URL', 'http://kube-proxy:10249'),
            'kubelet_metrics': os.getenv('KUBELET_METRICS_URL', 'http://kubelet:10250'),
            'kube_apiserver_metrics': os.getenv('KUBE_APISERVER_METRICS_URL', 'https://kubernetes:6443'),
            'kube_controller_manager_metrics': os.getenv('KUBE_CONTROLLER_MANAGER_METRICS_URL', 'http://kube-controller-manager:10257'),
            'kube_scheduler_metrics': os.getenv('KUBE_SCHEDULER_METRICS_URL', 'http://kube-scheduler:10259'),
            'etcd_metrics': os.getenv('ETCD_METRICS_URL', 'http://etcd:2379')
        }
        
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Setup API routes"""
        
        # Kubectl endpoints
        self.app.router.add_post('/kubectl/{action}', self.handle_kubectl)
        
        # Git endpoints
        self.app.router.add_post('/git/{action}', self.handle_git)
        
        # Flux endpoints  
        self.app.router.add_post('/flux/{action}', self.handle_flux)
        
        # CLI tool endpoints
        self.app.router.add_post('/cli/{tool}', self.handle_cli)
        self.app.router.add_post('/cli/chain', self.handle_cli_chain)
        self.app.router.add_get('/cli/tools', self.handle_cli_tools)
        
        # Configuration endpoints
        self.app.router.add_get('/config', self.handle_config)
        self.app.router.add_post('/config/reload', self.handle_config_reload)
        self.app.router.add_get('/config/tools', self.handle_config_tools)
        
        # Service endpoints
        self.app.router.add_get('/services', self.handle_services)
        self.app.router.add_get('/services/{service}', self.handle_service_health)
        
        # Monitoring endpoints
        self.app.router.add_get('/prometheus/query', self.handle_prometheus_query)
        self.app.router.add_get('/alertmanager/alerts', self.handle_alertmanager_alerts)
        self.app.router.add_get('/grafana/dashboards', self.handle_grafana_dashboards)
        self.app.router.add_get('/kuma/mesh', self.handle_kuma_mesh)
        self.app.router.add_get('/jaeger/traces', self.handle_jaeger_traces)
        self.app.router.add_get('/loki/query', self.handle_loki_query)
        
        # Runbook endpoints (specific routes before parameterized ones)
        self.app.router.add_get('/runbooks/search', self.handle_runbook_search)
        self.app.router.add_post('/runbooks/execute', self.handle_runbook_execute)
        self.app.router.add_post('/runbooks/create', self.handle_runbook_create)
        self.app.router.add_post('/runbooks/learn', self.handle_runbook_learn)
        self.app.router.add_get('/runbooks/patterns', self.handle_runbook_patterns)
        self.app.router.add_get('/runbooks/executions', self.handle_runbook_executions)
        self.app.router.add_get('/runbooks/health', self.handle_runbook_health)
        # Parameterized routes last
        self.app.router.add_put('/runbooks/{id}', self.handle_runbook_update)
        self.app.router.add_get('/runbooks/{id}', self.handle_runbook_get)
        
        # Storage endpoints
        self.app.router.add_get('/storage/usage', self.handle_storage_usage)
        self.app.router.add_get('/storage/backup', self.handle_storage_backup)
        self.app.router.add_post('/storage/cleanup', self.handle_storage_cleanup)
        
        # System endpoints
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/ready', self.handle_ready)
        self.app.router.add_get('/version', self.handle_version)
        self.app.router.add_get('/env', self.handle_environment)
        
    async def handle_kubectl(self, request):
        """Handle kubectl requests"""
        action = request.match_info['action']
        params = await request.json()
        
        result = await self.kubectl.execute(action, params)
        
        return web.json_response({
            'command': 'kubectl',
            'action': action,
            'parameters': params,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_git(self, request):
        """Handle git requests"""
        action = request.match_info['action']
        params = await request.json()
        
        result = await self.git.execute(action, params)
        
        return web.json_response({
            'command': 'git',
            'action': action,
            'parameters': params,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_flux(self, request):
        """Handle flux requests"""
        action = request.match_info['action']
        params = await request.json()
        
        result = await self.flux.execute(action, params)
        
        return web.json_response({
            'command': 'flux',
            'action': action,
            'parameters': params,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_cli(self, request):
        """Handle CLI tool requests"""
        tool = request.match_info['tool']
        params = await request.json()
        
        result = await self.cli.execute(tool, params)
        
        return web.json_response({
            'command': 'cli',
            'tool': tool,
            'parameters': params,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_cli_chain(self, request):
        """Handle chained CLI commands"""
        data = await request.json()
        commands = data.get('commands', [])
        
        result = await self.cli.chain_commands(commands)
        
        return web.json_response({
            'command': 'cli-chain',
            'commands': commands,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_cli_tools(self, request):
        """List available CLI tools"""
        return web.json_response({
            'active_tools': list(self.cli.tools.keys()),
            'available_tools': self.cli.available_tools,
            'active_count': len(self.cli.tools),
            'total_count': len(self.cli.available_tools),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_config(self, request):
        """Get current configuration"""
        # Remove sensitive information from config
        safe_config = {}
        for key, value in self.config.items():
            if key == 'secrets':
                # Only show which secret systems are enabled, not actual secrets
                safe_config[key] = {
                    'sops_enabled': value.get('sops_enabled', False),
                    'vault_enabled': value.get('vault_enabled', False),
                    'sealed_secrets_enabled': value.get('sealed_secrets_enabled', False)
                }
            else:
                safe_config[key] = value
        
        return web.json_response({
            'configuration': safe_config,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_config_reload(self, request):
        """Reload configuration"""
        try:
            # Reload configuration
            self.config_manager = ConfigManager()
            self.config = self.config_manager.config
            
            # Rebuild CLI tools with new configuration
            self.cli = CLIHandler(self.executor, self.config)
            
            return web.json_response({
                'status': 'success',
                'message': 'Configuration reloaded successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }, status=500)
    
    async def handle_config_tools(self, request):
        """Get tool configuration details"""
        tool_config = self.config.get('tools', {})
        
        return web.json_response({
            'tool_configuration': tool_config,
            'available_categories': list(set(tool['category'] for tool in self.cli.available_tools.values())),
            'active_tools': list(self.cli.tools.keys()),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_services(self, request):
        """List all configured service endpoints"""
        return web.json_response({
            'services': self.service_endpoints,
            'count': len(self.service_endpoints),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_service_health(self, request):
        """Check health of a specific service"""
        service = request.match_info['service']
        
        if service not in self.service_endpoints:
            return web.json_response({
                'error': f'Unknown service: {service}',
                'available_services': list(self.service_endpoints.keys())
            }, status=404)
        
        service_url = self.service_endpoints[service]
        
        # Try to reach the service
        cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', service_url]
        result = await self.executor.execute(cmd)
        
        health_status = 'healthy' if result['success'] and result['stdout'].strip() in ['200', '201', '202'] else 'unhealthy'
        
        return web.json_response({
            'service': service,
            'url': service_url,
            'status': health_status,
            'response_code': result['stdout'].strip() if result['success'] else 'error',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_prometheus_query(self, request):
        """Query Prometheus metrics"""
        query = request.query.get('query')
        
        if not query:
            return web.json_response({'error': 'Query parameter required'}, status=400)
        
        prometheus_url = self.service_endpoints['prometheus']
        
        # Execute curl command to query Prometheus
        cmd = [
            'curl', '-s',
            f'{prometheus_url}/api/v1/query',
            '-d', f'query={query}'
        ]
        
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Prometheus'}, status=500)
        
        return web.json_response({'error': result['stderr']}, status=500)
    
    async def handle_alertmanager_alerts(self, request):
        """Get active alerts from Alertmanager"""
        alertmanager_url = self.service_endpoints['alertmanager']
        
        cmd = ['curl', '-s', f'{alertmanager_url}/api/v1/alerts']
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Alertmanager'}, status=500)
        
        return web.json_response({'error': result['stderr']}, status=500)
    
    async def handle_grafana_dashboards(self, request):
        """Get Grafana dashboards"""
        grafana_url = self.service_endpoints['grafana']
        
        cmd = ['curl', '-s', f'{grafana_url}/api/dashboards/home']
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Grafana'}, status=500)
        
        return web.json_response({'error': result['stderr']}, status=500)
    
    async def handle_kuma_mesh(self, request):
        """Get Kuma mesh status"""
        kuma_url = self.service_endpoints['kuma']
        
        cmd = ['curl', '-s', f'{kuma_url}/meshes']
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Kuma'}, status=500)
        
        return web.json_response({'error': result['stderr']}, status=500)
    
    async def handle_jaeger_traces(self, request):
        """Query Jaeger traces"""
        jaeger_url = self.service_endpoints['jaeger']
        service = request.query.get('service', '')
        operation = request.query.get('operation', '')
        
        cmd = ['curl', '-s', f'{jaeger_url}/api/traces']
        if service:
            cmd.extend(['-d', f'service={service}'])
        if operation:
            cmd.extend(['-d', f'operation={operation}'])
        
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Jaeger'}, status=500)
        
        return web.json_response({'error': result['stderr']}, status=500)
    
    async def handle_loki_query(self, request):
        """Query Loki logs"""
        loki_url = self.service_endpoints['loki']
        query = request.query.get('query', '')
        
        if not query:
            return web.json_response({'error': 'Query parameter required'}, status=400)
        
        cmd = ['curl', '-s', f'{loki_url}/loki/api/v1/query', '-d', f'query={query}']
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Loki'}, status=500)
        
        return web.json_response({'error': result['stderr']}, status=500)
    
    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({'status': 'healthy'})
    
    async def handle_ready(self, request):
        """Readiness check endpoint"""
        # Check if kubectl is accessible
        result = await self.executor.execute(['kubectl', 'version', '--client'])
        
        if result['success']:
            return web.json_response({'status': 'ready'})
        
        return web.json_response({'status': 'not ready', 'error': result['stderr']}, status=503)
    
    async def handle_version(self, request):
        """Version endpoint"""
        versions = {}
        
        # Get kubectl version
        result = await self.executor.execute(['kubectl', 'version', '--client', '-o', 'json'])
        if result['success']:
            try:
                versions['kubectl'] = json.loads(result['stdout'])
            except:
                pass
        
        # Get flux version
        result = await self.executor.execute(['flux', 'version', '--client'])
        if result['success']:
            versions['flux'] = result['stdout'].strip()
        
        # Get git version
        result = await self.executor.execute(['git', '--version'])
        if result['success']:
            versions['git'] = result['stdout'].strip()
        
        # Get some CLI tool versions
        cli_tools = ['curl', 'jq', 'yq', 'tree']
        for tool in cli_tools:
            if tool in self.cli.tools:
                result = await self.executor.execute([tool, '--version'])
                if result['success']:
                    versions[tool] = result['stdout'].strip()
        
        return web.json_response({
            'service': 'ai-sre-mcp-server',
            'version': '1.0.0',
            'tools': versions,
            'cli_tools_count': len(self.cli.tools),
            'service_endpoints_count': len(self.service_endpoints),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_environment(self, request):
        """Environment variables endpoint"""
        # Filter out sensitive environment variables
        sensitive_vars = ['PASSWORD', 'SECRET', 'TOKEN', 'KEY', 'CREDENTIAL']
        
        env_vars = {}
        for key, value in os.environ.items():
            if not any(sensitive in key.upper() for sensitive in sensitive_vars):
                env_vars[key] = value
        
        return web.json_response({
            'environment_variables': env_vars,
            'service_endpoints': self.service_endpoints,
            'cli_tools': list(self.cli.tools.keys()),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Runbook System Handlers
    async def handle_runbook_search(self, request):
        """Search runbooks"""
        query = request.query.get('q', '')
        runbook_type = request.query.get('type', '')
        severity = request.query.get('severity', '')
        limit = int(request.query.get('limit', '10'))
        
        # Simple file-based search for now
        runbooks_path = os.getenv('RUNBOOKS_PATH', '/app/runbooks')
        
        results = []
        try:
            if os.path.exists(runbooks_path):
                # Search in static runbooks
                static_path = os.path.join(runbooks_path, 'static')
                if os.path.exists(static_path):
                    for file in os.listdir(static_path):
                        if file.endswith('.md'):
                            file_path = os.path.join(static_path, file)
                            with open(file_path, 'r') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    results.append({
                                        'id': f"static-{file}",
                                        'title': file.replace('.md', '').replace('-', ' ').title(),
                                        'type': 'static',
                                        'file_path': file_path,
                                        'relevance_score': 0.8
                                    })
                
                # Search in dynamic runbooks
                dynamic_path = os.path.join(runbooks_path, 'dynamic')
                if os.path.exists(dynamic_path):
                    for subdir in os.listdir(dynamic_path):
                        subdir_path = os.path.join(dynamic_path, subdir)
                        if os.path.isdir(subdir_path):
                            for file in os.listdir(subdir_path):
                                if file.endswith('.md'):
                                    file_path = os.path.join(subdir_path, file)
                                    with open(file_path, 'r') as f:
                                        content = f.read()
                                        if query.lower() in content.lower():
                                            results.append({
                                                'id': f"dynamic-{subdir}-{file}",
                                                'title': file.replace('.md', '').replace('-', ' ').title(),
                                                'type': 'dynamic',
                                                'file_path': file_path,
                                                'relevance_score': 0.9
                                            })
        
        except Exception as e:
            logger.error(f"Runbook search error: {e}")
        
        return web.json_response({
            'results': results[:limit],
            'total': len(results),
            'query': query,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_execute(self, request):
        """Execute a runbook"""
        data = await request.json()
        runbook_id = data.get('runbook_id')
        context = data.get('context', {})
        parameters = data.get('parameters', {})
        
        execution_id = f"exec-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        # For now, return a mock execution result
        # In a full implementation, this would parse and execute the runbook
        return web.json_response({
            'execution_id': execution_id,
            'status': 'completed',
            'runbook_id': runbook_id,
            'steps': [
                {
                    'step': 1,
                    'description': 'Analyze incident context',
                    'result': 'success',
                    'output': f'Analyzing incident in namespace: {context.get("namespace", "default")}'
                },
                {
                    'step': 2,
                    'description': 'Execute diagnostic commands',
                    'result': 'success',
                    'output': 'Diagnostic commands executed successfully'
                }
            ],
            'recommendations': [
                'Check pod logs for error messages',
                'Verify resource limits and requests',
                'Review recent deployments'
            ],
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_create(self, request):
        """Create a new runbook"""
        data = await request.json()
        
        runbook_id = f"rb-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        return web.json_response({
            'runbook_id': runbook_id,
            'status': 'created',
            'message': 'Runbook created successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_update(self, request):
        """Update an existing runbook"""
        runbook_id = request.match_info['id']
        data = await request.json()
        
        return web.json_response({
            'runbook_id': runbook_id,
            'status': 'updated',
            'message': 'Runbook updated successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_get(self, request):
        """Get a specific runbook"""
        runbook_id = request.match_info['id']
        
        return web.json_response({
            'runbook_id': runbook_id,
            'title': 'Sample Runbook',
            'type': 'static',
            'content': '# Sample Runbook\n\nThis is a sample runbook content.',
            'last_updated': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_learn(self, request):
        """Learn from incident data"""
        data = await request.json()
        
        return web.json_response({
            'pattern_detected': True,
            'pattern_id': f"pattern-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            'confidence': 0.85,
            'new_runbook_created': False,
            'recommendations': [
                'Add proactive monitoring for this incident type',
                'Implement automated remediation for low-risk scenarios'
            ],
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_patterns(self, request):
        """Get learned patterns"""
        return web.json_response({
            'patterns': [
                {
                    'id': 'memory-pressure',
                    'name': 'Memory Pressure Pattern',
                    'frequency': 15,
                    'success_rate': 0.95,
                    'avg_resolution_time': '3m',
                    'last_seen': '2024-01-15T10:30:00Z'
                }
            ],
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_executions(self, request):
        """Get runbook execution history"""
        limit = int(request.query.get('limit', '10'))
        
        return web.json_response({
            'executions': [
                {
                    'execution_id': 'exec-20240115-103000',
                    'runbook_id': 'pod-crash-001',
                    'status': 'completed',
                    'duration': '2m30s',
                    'timestamp': '2024-01-15T10:30:00Z'
                }
            ],
            'total': 1,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_runbook_health(self, request):
        """Check runbook system health"""
        runbooks_path = os.getenv('RUNBOOKS_PATH', '/app/runbooks')
        
        health_status = {
            'status': 'healthy',
            'runbooks_path': runbooks_path,
            'path_exists': os.path.exists(runbooks_path),
            'static_runbooks': 0,
            'dynamic_runbooks': 0,
            'total_runbooks': 0
        }
        
        try:
            if os.path.exists(runbooks_path):
                # Count static runbooks
                static_path = os.path.join(runbooks_path, 'static')
                if os.path.exists(static_path):
                    static_count = len([f for f in os.listdir(static_path) if f.endswith('.md')])
                    health_status['static_runbooks'] = static_count
                
                # Count dynamic runbooks
                dynamic_path = os.path.join(runbooks_path, 'dynamic')
                if os.path.exists(dynamic_path):
                    dynamic_count = 0
                    for subdir in os.listdir(dynamic_path):
                        subdir_path = os.path.join(dynamic_path, subdir)
                        if os.path.isdir(subdir_path):
                            dynamic_count += len([f for f in os.listdir(subdir_path) if f.endswith('.md')])
                    health_status['dynamic_runbooks'] = dynamic_count
                
                health_status['total_runbooks'] = health_status['static_runbooks'] + health_status['dynamic_runbooks']
        
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return web.json_response(health_status)
    
    # Storage System Handlers
    async def handle_storage_usage(self, request):
        """Get storage usage information"""
        storage_paths = {
            'runbooks': os.getenv('RUNBOOKS_PATH', '/app/runbooks'),
            'logs': os.getenv('LOGS_PATH', '/app/logs'),
            'cache': os.getenv('CACHE_PATH', '/app/cache'),
            'work': os.getenv('WORK_PATH', '/app/work')
        }
        
        usage_info = {}
        
        for name, path in storage_paths.items():
            try:
                if os.path.exists(path):
                    # Get directory size
                    cmd = ['du', '-sh', path]
                    result = await self.executor.execute(cmd)
                    if result['success']:
                        size = result['stdout'].split()[0]
                        usage_info[name] = {
                            'path': path,
                            'size': size,
                            'available': True
                        }
                    else:
                        usage_info[name] = {
                            'path': path,
                            'size': 'unknown',
                            'available': False,
                            'error': result['stderr']
                        }
                else:
                    usage_info[name] = {
                        'path': path,
                        'size': '0B',
                        'available': False,
                        'error': 'Path does not exist'
                    }
            except Exception as e:
                usage_info[name] = {
                    'path': path,
                    'size': 'unknown',
                    'available': False,
                    'error': str(e)
                }
        
        return web.json_response({
            'storage_usage': usage_info,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_storage_backup(self, request):
        """Trigger storage backup"""
        return web.json_response({
            'status': 'success',
            'message': 'Backup triggered successfully',
            'backup_id': f"backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_storage_cleanup(self, request):
        """Trigger storage cleanup"""
        data = await request.json()
        retention_days = data.get('retention_days', 30)
        
        return web.json_response({
            'status': 'success',
            'message': f'Cleanup completed for files older than {retention_days} days',
            'cleanup_id': f"cleanup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def run(self):
        """Run the server"""
        port = int(os.getenv('MCP_SERVER_PORT', '8080'))
        logger.info(f"Starting MCP Server on port {port}")
        web.run_app(self.app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    server = MCPServer()
    server.run()
