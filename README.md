# AI SRE - Intelligent Site Reliability Engineering

A lean, containerized toolbox for AI-powered Site Reliability Engineering operations. This project provides a lightweight MCP (Model Context Protocol) server that exposes Kubernetes, Git, and Flux operations through a clean REST API, designed to be orchestrated by external systems like N8N.

## 🏗️ Architecture

- **Container**: Stateless command executor (< 256MB RAM, < 500MB image)
- **Orchestration**: External (N8N handles intelligence, alert processing, RAG/vector store)
- **GitOps**: Flux-only approach for simplified operations
- **API**: RESTful MCP Server endpoints for all operations

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd ai-sre
make init
make build
make run

# Test the API
curl http://localhost:8080/health
```

## 📋 Features

### MCP Server API Endpoints

- **Kubernetes**: `/kubectl/{action}` - All kubectl operations
- **Git**: `/git/{action}` - Git operations and repository management
- **Flux**: `/flux/{action}` - Flux GitOps operations
- **Monitoring**: `/prometheus/query`, `/alertmanager/alerts`
- **System**: `/health`, `/ready`, `/version`

### Container Specifications

- **Size**: < 500MB image
- **Memory**: < 256MB runtime
- **CPU**: < 0.2 cores
- **Startup**: < 10 seconds
- **Dependencies**: Minimal (Python, aiohttp)

## 📁 Project Structure

```
ai-sre/
├── README.md                 # This file
├── QUICKSTART.md            # Developer quick start guide
├── Dockerfile               # Lean container definition
├── docker-compose.yaml      # Local development setup
├── Makefile                 # Build and management commands
├── .env.template            # Environment variables template
├── .gitignore              # Security-conscious ignore file
├── agent.md                # Sample knowledge base for N8N
├── docs/
│   ├── REQUIREMENTS.md     # Comprehensive requirements
│   └── ARCHITECTURE.md     # Architecture overview
├── src/
│   └── mcp_server.py       # Lightweight MCP Server (~400 lines)
└── scripts/
    └── entrypoint.sh       # Container initialization
```

## 🔧 Development

See [QUICKSTART.md](QUICKSTART.md) for detailed development instructions.

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Quick Start Guide](QUICKSTART.md)

## 🤝 Contributing

This project follows a lean architecture principle. All intelligence and orchestration should be handled externally (e.g., via N8N), keeping the container purely functional.

## 📄 License

MIT License - see LICENSE file for details.
