# AI SRE Development Requirements Document

## 1. Executive Summary

AI SRE is a lean CLI toolbox container for Kubernetes cluster remediation that executes commands as directed by N8N workflows. The container provides all necessary CLI tools for GitOps operations while N8N handles orchestration, alert processing, knowledge base management (RAG/Vector store), and Telegram integration.

## 2. System Architecture

### 2.1 Core Components

#### Self-Healing Toolbox Container
- **Purpose**: Execution environment for CLI commands triggered by N8N
- **Base Image**: Alpine Linux (lightweight)
- **CLI Tools Required**:
  - `kubectl`: Kubernetes cluster management
  - `git`: Version control operations
  - `gh`: GitHub CLI for PR/issue management
  - `flux`: GitOps operator (Flux only)
  - `curl`: HTTP operations
  - `jq`: JSON processing
  - `yq`: YAML processing
  - `sed/awk/grep`: Text processing
  - `helm`: Package management for Kubernetes
  - Shell utilities: `zsh`, `cat`, `find`, `tree`, `xargs`

#### MCP Server Integration
- **Purpose**: Provides structured API interface between N8N and CLI tools
- **Features**:
  - Execute kubectl commands from N8N requests
  - Handle authentication and context switching
  - Provide structured JSON responses
  - Error handling and command validation

#### N8N Orchestration (External)
- **Purpose**: Main orchestration and intelligence layer
- **Responsibilities**:
  - Receive and parse Telegram alerts
  - Manage vector store and RAG for knowledge base
  - Orchestrate remediation workflows
  - Handle human approvals via Telegram
  - Call MCP Server endpoints for execution
  - Track remediation history and learning

### 2.2 Container Integrations

#### GitHub Integration
- **Repository Access**: Read/write access to K8s source repository
- **Operations via MCP**:
  - Clone/pull repositories
  - Create branches
  - Commit changes
  - Push updates
  - Manage pull requests

#### Flux Integration
- **GitOps Management**: Flux-specific operations only
- **Operations**:
  - Trigger reconciliation
  - Check sync status
  - Manage Flux resources
  - Handle rollbacks

#### Monitoring Systems (Read-only)
- **Prometheus**: Query metrics via API
- **Alertmanager**: Fetch alert details
- **Uptime Kuma**: Check service status

## 3. Data Flow Architecture

```
1. Alert Generation
   └─> Prometheus/Uptime Kuma detect issue
   
2. Alert to N8N (via Telegram)
   └─> Alertmanager → Telegram → N8N Webhook
   
3. N8N Processing
   ├─> Parse alert details
   ├─> Query vector store for similar incidents
   └─> Consult RAG knowledge base
   
4. N8N Diagnosis
   ├─> Formulate remediation plan
   └─> Request diagnostic data via MCP Server
   
5. Human Approval (via N8N → Telegram)
   └─> N8N sends approval request to Telegram
   
6. Execution (N8N → MCP Server)
   ├─> N8N triggers kubectl commands via MCP
   ├─> N8N triggers git operations via MCP
   └─> N8N triggers flux sync via MCP
   
7. Verification
   ├─> N8N queries metrics via MCP
   └─> N8N confirms resolution
   
8. Learning (N8N)
   └─> N8N updates vector store with resolution
```

## 4. Container Specifications

### 4.1 Base Container Structure

```dockerfile
FROM alpine:3.19

# Install base packages
RUN apk add --no-cache \
    curl wget git openssh-client \
    bash zsh coreutils findutils \
    grep sed gawk jq yq \
    python3 py3-pip nodejs npm

# Install Kubernetes tools
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl && mv kubectl /usr/local/bin/

# Install GitHub CLI
RUN apk add --no-cache github-cli

# Install Flux CLI (v2)
RUN curl -s https://fluxcd.io/install.sh | bash

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 4.2 Environment Variables

```yaml
# GitHub Configuration
GITHUB_TOKEN: "ghp_xxxxxxxxxxxx"          # Personal access token with repo permissions
GITHUB_REPO: "org/k8s-configs"            # Target repository for GitOps
GITHUB_USER: "ai-sre-bot"                 # Git commit author
GITHUB_EMAIL: "ai-sre@example.com"        # Git commit email

# Kubernetes Configuration
KUBECONFIG: "/app/.kube/config"           # Path to kubeconfig file
KUBE_CONTEXT: "production"                # Default context to use
KUBE_NAMESPACE: "default"                 # Default namespace

# MCP Server Configuration
MCP_SERVER_PORT: "8080"                   # Port for MCP Server to listen on
MCP_API_KEY: "mcp_xxxxxxxxxxxxx"          # MCP authentication (if needed)

# Agent Configuration
AGENT_MODE: "executor"                    # Container runs as command executor
AGENT_LOG_LEVEL: "INFO"                   # DEBUG|INFO|WARN|ERROR
AGENT_WORKDIR: "/app/work"                # Working directory for operations

# Flux Configuration
FLUX_NAMESPACE: "flux-system"             # Flux installation namespace
FLUX_TIMEOUT: "5m"                        # Timeout for flux operations

# Repository Configuration
LOCAL_REPO_PATH: "/app/k8s-repo"          # Local path for git operations
GIT_BRANCH: "main"                        # Default branch to work with

# Alert Sources (for querying metrics)
PROMETHEUS_URL: "http://prometheus:9090"   # Prometheus API endpoint
ALERTMANAGER_URL: "http://alertmanager:9093" # Alertmanager API endpoint
UPTIME_KUMA_URL: "http://uptime-kuma:3001"  # Uptime Kuma API endpoint

# Safety Configuration
DRY_RUN: "false"                          # Enable dry-run mode
OPERATION_TIMEOUT: "300"                  # Timeout for operations in seconds
MAX_RETRY_ATTEMPTS: "3"                   # Max retries for failed operations
```

## 5. Development Phases

### Phase 1: Foundation (Week 1)
- [ ] Setup base container with all CLI tools
- [ ] Implement GitHub authentication and git configuration
- [ ] Setup Kubernetes client configuration
- [ ] Create MCP Server base structure
- [ ] Implement logging framework

### Phase 2: MCP Server Implementation (Week 1-2)
- [ ] Create MCP Server API endpoints
- [ ] Implement kubectl command executor
- [ ] Implement git operations executor
- [ ] Implement flux command executor
- [ ] Add structured JSON response format
- [ ] Implement error handling and validation

### Phase 3: Command Executors (Week 2-3)
- [ ] Create kubectl wrapper functions
- [ ] Create git operations wrapper
- [ ] Create flux operations wrapper
- [ ] Implement helm operations
- [ ] Add retry logic and timeouts
- [ ] Implement dry-run mode

### Phase 4: Monitoring Integration (Week 3-4)
- [ ] Implement Prometheus query interface
- [ ] Implement Alertmanager client
- [ ] Implement Uptime Kuma client
- [ ] Create metrics aggregation functions
- [ ] Add health check endpoints

### Phase 5: Testing & Hardening (Week 4-5)
- [ ] Create unit tests for all executors
- [ ] Create integration tests with mock K8s
- [ ] Add security validation
- [ ] Performance optimization
- [ ] Create test N8N workflows

### Phase 6: Documentation & Deployment (Week 5)
- [ ] Complete API documentation
- [ ] Create N8N workflow templates
- [ ] Create deployment manifests
- [ ] Setup CI/CD pipeline
- [ ] Create operation runbooks

## 6. Security Requirements

### 6.1 Authentication & Authorization
- Use service account tokens for Kubernetes access
- Implement RBAC with least privilege principle
- Secure storage of GitHub tokens
- MCP Server API key authentication

### 6.2 Audit & Compliance
- Log all executed commands with timestamps
- Track Git commits with clear attribution
- Maintain command execution history
- Structured logging for N8N consumption

### 6.3 Network Security
- Restrict container network access
- Use secure communication with MCP Server
- Limit egress to required endpoints only

## 7. Non-Functional Requirements

### 7.1 Performance
- Command execution: < 5 seconds average
- MCP Server response: < 1 second
- Container startup: < 10 seconds
- Memory usage: < 256MB under normal load

### 7.2 Reliability
- Stateless operation (all state in N8N)
- Automatic restart on failure
- Idempotent command execution
- Clear error reporting to N8N

### 7.3 Scalability
- Support concurrent command execution
- Efficient resource usage
- Minimal container footprint
- Quick startup/shutdown

### 7.4 Observability
- Structured JSON logging
- Command execution metrics
- Health check endpoint
- Performance metrics for N8N

## 8. Success Metrics

- **Command Success Rate**: > 95% successful executions
- **Response Time**: < 5 seconds for 95th percentile
- **Container Reliability**: 99.9% uptime
- **Resource Efficiency**: < 256MB RAM, < 0.2 CPU cores

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Command injection | Critical | Input validation, parameterized commands |
| Credential exposure | High | Secure secret mounting, no logging of secrets |
| Resource exhaustion | Medium | Command timeouts, resource limits |
| Network failures | Medium | Retry logic, clear error reporting |

## 10. Dependencies

### Required Services
- Kubernetes cluster (1.28+)
- GitHub repository with Flux
- MCP Server access
- N8N for orchestration

### Container Dependencies
- kubectl compatible with cluster version
- Flux CLI v2
- Git 2.x+
- GitHub CLI

## 11. Acceptance Criteria

- [ ] All CLI tools installed and functional
- [ ] MCP Server responds to all endpoints
- [ ] Successful kubectl operations
- [ ] Successful git/GitHub operations  
- [ ] Successful Flux operations
- [ ] Structured JSON responses
- [ ] Error handling and validation
- [ ] Health check endpoint working
- [ ] Container runs with minimal resources
- [ ] Documentation complete

## 12. MCP Server API Specification

### Endpoints

```yaml
# Kubernetes Operations
POST /kubectl/get
POST /kubectl/apply
POST /kubectl/delete
POST /kubectl/scale
POST /kubectl/rollout
POST /kubectl/logs
POST /kubectl/exec

# Git Operations
POST /git/clone
POST /git/pull
POST /git/commit
POST /git/push
POST /git/branch
POST /git/merge

# Flux Operations
POST /flux/reconcile
POST /flux/suspend
POST /flux/resume
POST /flux/get
POST /flux/logs

# Monitoring
GET /prometheus/query
GET /alertmanager/alerts
GET /metrics/pod
GET /metrics/node

# System
GET /health
GET /ready
GET /version
```

### Request/Response Format

```json
// Request
{
  "command": "kubectl",
  "action": "get",
  "parameters": {
    "resource": "pods",
    "namespace": "default",
    "output": "json"
  },
  "timeout": 30,
  "dryRun": false
}

// Response
{
  "success": true,
  "data": { /* command output */ },
  "error": null,
  "executionTime": 1.234,
  "timestamp": "2025-10-15T12:00:00Z"
}
```
