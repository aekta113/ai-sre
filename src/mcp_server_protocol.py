#!/usr/bin/env python3
"""
AI SRE - MCP Protocol Server
Model Context Protocol compliant server for N8N integration
"""

import os
import json
import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import uuid

from aiohttp import web, WSMsgType
import yaml

# Configure logging
logging.basicConfig(
    level=os.getenv('AGENT_LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPMessage:
    """MCP Protocol message handling"""
    
    @staticmethod
    def create_response(request_id: Union[str, int], result: Any = None, error: Any = None) -> Dict[str, Any]:
        """Create a JSON-RPC response message"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if error is not None:
            response["error"] = error
        else:
            response["result"] = result
            
        return response
    
    @staticmethod
    def create_notification(method: str, params: Any = None) -> Dict[str, Any]:
        """Create a JSON-RPC notification message"""
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params is not None:
            notification["params"] = params
            
        return notification
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """Validate JSON-RPC message format"""
        if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
            return False
        
        if "method" not in message and "id" not in message:
            return False
            
        return True


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


class MCPServer:
    """MCP Protocol compliant server"""
    
    def __init__(self):
        self.executor = CommandExecutor()
        self.server_info = {
            "name": "ai-sre-mcp-server",
            "version": "1.0.0"
        }
        
        # MCP Capabilities
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        
        # Initialize tools
        self._initialize_tools()
        self._initialize_resources()
        
    def _initialize_tools(self):
        """Initialize MCP tools"""
        self.capabilities["tools"] = {
            "listChanged": True
        }
        
        self.tools = {
            "kubectl_get": {
                "name": "kubectl_get",
                "description": "Execute kubectl get commands",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "resource": {
                            "type": "string",
                            "description": "Kubernetes resource type (pods, nodes, services, etc.)"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace (default: default)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Specific resource name (optional)"
                        },
                        "output": {
                            "type": "string",
                            "description": "Output format (json, yaml, wide, etc.)",
                            "default": "json"
                        }
                    },
                    "required": ["resource"]
                }
            },
            "kubectl_describe": {
                "name": "kubectl_describe",
                "description": "Execute kubectl describe commands",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "resource": {
                            "type": "string",
                            "description": "Kubernetes resource type"
                        },
                        "name": {
                            "type": "string",
                            "description": "Resource name"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace",
                            "default": "default"
                        }
                    },
                    "required": ["resource", "name"]
                }
            },
            "kubectl_logs": {
                "name": "kubectl_logs",
                "description": "Get pod logs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pod": {
                            "type": "string",
                            "description": "Pod name"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace",
                            "default": "default"
                        },
                        "container": {
                            "type": "string",
                            "description": "Container name (optional)"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of lines to retrieve",
                            "default": 100
                        }
                    },
                    "required": ["pod"]
                }
            },
            "flux_status": {
                "name": "flux_status",
                "description": "Get Flux GitOps status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Flux namespace",
                            "default": "flux-system"
                        },
                        "resource": {
                            "type": "string",
                            "description": "Flux resource type (sources, kustomizations, etc.)"
                        }
                    }
                }
            },
            "git_status": {
                "name": "git_status",
                "description": "Get git repository status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Git repository path",
                            "default": "/app/k8s-repo"
                        }
                    }
                }
            },
            "cli_tool": {
                "name": "cli_tool",
                "description": "Execute CLI tools (jq, grep, sed, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "description": "CLI tool name (jq, grep, sed, curl, etc.)"
                        },
                        "args": {
                            "type": "array",
                            "description": "Command line arguments",
                            "items": {"type": "string"}
                        },
                        "input": {
                            "type": "string",
                            "description": "Input data to process"
                        }
                    },
                    "required": ["tool"]
                }
            },
            "health_check": {
                "name": "health_check",
                "description": "Check system and service health",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service name to check (optional)"
                        }
                    }
                }
            },
            "git_pull": {
                "name": "git_pull",
                "description": "Pull latest changes from the Kubernetes Git repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to pull (default: current branch)"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force pull even if there are local changes",
                            "default": False
                        }
                    }
                }
            },
            "git_commit": {
                "name": "git_commit",
                "description": "Commit changes to the Kubernetes Git repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Commit message"
                        },
                        "files": {
                            "type": "array",
                            "description": "Specific files to commit (optional)",
                            "items": {"type": "string"}
                        },
                        "all": {
                            "type": "boolean",
                            "description": "Commit all changes",
                            "default": False
                        }
                    },
                    "required": ["message"]
                }
            },
            "git_push": {
                "name": "git_push",
                "description": "Push changes to the Kubernetes Git repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "branch": {
                            "type": "string",
                            "description": "Branch to push (default: current branch)"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force push",
                            "default": False
                        }
                    }
                }
            }
        }
    
    def _initialize_resources(self):
        """Initialize MCP resources"""
        self.capabilities["resources"] = {
            "listChanged": True,
            "subscribe": True
        }
        
        self.resources = {
            "config": {
                "uri": "config://main",
                "name": "Main Configuration",
                "description": "Main server configuration",
                "mimeType": "application/json"
            },
            "version": {
                "uri": "version://info",
                "name": "Version Information",
                "description": "Server version and tool information",
                "mimeType": "application/json"
            },
            "tools": {
                "uri": "tools://list",
                "name": "Available Tools",
                "description": "List of available CLI tools",
                "mimeType": "application/json"
            }
        }
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        client_info = params.get("clientInfo", {})
        logger.info(f"Initializing MCP connection with client: {client_info}")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": self.server_info
        }
    
    async def handle_tools_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": list(self.tools.values())
        }
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise ValueError(f"Tool execution failed: {str(e)}")
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool"""
        
        if tool_name == "kubectl_get":
            return await self._kubectl_get(arguments)
        elif tool_name == "kubectl_describe":
            return await self._kubectl_describe(arguments)
        elif tool_name == "kubectl_logs":
            return await self._kubectl_logs(arguments)
        elif tool_name == "flux_status":
            return await self._flux_status(arguments)
        elif tool_name == "git_status":
            return await self._git_status(arguments)
        elif tool_name == "cli_tool":
            return await self._cli_tool(arguments)
        elif tool_name == "health_check":
            return await self._health_check(arguments)
        elif tool_name == "git_pull":
            return await self._git_pull(arguments)
        elif tool_name == "git_commit":
            return await self._git_commit(arguments)
        elif tool_name == "git_push":
            return await self._git_push(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _kubectl_get(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute kubectl get command"""
        cmd = ['kubectl', 'get']
        
        resource = args.get('resource')
        namespace = args.get('namespace', 'default')
        name = args.get('name')
        output = args.get('output', 'json')
        
        cmd.extend(['-n', namespace])
        cmd.append(resource)
        
        if name:
            cmd.append(name)
        
        cmd.extend(['-o', output])
        
        result = await self.executor.execute(cmd)
        
        # Parse JSON output if requested
        if output == 'json' and result['success']:
            try:
                result['data'] = json.loads(result['stdout'])
            except json.JSONDecodeError:
                result['data'] = result['stdout']
        
        return result
    
    async def _kubectl_describe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute kubectl describe command"""
        cmd = ['kubectl', 'describe']
        
        resource = args.get('resource')
        name = args.get('name')
        namespace = args.get('namespace', 'default')
        
        cmd.extend(['-n', namespace])
        cmd.append(resource)
        cmd.append(name)
        
        return await self.executor.execute(cmd)
    
    async def _kubectl_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get pod logs"""
        cmd = ['kubectl', 'logs']
        
        pod = args.get('pod')
        namespace = args.get('namespace', 'default')
        container = args.get('container')
        lines = args.get('lines', 100)
        
        cmd.extend(['-n', namespace])
        cmd.extend(['--tail', str(lines)])
        
        if container:
            cmd.extend(['-c', container])
        
        cmd.append(pod)
        
        return await self.executor.execute(cmd)
    
    async def _flux_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get Flux status"""
        cmd = ['flux', 'get']
        
        namespace = args.get('namespace', 'flux-system')
        resource = args.get('resource', 'all')
        
        cmd.extend(['-n', namespace])
        cmd.append(resource)
        
        return await self.executor.execute(cmd)
    
    async def _git_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get git status"""
        path = args.get('path', '/app/k8s-repo')
        cmd = ['git', 'status', '--porcelain']
        
        return await self.executor.execute(cmd, cwd=path)
    
    async def _cli_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CLI tool"""
        tool = args.get('tool')
        tool_args = args.get('args', [])
        input_data = args.get('input')
        
        cmd = [tool] + tool_args
        
        if input_data:
            # Handle piped input
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=input_data.encode('utf-8'))
            
            return {
                'success': process.returncode == 0,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'exitcode': process.returncode
            }
        else:
            return await self.executor.execute(cmd)
    
    async def _health_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check system health"""
        service = args.get('service')
        
        if service:
            # Check specific service
            cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', f'http://{service}:8080/health']
            result = await self.executor.execute(cmd)
            
            return {
                'service': service,
                'status': 'healthy' if result['success'] and result['stdout'].strip() == '200' else 'unhealthy',
                'response_code': result['stdout'].strip()
            }
        else:
            # General health check
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'server': self.server_info
            }
    
    async def _git_pull(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Pull latest changes from Git repository"""
        repo_path = os.getenv('K8S_REPO_PATH', '/app/k8s-repo')
        branch = args.get('branch')
        force = args.get('force', False)
        
        if not os.path.exists(os.path.join(repo_path, '.git')):
            return {
                'success': False,
                'error': f'Git repository not found at {repo_path}. Make sure K8S_GIT_REPO is configured.'
            }
        
        try:
            # Get current branch if not specified
            if not branch:
                cmd = ['git', 'branch', '--show-current']
                result = await self.executor.execute(cmd, cwd=repo_path)
                if result['success']:
                    branch = result['stdout'].strip()
                else:
                    branch = 'main'
            
            # Fetch latest changes
            cmd = ['git', 'fetch', 'origin']
            result = await self.executor.execute(cmd, cwd=repo_path)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': f'Failed to fetch from origin: {result["stderr"]}'
                }
            
            # Pull changes
            if force:
                cmd = ['git', 'reset', '--hard', f'origin/{branch}']
                reset_result = await self.executor.execute(cmd, cwd=repo_path)
                if not reset_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to reset to origin/{branch}: {reset_result["stderr"]}'
                    }
            else:
                cmd = ['git', 'pull', 'origin', branch]
                result = await self.executor.execute(cmd, cwd=repo_path)
                
                if not result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to pull from origin/{branch}: {result["stderr"]}'
                    }
            
            # Get repository status
            status_cmd = ['git', 'status', '--porcelain']
            status_result = await self.executor.execute(status_cmd, cwd=repo_path)
            
            # Get latest commit
            log_cmd = ['git', 'log', '--oneline', '-1']
            log_result = await self.executor.execute(log_cmd, cwd=repo_path)
            
            return {
                'success': True,
                'branch': branch,
                'force': force,
                'status': status_result['stdout'].strip() if status_result['success'] else '',
                'latest_commit': log_result['stdout'].strip() if log_result['success'] else '',
                'message': f'Successfully pulled latest changes from origin/{branch}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Git pull failed: {str(e)}'
            }
    
    async def _git_commit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Commit changes to Git repository"""
        repo_path = os.getenv('K8S_REPO_PATH', '/app/k8s-repo')
        message = args.get('message')
        files = args.get('files', [])
        commit_all = args.get('all', False)
        
        if not os.path.exists(os.path.join(repo_path, '.git')):
            return {
                'success': False,
                'error': f'Git repository not found at {repo_path}. Make sure K8S_GIT_REPO is configured.'
            }
        
        try:
            # Check if there are changes to commit
            status_cmd = ['git', 'status', '--porcelain']
            status_result = await self.executor.execute(status_cmd, cwd=repo_path)
            
            if not status_result['success'] or not status_result['stdout'].strip():
                return {
                    'success': True,
                    'message': 'No changes to commit',
                    'status': status_result['stdout'].strip()
                }
            
            # Add files to staging
            if commit_all:
                cmd = ['git', 'add', '-A']
            elif files:
                cmd = ['git', 'add'] + files
            else:
                # Add all modified files
                cmd = ['git', 'add', '-u']
            
            add_result = await self.executor.execute(cmd, cwd=repo_path)
            if not add_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to stage files: {add_result["stderr"]}'
                }
            
            # Commit changes
            cmd = ['git', 'commit', '-m', message]
            commit_result = await self.executor.execute(cmd, cwd=repo_path)
            
            if not commit_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to commit: {commit_result["stderr"]}'
                }
            
            # Get commit hash
            hash_cmd = ['git', 'rev-parse', 'HEAD']
            hash_result = await self.executor.execute(hash_cmd, cwd=repo_path)
            
            return {
                'success': True,
                'message': f'Successfully committed: {message}',
                'commit_hash': hash_result['stdout'].strip() if hash_result['success'] else '',
                'files_committed': files if files else 'all modified files'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Git commit failed: {str(e)}'
            }
    
    async def _git_push(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Push changes to Git repository"""
        repo_path = os.getenv('K8S_REPO_PATH', '/app/k8s-repo')
        branch = args.get('branch')
        force = args.get('force', False)
        
        if not os.path.exists(os.path.join(repo_path, '.git')):
            return {
                'success': False,
                'error': f'Git repository not found at {repo_path}. Make sure K8S_GIT_REPO is configured.'
            }
        
        try:
            # Get current branch if not specified
            if not branch:
                cmd = ['git', 'branch', '--show-current']
                result = await self.executor.execute(cmd, cwd=repo_path)
                if result['success']:
                    branch = result['stdout'].strip()
                else:
                    branch = 'main'
            
            # Check if there are commits to push
            cmd = ['git', 'log', 'origin/{branch}..HEAD', '--oneline']
            result = await self.executor.execute(cmd, cwd=repo_path)
            
            if not result['stdout'].strip():
                return {
                    'success': True,
                    'message': f'No commits to push to origin/{branch}',
                    'branch': branch
                }
            
            # Push changes
            if force:
                cmd = ['git', 'push', 'origin', branch, '--force']
            else:
                cmd = ['git', 'push', 'origin', branch]
            
            result = await self.executor.execute(cmd, cwd=repo_path)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': f'Failed to push to origin/{branch}: {result["stderr"]}'
                }
            
            return {
                'success': True,
                'message': f'Successfully pushed to origin/{branch}',
                'branch': branch,
                'force': force,
                'commits_pushed': result['stdout'].strip()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Git push failed: {str(e)}'
            }
    
    async def handle_resources_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": list(self.resources.values())
        }
    
    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if uri not in [r["uri"] for r in self.resources.values()]:
            raise ValueError(f"Unknown resource: {uri}")
        
        if uri == "config://main":
            content = {
                "tools_enabled": list(self.tools.keys()),
                "server_info": self.server_info,
                "capabilities": self.capabilities
            }
        elif uri == "version://info":
            content = {
                "server": self.server_info,
                "tools_count": len(self.tools),
                "resources_count": len(self.resources),
                "timestamp": datetime.utcnow().isoformat()
            }
        elif uri == "tools://list":
            content = {
                "available_tools": list(self.tools.keys()),
                "tools": self.tools
            }
        else:
            content = {"error": "Unknown resource"}
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(content, indent=2)
                }
            ]
        }
    
    async def handle_notification(self, method: str, params: Dict[str, Any] = None):
        """Handle notification messages"""
        logger.info(f"Received notification: {method}")
        # Notifications don't require responses
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming MCP message"""
        if not MCPMessage.validate_message(message):
            return MCPMessage.create_response(
                message.get("id", 0),
                error={"code": -32600, "message": "Invalid Request"}
            )
        
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params", {})
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
                return MCPMessage.create_response(message_id, result)
            
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
                return MCPMessage.create_response(message_id, result)
            
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
                return MCPMessage.create_response(message_id, result)
            
            elif method == "resources/list":
                result = await self.handle_resources_list(params)
                return MCPMessage.create_response(message_id, result)
            
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
                return MCPMessage.create_response(message_id, result)
            
            elif method == "notifications/cancelled":
                await self.handle_notification(method, params)
                return None  # Notifications don't have responses
            
            else:
                return MCPMessage.create_response(
                    message_id,
                    error={"code": -32601, "message": f"Method not found: {method}"}
                )
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return MCPMessage.create_response(
                message_id,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )


class MCPWebSocketHandler:
    """WebSocket handler for MCP protocol"""
    
    def __init__(self, mcp_server: MCPServer):
        self.mcp_server = mcp_server
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for MCP protocol"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        logger.info("MCP WebSocket connection established")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        message = json.loads(msg.data)
                        logger.debug(f"Received MCP message: {message}")
                        
                        response = await self.mcp_server.process_message(message)
                        
                        if response:
                            await ws.send_str(json.dumps(response))
                            logger.debug(f"Sent MCP response: {response}")
                    
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON received: {e}")
                        error_response = MCPMessage.create_response(
                            0,
                            error={"code": -32700, "message": "Parse error"}
                        )
                        await ws.send_str(json.dumps(error_response))
                    
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")
                
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
        
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        
        finally:
            logger.info("MCP WebSocket connection closed")
        
        return ws


class MCPHTTPServer:
    """HTTP Server with MCP protocol support"""
    
    def __init__(self):
        self.mcp_server = MCPServer()
        self.ws_handler = MCPWebSocketHandler(self.mcp_server)
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup HTTP routes"""
        # MCP WebSocket endpoint
        self.app.router.add_get('/mcp', self.ws_handler.websocket_handler)
        
        # Health check endpoint
        self.app.router.add_get('/health', self.handle_health)
        
        # MCP over HTTP endpoint (for testing)
        self.app.router.add_post('/mcp/http', self.handle_http_mcp)
    
    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'protocol': 'MCP',
            'server_info': self.mcp_server.server_info,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def handle_http_mcp(self, request):
        """Handle MCP over HTTP (for testing purposes)"""
        try:
            data = await request.json()
            response = await self.mcp_server.process_message(data)
            
            if response:
                return web.json_response(response)
            else:
                return web.json_response({'status': 'notification_processed'})
        
        except Exception as e:
            logger.error(f"HTTP MCP error: {e}")
            return web.json_response({
                'error': str(e)
            }, status=500)
    
    def run(self):
        """Run the MCP server"""
        port = int(os.getenv('MCP_SERVER_PORT', '8080'))
        logger.info(f"Starting MCP Server on port {port}")
        logger.info(f"MCP WebSocket endpoint: ws://localhost:{port}/mcp")
        logger.info(f"MCP HTTP endpoint: http://localhost:{port}/mcp/http")
        logger.info(f"Health check: http://localhost:{port}/health")
        
        web.run_app(self.app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    server = MCPHTTPServer()
    server.run()
