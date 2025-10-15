# AI SRE Architecture Summary

## Project Overview

**AI SRE** is a lightweight, containerized CLI toolbox designed to execute Kubernetes remediation commands as directed by N8N workflows. The architecture follows a clean separation of concerns:

- **N8N**: Handles all orchestration, intelligence, RAG/vector store, and Telegram integration
- **AI SRE Container**: Provides execution environment with CLI tools and MCP Protocol Server
- **GitOps**: All changes tracked via Git with Flux for synchronization

## Key Design Principles

1. **Lean & Focused**: Container only executes commands, no complex logic
2. **Stateless**: All state managed by N8N, container is purely functional
3. **Protocol-Driven**: Model Context Protocol (MCP) interface for AI integration
4. **GitOps Native**: All cluster changes tracked in Git
5. **Secure**: Minimal attack surface, clear audit trail

## Component Breakdown

### 1. Self-Healing Toolbox Container

**Purpose**: Execution environment for CLI tools

**Included Tools**:
- `kubectl` - Kubernetes operations
- `git` / `gh` - Version control and GitHub
- `flux` - GitOps synchronization (Flux v2)
- `helm` - Package management
- `jq` / `yq` - JSON/YAML processing
- Standard Unix tools (grep, sed, awk, etc.)

**Resource Requirements**:
- Memory: < 256MB
- CPU: < 0.2 cores
- Storage: < 500MB

### 2. MCP Protocol Server

**Purpose**: Model Context Protocol interface for N8N MCP Client

**Protocol**: JSON-RPC 2.0 over WebSocket/HTTP

**Available Tools**:
- **Kubernetes Operations**: `kubectl_get`, `kubectl_describe`, `kubectl_logs`
- **Git Operations**: `git_status`, `git_pull`, `git_commit`, `git_push`
- **GitOps**: `flux_status`
- **CLI Tools**: `cli_tool` (jq, grep, sed, curl, etc.)
- **Health**: `health_check`

**MCP Endpoints**:
```
WebSocket: ws://localhost:8080/mcp
HTTP:      http://localhost:8080/mcp/http
Health:    http://localhost:8080/health
```

**MCP Tool Call Format**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "kubectl_get",
    "arguments": {
      "resource": "pods",
      "namespace": "default"
    }
  }
}
```

### 3. N8N Integration (External)

**Responsibilities**:
- Receive alerts from Telegram
- Parse and analyze alerts
- Query vector store for similar incidents
- Consult RAG knowledge base
- Orchestrate remediation workflow
- Request human approval via Telegram
- Execute fixes via MCP Server
- Update knowledge base with resolutions

## Data Flow

```
1. Alert → Telegram → N8N Webhook
2. N8N analyzes alert using RAG
3. N8N calls MCP Protocol Server for diagnostics
4. N8N formulates remediation plan
5. N8N requests approval via Telegram
6. Upon approval, N8N executes fix via MCP tools
7. MCP Protocol Server executes commands and returns results
8. N8N verifies resolution
9. N8N updates vector store with learning
```

## Deployment Architecture

```yaml
Kubernetes Cluster:
  ├── AI SRE Pod
  │   └── Container with MCP Protocol Server
  ├── Flux System
  │   └── GitOps synchronization
  └── Monitoring Stack
      ├── Prometheus
      ├── Alertmanager
      └── Uptime Kuma

External:
  ├── N8N Instance
  │   ├── Workflows
  │   ├── Vector Store
  │   └── RAG System
  ├── GitHub Repository
  │   └── K8s manifests
  └── Telegram
      └── Alert channel
```

## Security Model

1. **Authentication**:
   - GitHub token for repository access
   - Kubeconfig for cluster access
   - Optional MCP API key

2. **Authorization**:
   - Container runs as non-root user
   - RBAC for Kubernetes operations
   - Git branch protection rules

3. **Audit**:
   - All commands logged with timestamps
   - Git commits tracked
   - N8N workflow history

## Environment Variables

**Minimal Configuration**:
```bash
# GitHub
GITHUB_TOKEN=<token>
GITHUB_REPO=org/k8s-configs

# Kubernetes
KUBECONFIG=/app/.kube/config
KUBE_CONTEXT=production

# Flux
FLUX_NAMESPACE=flux-system

# MCP Protocol Server
MCP_SERVER_PORT=8080

# Monitoring URLs
PROMETHEUS_URL=http://prometheus:9090
ALERTMANAGER_URL=http://alertmanager:9093
```

## Development Workflow

1. **Setup**:
   ```bash
   make init          # Initialize project
   make build         # Build container
   make run          # Start container
   ```

2. **Testing**:
   ```bash
   make test-mcp     # Test MCP endpoints
   make logs         # View logs
   make shell        # Debug inside container
   ```

3. **N8N Integration**:
   - Import workflow templates
   - Configure MCP Client node to `ws://ai-sre:8080/mcp`
   - Test with sample alerts

## Key Benefits

1. **Simplicity**: Clean separation between orchestration (N8N) and execution (container)
2. **Flexibility**: N8N can easily modify workflows without changing container
3. **Scalability**: Stateless container can be replicated
4. **Maintainability**: Minimal codebase, standard tools
5. **Security**: Reduced attack surface, clear boundaries
6. **Cost-Effective**: Low resource requirements

## Success Metrics

- Command execution success rate: > 95%
- Response time: < 5 seconds (95th percentile)
- Container uptime: 99.9%
- Resource usage: < 256MB RAM, < 0.2 CPU

## Future Enhancements

While keeping the container lean, potential improvements include:

1. **Command Validation**: Pre-flight checks before execution
2. **Caching**: Cache frequently used query results
3. **Batch Operations**: Support for bulk command execution
4. **Metrics Export**: Prometheus metrics endpoint
5. **OpenTelemetry**: Distributed tracing support

## Conclusion

The AI SRE project demonstrates a clean, microservices approach to Kubernetes self-healing. By separating concerns between N8N (brain) and the container (hands), we achieve a flexible, maintainable, and secure solution for automated incident response.
