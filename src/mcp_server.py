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


class MCPServer:
    """Main MCP Server application"""
    
    def __init__(self):
        self.executor = CommandExecutor()
        self.kubectl = KubectlHandler(self.executor)
        self.git = GitHandler(self.executor)
        self.flux = FluxHandler(self.executor)
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
        
        # Monitoring endpoints
        self.app.router.add_get('/prometheus/query', self.handle_prometheus_query)
        self.app.router.add_get('/alertmanager/alerts', self.handle_alertmanager_alerts)
        
        # System endpoints
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/ready', self.handle_ready)
        self.app.router.add_get('/version', self.handle_version)
        
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
    
    async def handle_prometheus_query(self, request):
        """Query Prometheus metrics"""
        query = request.query.get('query')
        
        if not query:
            return web.json_response({'error': 'Query parameter required'}, status=400)
        
        prometheus_url = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')
        
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
        alertmanager_url = os.getenv('ALERTMANAGER_URL', 'http://alertmanager:9093')
        
        cmd = ['curl', '-s', f'{alertmanager_url}/api/v1/alerts']
        result = await self.executor.execute(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return web.json_response(data)
            except json.JSONDecodeError:
                return web.json_response({'error': 'Invalid response from Alertmanager'}, status=500)
        
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
        
        return web.json_response({
            'service': 'ai-sre-mcp-server',
            'version': '1.0.0',
            'tools': versions
        })
    
    def run(self):
        """Run the server"""
        port = int(os.getenv('MCP_SERVER_PORT', '8080'))
        logger.info(f"Starting MCP Server on port {port}")
        web.run_app(self.app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    server = MCPServer()
    server.run()
