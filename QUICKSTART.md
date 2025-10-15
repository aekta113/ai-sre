# AI SRE - Quick Start Guide

## Overview

AI SRE is a comprehensive, containerized CLI toolbox designed for Kubernetes cluster remediation with AI-powered operations. It provides a **Model Context Protocol (MCP) compliant server** that exposes Kubernetes, Git, Flux, and diagnostic CLI operations through standardized MCP tools, designed to be seamlessly integrated with N8N's MCP Client node.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Telegram  │────▶│     N8N      │────▶│   AI SRE       │
│   Alerts    │     │  Orchestrator│     │   Container    │
└─────────────┘     └──────────────┘     └────────────────┘
                           │                      │
                           │                      ├── MCP Protocol Server
                    ┌──────▼──────┐              ├── kubectl + CLI tools
                    │  RAG/Vector │              ├── git/gh
                    │    Store    │              ├── flux
                    └─────────────┘              ├── sops + secrets
                                                 ├── monitoring APIs
                                                 └── AI learning
```

### Key Components:

1. **N8N (External)**: Handles all orchestration, alert processing, RAG/vector store, and Telegram integration
2. **AI SRE Container**: Provides CLI tools, MCP Protocol Server, secrets management, and AI learning capabilities
3. **MCP Protocol Server**: JSON-RPC over WebSocket/HTTP interface for N8N MCP Client to execute commands and get structured responses
4. **CLI Tools**: Comprehensive set of diagnostic tools (sed, curl, cat, tree, find, grep, etc.)
5. **Secrets Management**: SOPS with AGE encryption for secure secret handling
6. **Configuration Management**: Flexible tool activation/deactivation via ConfigMaps

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

### 2. MCP Protocol Integration

The AI SRE server now implements the **Model Context Protocol (MCP)** for seamless integration with N8N's MCP Client node.

#### N8N MCP Client Configuration

```json
{
  "connectionType": "WebSocket",
  "serverUrl": "ws://ai-sre.ai.svc.cluster.local:8080/mcp",
  "authentication": {
    "type": "none"
  }
}
```

#### Available MCP Tools

- **`kubectl_get`** - Get Kubernetes resources
- **`kubectl_describe`** - Describe Kubernetes resources
- **`kubectl_logs`** - Get pod logs
- **`flux_status`** - Get Flux GitOps status
- **`git_status`** - Get git repository status
- **`cli_tool`** - Execute CLI tools (jq, grep, sed, etc.)
- **`health_check`** - Check system health

#### Testing MCP Connection

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test MCP initialization
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {"tools": {}},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }'

# List available tools
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

### 3. Configure Environment

#### Environment Variables (.env)

Create a `.env` file from the template:

```bash
cp .env.template .env
nano .env
```

**Required Configuration:**

```bash
# =============================================================================
# SERVER CONFIGURATION
# =============================================================================
MCP_SERVER_PORT=8080
AGENT_LOG_LEVEL=INFO
AGENT_WORKDIR=/app/work
COMMAND_TIMEOUT=60
DRY_RUN=false

# =============================================================================
# KUBERNETES CONFIGURATION
# =============================================================================
KUBE_CONTEXT=
KUBE_NAMESPACE=default
KUBECONFIG_PATH=/root/.kube/config

# =============================================================================
# FLUX CONFIGURATION
# =============================================================================
FLUX_NAMESPACE=flux-system
GITHUB_REPO=https://github.com/your-org/your-repo.git
LOCAL_REPO_PATH=/app/k8s-repo

# =============================================================================
# SECRETS MANAGEMENT
# =============================================================================
SOPS_ENABLED=true
SOPS_AGE_KEY=age1...  # Your AGE private key
AGE_KEY_PATH=/app/secrets/age-key.txt

# =============================================================================
# SERVICE ENDPOINTS
# =============================================================================
PROMETHEUS_URL=http://prometheus:9090
ALERTMANAGER_URL=http://alertmanager:9093
GRAFANA_URL=http://grafana:3000
KUMA_URL=http://kuma:5681
# ... (see .env.template for complete list)
```

#### Secrets Configuration

**Generate AGE Key for SOPS:**

```bash
# Generate AGE key pair
age-keygen -o age-key.txt

# The output will show:
# Public key: age1...
# Private key: AGE-SECRET-KEY-1...

# Add the private key to your .env file
echo "SOPS_AGE_KEY=AGE-SECRET-KEY-1..." >> .env
```

**Configure GitHub Token:**

```bash
# Create GitHub Personal Access Token with repo access
# Add to .env:
GITHUB_TOKEN=ghp_your_token_here
```

**Configure Kubernetes Access:**

```bash
# Copy your kubeconfig
cp ~/.kube/config ./kubeconfig

# Or set context if using existing kubeconfig
KUBE_CONTEXT=your-cluster-context
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

# Test CLI tools
curl -X POST http://localhost:8080/cli/grep \
  -H "Content-Type: application/json" \
  -d '{"args": ["-r", "error", "/var/log"], "flags": {"i": true}}'

# Test SOPS encryption
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "encrypt",
    "data": "apiVersion: v1\nkind: Secret\nmetadata:\n  name: my-secret\nstringData:\n  password: secret123"
  }'

# Test configuration
curl http://localhost:8080/config
curl http://localhost:8080/cli/tools
```

### 5. Kubernetes Deployment

#### Prerequisites

```bash
# Create namespace
kubectl create namespace ai-sre

# Apply storage configuration
kubectl apply -f k8s-repo/storage.yaml

# Apply configuration and secrets
kubectl apply -f k8s-repo/configmap.yaml
```

#### Deploy AI SRE

```bash
# Deploy the complete application
kubectl apply -f k8s-repo/deployment.yaml

# Check deployment status
kubectl get pods -n ai-sre
kubectl get pvc -n ai-sre
kubectl get svc -n ai-sre

# Check runbook storage
kubectl exec -it deployment/ai-sre -n ai-sre -- ls -la /app/runbooks/

# Port forward for testing
kubectl port-forward svc/ai-sre 8080:8080 -n ai-sre
```

#### Storage Configuration

The deployment includes persistent storage for:

- **Runbooks Storage** (5Gi): Static and dynamic runbooks
- **Logs Storage** (20Gi): Application and execution logs  
- **Cache Storage** (2Gi): Cached data and search indexes
- **Main Storage** (10Gi): General application data

```bash
# Check storage usage
kubectl exec -it deployment/ai-sre -n ai-sre -- df -h

# View storage configuration
kubectl describe pvc -n ai-sre
```

## Configuration Management

### Tool Configuration

The AI SRE agent supports flexible tool activation/deactivation through configuration:

**Available Tool Categories:**
- `text`: sed, grep, awk, sort, uniq, wc, head, tail, tr, cut, paste, diff
- `network`: curl, netstat, ss, tcpdump, ping, nslookup, dig
- `filesystem`: tree, find, cat, less, more
- `system`: ps, top, df, du, free, lsof
- `archive`: tar, gzip
- `json`: jq
- `yaml`: yq
- `encoding`: base64
- `security`: sops, age
- `kubernetes`: kustomize, helm, k9s, kubectx, kubens

**Configuration Methods:**

1. **Environment Variables:**
```bash
# Enable specific categories
TOOLS_ENABLED_CATEGORIES=text,network,security

# Disable specific tools
TOOLS_DISABLED=tcpdump,lsof

# Enable specific tools (overrides categories)
TOOLS_ENABLED=sops,age,curl
```

2. **ConfigMap (Kubernetes):**
```bash
# Apply configuration
kubectl apply -f k8s-repo/configmap.yaml

# Update configuration
kubectl edit configmap ai-sre-config -n ai-sre
```

3. **Configuration File:**
```bash
# Edit config file
nano config/config.yaml

# Reload configuration
curl -X POST http://localhost:8080/config/reload
```

### Secrets Management

#### SOPS with AGE Encryption

**Encrypt Secrets:**
```bash
# Create a secret file
cat > secret.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
stringData:
  password: secret123
  token: abc123
EOF

# Encrypt with SOPS
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "encrypt",
    "file": "secret.yaml"
  }'
```

**Decrypt Secrets:**
```bash
# Decrypt secret
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "decrypt",
    "file": "secret.enc.yaml"
  }'
```

**Inline Encryption/Decryption:**
```bash
# Encrypt inline data
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "encrypt",
    "data": "password: secret123"
  }'

# Decrypt inline data
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "decrypt",
    "data": "ENC[AES256_GCM,data:...]"
  }'
```

#### Kubernetes Secrets

**Create Secret with SOPS:**
```bash
# Apply encrypted secret to cluster
curl -X POST http://localhost:8080/kubectl/apply \
  -H "Content-Type: application/json" \
  -d '{
    "file": "secret.enc.yaml",
    "namespace": "default"
  }'
```

**Update Secret:**
```bash
# Edit secret
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "edit",
    "file": "secret.enc.yaml"
  }'
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

### CLI Tools Operations

```http
POST /cli/{tool}
```

**Available Tools:**
- `sed`, `curl`, `cat`, `tree`, `find`, `grep`, `awk`, `sort`, `uniq`, `wc`
- `head`, `tail`, `less`, `more`, `jq`, `yq`, `base64`, `tr`, `cut`, `paste`
- `diff`, `tar`, `gzip`, `ps`, `top`, `df`, `du`, `free`, `netstat`, `ss`
- `lsof`, `tcpdump`, `ping`, `nslookup`, `dig`, `sops`, `age`
- `kustomize`, `helm`, `k9s`, `kubectx`, `kubens`

**Examples:**

```bash
# Grep with flags
curl -X POST http://localhost:8080/cli/grep \
  -H "Content-Type: application/json" \
  -d '{
    "args": ["-r", "error", "/var/log"],
    "flags": {"i": true, "n": true}
  }'

# Find files
curl -X POST http://localhost:8080/cli/find \
  -H "Content-Type: application/json" \
  -d '{
    "args": ["/app", "-name", "*.yaml", "-type", "f"]
  }'

# Process list
curl -X POST http://localhost:8080/cli/ps \
  -H "Content-Type: application/json" \
  -d '{
    "flags": {"aux": true}
  }'

# JSON processing
curl -X POST http://localhost:8080/cli/jq \
  -H "Content-Type: application/json" \
  -d '{
    "args": [".items[].metadata.name"],
    "input": "{\"items\":[{\"metadata\":{\"name\":\"pod1\"}}]}"
  }'

# Chained commands (pipe-like)
curl -X POST http://localhost:8080/cli/chain \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"tool": "cat", "args": ["/var/log/syslog"]},
      {"tool": "grep", "args": ["error"]},
      {"tool": "wc", "args": ["-l"]}
    ]
  }'
```

### SOPS Operations

```http
POST /cli/sops
```

**Operations:**
- `encrypt`: Encrypt files or data
- `decrypt`: Decrypt files or data
- `edit`: Edit encrypted files
- `keys`: Show encryption keys
- `version`: Show SOPS version

**Examples:**

```bash
# Encrypt file
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "encrypt",
    "file": "secret.yaml"
  }'

# Decrypt inline data
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "decrypt",
    "data": "ENC[AES256_GCM,data:...]"
  }'

# Edit encrypted file
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "edit",
    "file": "secret.enc.yaml"
  }'
```

### Configuration Operations

```http
GET /config              # Get current configuration
POST /config/reload      # Reload configuration
GET /config/tools        # Get tool configuration
GET /cli/tools          # List available tools
```

### Service Monitoring

```http
GET /services                    # List all services
GET /services/{service}         # Check service health
GET /prometheus/query           # Query Prometheus
GET /alertmanager/alerts        # Get alerts
GET /grafana/dashboards         # Get dashboards
GET /kuma/mesh                 # Get mesh status
GET /jaeger/traces             # Query traces
GET /loki/query                # Query logs
```

### System Operations

```http
GET /health          # Health check
GET /ready          # Readiness check
GET /version        # Version information
GET /env           # Environment variables
```

## Runbook System

### Overview

The AI SRE runbook system provides intelligent incident response with both static and dynamic runbooks:

- **Static Runbooks**: Core knowledge base (`agent.md`) with standard procedures
- **Dynamic Runbooks**: AI-generated runbooks based on actual incidents
- **Pattern Recognition**: Learns from successful resolutions
- **Persistent Storage**: All runbooks stored in persistent volumes

### Storage Structure

```
/app/runbooks/
├── static/                    # Static runbooks (agent.md, templates)
│   ├── agent.md              # Main knowledge base
│   ├── templates/            # Runbook templates
│   └── best-practices/       # Best practices documentation
├── dynamic/                   # AI-generated runbooks
│   ├── incidents/            # Incident-specific runbooks
│   ├── patterns/             # Learned patterns
│   └── resolutions/          # Successful resolutions
├── cache/                    # Cached runbook data
└── backups/                  # Backup storage
```

### Runbook Operations

```bash
# Search runbooks
curl "http://localhost:8080/runbooks/search?q=pod%20crash&type=static&severity=high"

# Execute runbook with context
curl -X POST http://localhost:8080/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "runbook_id": "pod-crash-001",
    "context": {
      "namespace": "production",
      "pod_name": "my-app-7d4b8c9f-x2k9m"
    },
    "parameters": {
      "auto_execute": false,
      "dry_run": true
    }
  }'

# Learn from incident data
curl -X POST http://localhost:8080/runbooks/learn \
  -H "Content-Type: application/json" \
  -d '{
    "incident_data": {
      "type": "pod_crash",
      "diagnosis": ["memory_limit_exceeded"],
      "resolution": ["increase_memory_limit"],
      "success": true,
      "duration": "5m"
    }
  }'

# Get learned patterns
curl http://localhost:8080/runbooks/patterns

# Check runbook system health
curl http://localhost:8080/runbooks/health
```

### Storage Management

```bash
# Check storage usage
curl http://localhost:8080/storage/usage

# Trigger backup
curl http://localhost:8080/storage/backup

# Clean up old files
curl -X POST http://localhost:8080/storage/cleanup \
  -H "Content-Type: application/json" \
  -d '{"retention_days": 30}'
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
│   └── mcp_server_protocol.py  # MCP Protocol Server implementation
├── scripts/
│   └── entrypoint.sh  # Container entrypoint
├── k8s-repo/         # Local Git repository
├── logs/             # Application logs
└── work/             # Working directory
```

### Adding New MCP Tools

To add new tool support to the MCP Protocol Server:

1. Edit `src/mcp_server_protocol.py`
2. Add new tool definition in `_initialize_tools()`
3. Add tool execution method in `_execute_tool()`
4. Implement the specific tool handler

Example:
```python
# Add to _initialize_tools() method
"helm_list": {
    "name": "helm_list",
    "description": "List Helm releases",
    "inputSchema": {
        "type": "object",
        "properties": {
            "namespace": {"type": "string", "description": "Kubernetes namespace"},
            "all": {"type": "boolean", "description": "Show all releases"}
        }
    }
}

# Add to _execute_tool() method
elif tool_name == "helm_list":
    return await self._helm_list(arguments)

# Implement the tool handler
async def _helm_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
    cmd = ['helm', 'list']
    if args.get('all', False):
        cmd.append('--all')
    if 'namespace' in args:
        cmd.extend(['-n', args['namespace']])
    
    return await self.executor.execute(cmd)
```

### Testing

```bash
# Run unit tests
make test

# Test MCP server
python test_mcp.py

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
- Verify Python dependencies installed (aiohttp, yaml)
- Check logs: `make logs`
- Test health endpoint: `curl http://localhost:8080/health`
- Test MCP protocol: `python test_mcp.py`

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
