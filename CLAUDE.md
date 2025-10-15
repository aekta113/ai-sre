# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI SRE is a lightweight, containerized MCP (Model Context Protocol) server designed for Kubernetes operations and GitOps workflows. It provides a stateless execution environment that exposes Kubernetes, Git, Flux, and CLI tools through the standardized MCP protocol for integration with N8N workflows and AI agents.

**Key Architecture Principle**: The container is stateless and lean (< 256MB RAM, < 500MB image). Intelligence and orchestration are handled externally by N8N. This container is purely an execution environment.

## Common Development Commands

### Build and Run
```bash
# Initialize project (creates .env, directories)
make init

# Build Docker image
make build

# Start container with docker-compose
make run

# Stop container
make stop

# View logs
make logs

# Open shell in running container
make shell
```

### Testing
```bash
# Test MCP Protocol server
make test-mcp

# Test kubectl tools via MCP
make test-kubectl

# Test git tools via MCP
make test-git-tools

# Test Flux tools via MCP
make test-flux

# Run Python test script
python test_mcp.py
```

### Local Development
```bash
# Run MCP server locally (without Docker)
python src/mcp_server_protocol.py

# Requirements: aiohttp, pyyaml
pip install aiohttp pyyaml
```

### Kubernetes Deployment
```bash
# Deploy to cluster
kubectl apply -f k8s-repo/storage.yaml
kubectl apply -f k8s-repo/configmap.yaml
kubectl apply -f k8s-repo/deployment.yaml

# Check status
kubectl get pods -n ai-sre
kubectl logs -f deployment/ai-sre -n ai-sre

# Port forward for testing
kubectl port-forward svc/ai-sre 8080:8080 -n ai-sre
```

## Architecture and Code Organization

### Core Components

1. **MCP Protocol Server** (`src/mcp_server_protocol.py`)
   - Single-file Python server implementing MCP protocol (JSON-RPC 2.0)
   - Uses aiohttp for WebSocket and HTTP endpoints
   - Exposes tools for kubectl, git, flux, and CLI operations
   - Handles both WebSocket (ws://host:8080/mcp) and HTTP (POST /mcp/http)

2. **Container Runtime** (`Dockerfile`)
   - Multi-stage Alpine-based build for security and size optimization
   - Builder stage: Installs kubectl, helm, flux, gh CLI
   - Runtime stage: Minimal Alpine with only essential tools and binaries
   - Runs as non-root user (aisre:aisre, uid/gid 1000)

3. **Entrypoint** (`scripts/entrypoint.sh`)
   - Configures Git authentication (SSH keys or GitHub token)
   - Auto-clones/updates Kubernetes GitOps repository on startup
   - Sets up kubeconfig and validates cluster access
   - Runs MCP server as main process

### Tool Categories and MCP Protocol

**MCP Tools** are defined in `_initialize_tools()` method in `src/mcp_server_protocol.py`:

- **Kubernetes**: `kubectl_get`, `kubectl_describe`, `kubectl_logs`
- **Git**: `git_status`, `git_pull`, `git_commit`, `git_push`
- **GitOps**: `flux_status`
- **CLI**: `cli_tool` (generic executor for jq, grep, sed, curl, etc.)
- **File Operations**: `file_read`, `file_write`, `file_list`, `file_delete`, `file_exists`, `file_info`
- **Health**: `health_check`

Each tool has:
- JSON schema definition (`inputSchema`)
- Async execution method (e.g., `_kubectl_get()`)
- Structured result format with success/failure status

### MCP Call Logging

All MCP calls are automatically logged to daily JSON log files with 5-day retention:

**Log Location**: `/app/logs/mcp-calls/`
**Log Format**: `mcp-calls-YYYY-MM-DD.jsonl` (JSON Lines format)
**Retention**: 5 days (configurable via `MCP_LOG_RETENTION_DAYS`)

**Log Entry Structure**:
```json
{
  "timestamp": "2025-10-15T10:30:00.123Z",
  "method": "tools/call",
  "params": {"name": "kubectl_get", "arguments": {...}},
  "success": true,
  "result": {...},
  "duration": 0.234
}
```

**Endpoints**:
- `GET /logs/mcp/stats` - Get log statistics (file count, size, retention)
- `POST /logs/mcp/cleanup` - Manually trigger log cleanup

**Automatic Cleanup**: Runs daily in background task, removing logs older than retention period.

### File Operations

The server provides secure file operations for allowed directories only:
- `/app/k8s-repo` - Kubernetes GitOps repository
- `/app/runbooks` - Runbook storage
- `/app/work` - Working directory
- `/app/logs` - Log files (read-only recommended)

**Available Operations**:

1. **file_read** - Read file contents
   ```json
   {"path": "/app/runbooks/static/agent.md", "encoding": "utf-8"}
   ```

2. **file_write** - Write content to file
   ```json
   {"path": "/app/k8s-repo/deployment.yaml", "content": "...", "create_dirs": true}
   ```

3. **file_list** - List directory contents
   ```json
   {"path": "/app/runbooks", "pattern": "*.md", "recursive": true}
   ```

4. **file_delete** - Delete file (requires confirmation)
   ```json
   {"path": "/app/work/temp.txt", "confirm": true}
   ```

5. **file_exists** - Check if path exists
   ```json
   {"path": "/app/k8s-repo/deployment.yaml"}
   ```

6. **file_info** - Get file metadata (size, modified time, permissions)
   ```json
   {"path": "/app/runbooks/static/agent.md"}
   ```

**Security**: All file operations validate paths using `_is_path_allowed()` method. Attempts to access files outside allowed directories are rejected.

### Adding New MCP Tools

To add a new tool to the MCP server:

1. **Define tool schema** in `_initialize_tools()`:
```python
"my_tool": {
    "name": "my_tool",
    "description": "Description of what the tool does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"},
            "param2": {"type": "integer", "default": 100}
        },
        "required": ["param1"]
    }
}
```

2. **Route to handler** in `_execute_tool()`:
```python
elif tool_name == "my_tool":
    return await self._my_tool(arguments)
```

3. **Implement handler method**:
```python
async def _my_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
    param1 = args.get('param1')
    param2 = args.get('param2', 100)

    cmd = ['command', '--flag', param1]
    result = await self.executor.execute(cmd)

    return result  # Must include: success, stdout, stderr, exitcode
```

### Git Repository Management

The container automatically manages a Kubernetes GitOps repository:

**Environment Variables** (set in `.env`):
- `K8S_GIT_REPO`: Git repository URL (SSH or HTTPS)
- `K8S_GIT_BRANCH`: Branch to checkout (default: main)
- `K8S_REPO_PATH`: Local path (default: /app/k8s-repo)
- `GITHUB_TOKEN`: For HTTPS authentication
- `GITHUB_USER`: Git commit author name
- `GITHUB_EMAIL`: Git commit author email

**Authentication Methods**:
- SSH: Mount `~/.ssh` volume in docker-compose.yaml
- HTTPS: Set `GITHUB_TOKEN` environment variable

**Git Operations** available via MCP tools:
- `git_status`: Check repository status
- `git_pull`: Pull latest changes (with force option)
- `git_commit`: Commit changes (with file selection)
- `git_push`: Push to remote (with force option)

### Runbook System

The runbook system provides static and dynamic incident response documentation:

**Storage Structure** (persistent volume in k8s):
```
/app/runbooks/
├── static/              # Static runbooks and templates
│   ├── agent.md        # Main AI knowledge base
│   ├── templates/      # Incident/remediation templates
│   └── best-practices/ # Monitoring and operational guidelines
├── dynamic/            # AI-generated runbooks
│   ├── incidents/      # Real incident documentation
│   ├── patterns/       # Learned patterns
│   └── resolutions/    # Successful resolution strategies
└── cache/              # Search indexes and metrics
```

**Purpose**: Store operational knowledge, incident patterns, and successful resolutions for AI learning and future reference.

## Configuration and Environment

### Critical Environment Variables

**Server Configuration**:
- `MCP_SERVER_PORT`: Port for MCP server (default: 8080)
- `AGENT_LOG_LEVEL`: Logging level (default: INFO)
- `COMMAND_TIMEOUT`: Command execution timeout in seconds (default: 60)
- `DRY_RUN`: Enable dry-run mode (default: false)

**MCP Call Logging**:
- `MCP_LOG_DIR`: Directory for MCP call logs (default: /app/logs/mcp-calls)
- `MCP_LOG_RETENTION_DAYS`: Number of days to retain logs (default: 5)

**Kubernetes**:
- `KUBECONFIG`: Path to kubeconfig file
- `KUBE_CONTEXT`: Kubernetes context to use

**Git/GitOps**:
- `K8S_GIT_REPO`: GitOps repository URL
- `K8S_GIT_BRANCH`: Branch to use
- `GITHUB_TOKEN`: GitHub authentication token

**Flux**:
- `FLUX_NAMESPACE`: Flux system namespace (default: flux-system)

### Configuration File

`config/config.yaml` controls tool availability, security, and behavior:
- **tools.enabled_categories**: Enable tool categories (all, text, network, kubernetes, etc.)
- **tools.disabled_tools**: Blacklist specific tools
- **security.blocked_commands**: Commands that cannot be executed (rm, dd, shutdown, etc.)
- **performance.command_timeout**: Override default timeout

## Testing the MCP Server

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8080/health

# Initialize MCP connection
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test", "version": "1.0.0"}}}'

# List available tools
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'

# Call a tool
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "kubectl_get", "arguments": {"resource": "pods", "namespace": "default"}}}'
```

### Python Test Script

Use `test_mcp.py` for comprehensive testing:
```bash
python test_mcp.py
```

### Testing File Operations

```bash
# Read a file
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "file_read", "arguments": {"path": "/app/runbooks/static/agent.md"}}}'

# Write a file
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "file_write", "arguments": {"path": "/app/work/test.txt", "content": "Hello World"}}}'

# List files
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "file_list", "arguments": {"path": "/app/runbooks", "pattern": "*.md", "recursive": true}}}'

# Get file info
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "file_info", "arguments": {"path": "/app/k8s-repo/deployment.yaml"}}}'
```

### Testing MCP Call Logging

```bash
# Get log statistics
curl http://localhost:8080/logs/mcp/stats

# Manually trigger log cleanup
curl -X POST http://localhost:8080/logs/mcp/cleanup

# View log files directly
ls -lh /app/logs/mcp-calls/

# Read a specific day's logs
cat /app/logs/mcp-calls/mcp-calls-2025-10-15.jsonl | jq .
```

## N8N Integration

The MCP server is designed for use with N8N's MCP Client node:

**Connection Configuration**:
- Type: WebSocket
- URL: `ws://ai-sre.ai.svc.cluster.local:8080/mcp` (or `ws://localhost:8080/mcp` for local)
- Authentication: None (or set `MCP_API_KEY` if required)

**Workflow Pattern**:
1. N8N receives alert (Telegram, Prometheus, etc.)
2. N8N queries RAG/vector store for similar incidents
3. N8N calls MCP tools for diagnostics (kubectl_logs, kubectl_describe)
4. N8N formulates remediation plan
5. N8N requests human approval (Telegram)
6. N8N executes fix via MCP tools
7. N8N verifies resolution and updates knowledge base

## Container Specifications and Constraints

**Resource Limits**:
- Memory: < 256MB (enforced in k8s-repo/deployment.yaml)
- CPU: < 0.2 cores
- Image Size: < 500MB
- Startup Time: < 10 seconds

**Security Constraints**:
- Runs as non-root user (uid 1000)
- Multi-stage build for minimal attack surface
- Blocked commands: rm, dd, mkfs, fdisk, shutdown, reboot
- No interactive commands supported (no `git rebase -i`, `git add -i`)

## Important Development Notes

### MCP Protocol Version
The server implements MCP protocol version **2024-11-05**. When updating protocol version, ensure:
- `handle_initialize()` returns correct protocol version
- Client compatibility is maintained
- Tool schemas follow MCP specification

### Command Execution
All commands are executed through `CommandExecutor` class:
- Async subprocess execution via `asyncio.create_subprocess_exec()`
- Timeout handling (default 60s)
- Environment variable merging
- Working directory support
- Structured output: `{success, stdout, stderr, exitcode, duration}`

### Logging
- Uses Python `logging` module
- Log level controlled by `AGENT_LOG_LEVEL` environment variable
- All MCP messages logged at DEBUG level
- Command executions logged at INFO level

### Error Handling
MCP errors follow JSON-RPC 2.0 error codes:
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32603`: Internal error
- `-32700`: Parse error

## Storage and Persistence

### Persistent Volumes (Kubernetes)
The deployment uses PersistentVolumeClaims:
- `runbooks-storage`: 5Gi for runbook system
- `logs-storage`: 20Gi for application logs
- `cache-storage`: 2Gi for cached data
- `main-storage`: 10Gi for general data

### Volume Mounts (Docker Compose)
Local development volumes:
- `./.kube:/app/.kube:ro` - Kubeconfig
- `./k8s-repo:/app/k8s-repo` - Git repository
- `./logs:/app/logs` - Logs
- `./work:/app/work` - Working directory
- `./runbooks:/app/runbooks` - Runbook storage

## Troubleshooting Common Issues

### Container Fails to Start
- Check `.env` file exists and is properly configured
- Verify Git repository URL is accessible (SSH keys or token)
- Check kubeconfig is mounted and valid

### MCP Server Not Responding
- Verify port 8080 is available
- Check Python dependencies (aiohttp, pyyaml) are installed
- Review logs with `make logs` or `kubectl logs`
- Test health endpoint: `curl http://localhost:8080/health`

### Git Operations Failing
- Verify Git authentication is configured (SSH keys or GITHUB_TOKEN)
- Check Git repository URL format (git@github.com: vs https://github.com/)
- Ensure repository exists and user has access
- Check entrypoint logs for Git clone/pull errors

### kubectl Commands Failing
- Verify kubeconfig is mounted correctly
- Check cluster connectivity from container
- Test with: `docker exec ai-sre kubectl cluster-info`
- Verify RBAC permissions in cluster

## Security Considerations

- Never commit `.env` file or secrets to Git
- Use SSH keys or GitHub tokens for Git authentication
- Apply least-privilege RBAC for Kubernetes access
- Review `config/config.yaml` for blocked commands
- All command executions are logged with timestamps
- Container runs as non-root user for security
- Use SOPS with AGE encryption for secrets management (future feature)
