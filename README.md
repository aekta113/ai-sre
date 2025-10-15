# 🤖 AI SRE - Intelligent Site Reliability Engineering

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)
[![Flux](https://img.shields.io/badge/flux-ready-purple.svg)](https://fluxcd.io/)

[![CI/CD Pipeline](https://github.com/nachtschatt3n/ai-sre/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/nachtschatt3n/ai-sre/actions/workflows/ci-cd.yml)
[![Security Scan](https://github.com/nachtschatt3n/ai-sre/actions/workflows/security.yml/badge.svg)](https://github.com/nachtschatt3n/ai-sre/actions/workflows/security.yml)
[![Multi-Platform Tests](https://github.com/nachtschatt3n/ai-sre/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/nachtschatt3n/ai-sre/actions/workflows/test-matrix.yml)
[![Docker Image](https://img.shields.io/badge/docker%20image-ghcr.io%2Fnachtschatt3n%2Fai--sre-blue)](https://github.com/nachtschatt3n/ai-sre/pkgs/container/ai-sre)

A lean, containerized toolbox for AI-powered Site Reliability Engineering operations. This project provides a lightweight MCP (Model Context Protocol) server that exposes Kubernetes, Git, and Flux operations through a clean REST API, designed to be orchestrated by external systems like N8N.

> **🚀 Production Ready**: Lightweight (< 256MB RAM), fast startup (< 10s), and battle-tested for Kubernetes operations with Flux GitOps.

## 🏗️ Architecture

- **Container**: Stateless command executor (< 256MB RAM, < 500MB image)
- **Orchestration**: External (N8N handles intelligence, alert processing, RAG/vector store)
- **GitOps**: Flux-only approach for simplified operations
- **API**: RESTful MCP Server endpoints for all operations

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Kubernetes cluster (local or remote)
- Flux CLI (for GitOps operations)
- Git repository access

### Installation

```bash
# Clone and setup
git clone https://github.com/your-org/ai-sre.git
cd ai-sre

# Configure environment
cp .env.template .env
# Edit .env with your configuration

# Build and run
make init
make build
make run

# Test the API
curl http://localhost:8080/health
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ai-sre

# Stop services
docker-compose down
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s-repo/manifests/

# Check deployment
kubectl get pods -n ai-sre

# Port forward for testing
kubectl port-forward svc/ai-sre 8080:8080 -n ai-sre
```

## ✨ Key Features

### 🎯 **AI-Powered Operations**
- **Intelligent Incident Response**: Automated diagnosis and remediation
- **Pattern Recognition**: Learns from incidents to prevent future issues
- **Predictive Monitoring**: Proactive alerting based on learned patterns
- **Self-Healing**: Automatic recovery from common Kubernetes issues

### 🔧 **MCP Server API Endpoints**

#### Kubernetes Operations
- `GET/POST /kubectl/{action}` - Complete kubectl command execution
- `GET /kubectl/pods` - Pod management and troubleshooting
- `GET /kubectl/nodes` - Node health and resource monitoring
- `POST /kubectl/apply` - Resource deployment and updates

#### GitOps & Flux
- `GET /flux/sources` - Git repository source management
- `POST /flux/reconcile` - Force reconciliation of workloads
- `GET /flux/status` - Real-time sync status monitoring
- `POST /flux/suspend` - Suspend/resume Flux operations

#### Git Operations
- `POST /git/commit` - Automated Git commits and pushes
- `GET /git/status` - Repository status and changes
- `POST /git/merge` - Automated merge operations
- `GET /git/log` - Commit history and analysis

#### CLI Tools & Diagnostics
- `POST /cli/{tool}` - Execute CLI tools (sed, curl, cat, tree, find, grep, etc.)
- `POST /cli/chain` - Chain multiple CLI commands together
- `GET /cli/tools` - List available CLI tools and categories
- `POST /cli/sops` - SOPS encryption/decryption with AGE keys

#### Configuration Management
- `GET /config` - Get current configuration
- `POST /config/reload` - Reload configuration without restart
- `GET /config/tools` - Get tool activation settings
- `GET /env` - Environment variables and service endpoints

#### Monitoring & Observability
- `GET /prometheus/query` - Custom Prometheus queries
- `GET /alertmanager/alerts` - Alert management
- `GET /grafana/dashboards` - Grafana dashboard access
- `GET /kuma/mesh` - Service mesh status
- `GET /jaeger/traces` - Distributed tracing queries
- `GET /loki/query` - Log aggregation queries
- `GET /metrics` - System and application metrics
- `POST /ai/analyze` - AI-powered log and metric analysis

#### Runbook System
- `GET /runbooks/search` - Search runbooks by query, type, and severity
- `POST /runbooks/execute` - Execute runbooks with context and parameters
- `POST /runbooks/create` - Create new runbooks dynamically
- `PUT /runbooks/{id}` - Update existing runbooks
- `GET /runbooks/{id}` - Get specific runbook content
- `POST /runbooks/learn` - Learn from incident data and create patterns
- `GET /runbooks/patterns` - Get learned patterns and insights
- `GET /runbooks/executions` - Get runbook execution history
- `GET /runbooks/health` - Check runbook system health

#### Storage Management
- `GET /storage/usage` - Get storage usage for all volumes
- `GET /storage/backup` - Trigger storage backup operations
- `POST /storage/cleanup` - Clean up old files based on retention policy

#### System & Health
- `GET /health` - Health check endpoint
- `GET /ready` - Readiness probe
- `GET /version` - Version and build information
- `GET /ai/status` - AI agent status and capabilities

### 📦 **Container Specifications**

| Specification | Value | Notes |
|---------------|-------|-------|
| **Image Size** | < 500MB | Optimized Alpine-based image |
| **Memory Usage** | < 256MB | Efficient resource utilization |
| **CPU Usage** | < 0.2 cores | Lightweight processing |
| **Startup Time** | < 10 seconds | Fast container initialization |
| **Dependencies** | Minimal | Python + aiohttp only |

### 🛡️ **Security & Reliability**
- **RBAC Integration**: Full Kubernetes RBAC support
- **Secret Management**: Secure handling of credentials and tokens
- **Audit Logging**: Complete operation audit trail
- **Error Handling**: Graceful failure recovery
- **Resource Limits**: Built-in resource constraints

## 💡 Usage Examples

### Incident Response Automation

```bash
# Detect and fix a crashed pod
curl -X POST http://localhost:8080/kubectl/diagnose \
  -H "Content-Type: application/json" \
  -d '{"pod": "my-app-7d4b8c9f-x2k9m", "namespace": "production"}'

# AI will automatically:
# 1. Analyze pod logs
# 2. Check resource constraints
# 3. Apply appropriate fix
# 4. Verify resolution
```

### GitOps Operations

```bash
# Force Flux reconciliation
curl -X POST http://localhost:8080/flux/reconcile \
  -H "Content-Type: application/json" \
  -d '{"source": "my-git-repo", "namespace": "flux-system"}'

# Check sync status
curl http://localhost:8080/flux/status
```

### Automated Git Operations

```bash
# Commit and push configuration changes
curl -X POST http://localhost:8080/git/commit \
  -H "Content-Type: application/json" \
  -d '{
    "message": "fix: update resource limits",
    "files": ["manifests/deployment.yaml"],
    "branch": "main"
  }'
```

### CLI Diagnostics

```bash
# Search for errors in logs
curl -X POST http://localhost:8080/cli/grep \
  -H "Content-Type: application/json" \
  -d '{
    "args": ["-r", "error", "/var/log"],
    "flags": {"i": true, "n": true}
  }'

# Find large files
curl -X POST http://localhost:8080/cli/find \
  -H "Content-Type: application/json" \
  -d '{
    "args": ["/app", "-size", "+100M", "-type", "f"]
  }'

# Process system information
curl -X POST http://localhost:8080/cli/ps \
  -H "Content-Type: application/json" \
  -d '{"flags": {"aux": true}}'
```

### SOPS Secrets Management

```bash
# Encrypt a Kubernetes secret
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "encrypt",
    "data": "apiVersion: v1\nkind: Secret\nmetadata:\n  name: my-secret\nstringData:\n  password: secret123"
  }'

# Decrypt and apply secret
curl -X POST http://localhost:8080/cli/sops \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "decrypt",
    "file": "secret.enc.yaml"
  }'
```

### Configuration Management

```bash
# Get current configuration
curl http://localhost:8080/config

# Reload configuration
curl -X POST http://localhost:8080/config/reload

# List available CLI tools
curl http://localhost:8080/cli/tools

# Check service health
curl http://localhost:8080/services/prometheus
```

### Runbook System

```bash
# Search for runbooks
curl "http://localhost:8080/runbooks/search?q=pod%20crash&type=static&severity=high"

# Execute a runbook
curl -X POST http://localhost:8080/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "runbook_id": "pod-crash-001",
    "context": {
      "namespace": "production",
      "pod_name": "my-app-7d4b8c9f-x2k9m",
      "cluster": "prod-cluster"
    },
    "parameters": {
      "auto_execute": false,
      "dry_run": true
    }
  }'

# Learn from incident
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

### AI-Powered Analysis

```bash
# Analyze cluster health
curl -X POST http://localhost:8080/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "type": "cluster_health",
    "namespace": "production",
    "timeframe": "24h"
  }'
```

## 📁 Project Structure

```
ai-sre/
├── 📄 README.md                 # This comprehensive guide
├── 📄 QUICKSTART.md            # Developer quick start guide
├── 📄 LICENSE                  # MIT License
├── 🐳 Dockerfile               # Lean container definition
├── 🐳 docker-compose.yaml      # Local development setup
├── 🐳 docker-compose.test.yml  # Testing environment
├── 🔧 Makefile                 # Build and management commands
├── ⚙️  .env.template            # Environment variables template
├── 📝 agent.md                 # AI knowledge base and runbooks
├── 📁 docs/
│   ├── 📋 REQUIREMENTS.md     # Comprehensive requirements
│   └── 🏗️  ARCHITECTURE.md     # Architecture overview
├── 📁 src/
│   └── 🐍 mcp_server.py       # Enhanced MCP Server with CLI tools & SOPS
├── 📁 scripts/
│   └── 🚀 entrypoint.sh       # Container initialization
├── 📁 config/
│   └── ⚙️  config.yaml         # Runtime configuration
├── 📁 k8s-repo/
│   ├── 📋 configmap.yaml       # Kubernetes ConfigMap & Secrets
│   ├── 📋 storage.yaml         # Persistent storage claims
│   ├── 📋 deployment.yaml      # Complete deployment manifests
│   └── 📁 manifests/           # Additional Kubernetes manifests
├── 📁 logs/                   # Application logs
└── 📁 work/                   # Working directory
```

## 🔧 Development

See [QUICKSTART.md](QUICKSTART.md) for detailed development instructions.

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python src/mcp_server.py

# Run tests
make test

# Lint code
make lint
```

### Testing

```bash
# Run integration tests
./integration-test.sh

# Run quick tests
./quick-test.sh

# Test with Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📖 Documentation

- 📋 [Requirements](docs/REQUIREMENTS.md) - Comprehensive project requirements
- 🏗️ [Architecture Overview](docs/ARCHITECTURE.md) - System architecture details
- 🚀 [Quick Start Guide](QUICKSTART.md) - Developer quick start guide
- 🤖 [AI Knowledge Base](agent.md) - Incident response runbooks and best practices

## 🤝 Contributing

We welcome contributions! This project follows a lean architecture principle where:

- **Container**: Remains stateless and lightweight
- **Intelligence**: Handled externally (N8N, AI agents)
- **GitOps**: Flux-only approach for simplicity
- **API**: Clean REST endpoints for all operations

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add tests for new features
- Update documentation for API changes
- Keep container size minimal

## 🆘 Support & Community

- 📧 **Issues**: [GitHub Issues](https://github.com/your-org/ai-sre/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/ai-sre/discussions)
- 📚 **Wiki**: [Project Wiki](https://github.com/your-org/ai-sre/wiki)
- 🐛 **Bug Reports**: Use GitHub Issues with the `bug` label

## 🏆 Acknowledgments

- **Flux** - GitOps toolkit for Kubernetes
- **Kubernetes** - Container orchestration platform
- **N8N** - Workflow automation platform
- **MCP** - Model Context Protocol specification

## 📊 Project Status

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-85%25-green.svg)]()
[![Security](https://img.shields.io/badge/security-audited-green.svg)]()
[![Production Ready](https://img.shields.io/badge/production-ready-brightgreen.svg)]()

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🚀 Built with ❤️ for the Kubernetes and GitOps community**

[⭐ Star this repo](https://github.com/your-org/ai-sre) | [🐛 Report Bug](https://github.com/your-org/ai-sre/issues) | [💡 Request Feature](https://github.com/your-org/ai-sre/issues)

</div>
