# AI SRE - Quick Start Guide

## Overview

AI SRE is a lean, containerized CLI toolbox designed for Kubernetes cluster remediation. It acts as an execution environment controlled by N8N workflows, providing all necessary CLI tools for GitOps operations.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Telegram  │────▶│     N8N      │────▶│   AI SRE       │
│   Alerts    │     │  Orchestrator│     │   Container    │
└─────────────┘     └──────────────┘     └────────────────┘
                           │                      │
                           │                      ├── MCP Server
                    ┌──────▼──────┐              ├── kubectl
                    │  RAG/Vector │              ├── git/gh
                    │    Store    │              ├── flux
                    └─────────────┘              └── helm
```

### Key Components:

1. **N8N (External)**: Handles all orchestration, alert processing, RAG/vector store, and Telegram integration
2. **AI SRE Container**: Provides CLI tools and MCP Server for command execution
3. **MCP Server**: REST API interface for N8N to execute commands and get structured responses

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-sre

# Initialize the project
make init

# Edit the .env file with your configuration
nano .env
```

### 2. Configure Environment

Required environment variables in `.env`:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your-org/k8s-configs

# Kubernetes Configuration
KUBECONFIG=/app/.kube/config
KUBE_CONTEXT=your-context

# Flux Configuration
FLUX_NAMESPACE=flux-system
```

### 3. Build and Run

```bash
# Build the container
make build

# Start the container
make run

# Check status
make status

# View logs
make logs
```

### 4. Test MCP Server

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test kubectl command
curl -X POST http://localhost:8080/kubectl/get \
  -H "Content-Type: application/json" \
  -d '{"resource": "pods", "namespace": "default", "output": "json"}'

# Test git operation
curl -X POST http://localhost:8080/git/status \
  -H "Content-Type: application/json" \
  -d '{}'
```

## MCP Server API

### Kubectl Operations

```http
POST /kubectl/{action}
```

Actions: `get`, `apply`, `delete`, `scale`, `rollout`, `logs`, `exec`

Example:
```json
{
  "resource": "deployment",
  "name": "my-app",
  "namespace": "default",
  "flags": {
    "replicas": 3
  }
}
```

### Git Operations

```http
POST /git/{action}
```

Actions: `clone`, `pull`, `push`, `commit`, `checkout`, `status`

Example:
```json
{
  "message": "Fix configuration",
  "all": true
}
```

### Flux Operations

```http
POST /flux/{action}
```

Actions: `reconcile`, `suspend`, `resume`, `get`

Example:
```json
{
  "resource": "kustomization",
  "name": "my-app",
  "namespace": "flux-system"
}
```

## N8N Integration

### Webhook Configuration

Configure N8N to send HTTP requests to the MCP Server:

1. **URL**: `http://ai-sre:8080/{endpoint}`
2. **Method**: `POST` for commands, `GET` for queries
3. **Headers**: `Content-Type: application/json`
4. **Authentication**: Set `MCP_API_KEY` if needed

### Example N8N Workflow

1. **Telegram Trigger**: Receives alert
2. **Parse Alert**: Extract details
3. **Query RAG**: Check knowledge base
4. **Execute Diagnosis**: Call MCP Server for kubectl logs/describe
5. **Formulate Fix**: Based on diagnosis
6. **Request Approval**: Send to Telegram
7. **Execute Fix**: Call MCP Server for remediation
8. **Verify**: Check if issue resolved
9. **Update RAG**: Store resolution

## Development

### Project Structure

```
ai-sre/
├── Dockerfile           # Container definition
├── docker-compose.yaml  # Local development setup
├── .env.template       # Environment template
├── Makefile           # Build and run commands
├── src/
│   └── mcp_server.py  # MCP Server implementation
├── scripts/
│   └── entrypoint.sh  # Container entrypoint
├── k8s-repo/         # Local Git repository
├── logs/             # Application logs
└── work/             # Working directory
```

### Adding New Commands

To add new command support to MCP Server:

1. Edit `src/mcp_server.py`
2. Add new handler class (e.g., `HelmHandler`)
3. Add routes in `setup_routes()`
4. Implement execute method

Example:
```python
class HelmHandler:
    async def execute(self, action: str, params: Dict[str, Any]):
        # Build helm command
        cmd = ['helm', action]
        # Add parameters
        # Execute and return result
```

### Testing

```bash
# Run unit tests
make test

# Test specific endpoint
make test-kubectl

# Open shell in container
make shell
```

## Security Considerations

1. **Secrets**: Never commit `.env` file
2. **RBAC**: Use least privilege for kubeconfig
3. **Network**: Restrict container network access
4. **Audit**: All commands are logged with timestamps

## Troubleshooting

### Container won't start
- Check `.env` configuration
- Verify kubeconfig is valid
- Check Docker logs: `docker logs ai-sre`

### MCP Server not responding
- Check port 8080 is not in use
- Verify Python dependencies installed
- Check logs: `make logs`

### Kubectl commands failing
- Verify kubeconfig is mounted correctly
- Check cluster connectivity
- Test with: `docker exec ai-sre kubectl get nodes`

## Next Steps

1. **Setup N8N**: Install and configure N8N workflows
2. **Configure Alerts**: Setup Prometheus/Alertmanager to send to Telegram
3. **Create Runbooks**: Document common fixes in N8N's RAG store
4. **Test Scenarios**: Run through common failure scenarios
5. **Monitor**: Setup dashboards to track remediation success

## Support

For issues or questions:
- Check logs: `make logs`
- Debug mode: Set `AGENT_LOG_LEVEL=DEBUG` in `.env`
- Shell access: `make shell`
