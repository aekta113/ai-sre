# AI SRE Makefile

.PHONY: help build run stop clean logs shell test

# Variables
IMAGE_NAME := ai-sre
CONTAINER_NAME := ai-sre
VERSION := 1.0.0

help: ## Show this help message
	@echo "AI SRE - Self-Healing Toolbox Container"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build the Docker container
	@echo "Building $(IMAGE_NAME):$(VERSION)..."
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .

run: ## Run the container with docker-compose
	@echo "Starting AI SRE container..."
	docker-compose up -d

stop: ## Stop the running container
	@echo "Stopping AI SRE container..."
	docker-compose down

restart: stop run ## Restart the container

logs: ## Show container logs
	docker-compose logs -f ai-sre

shell: ## Open a shell in the running container
	docker exec -it $(CONTAINER_NAME) /bin/bash

test-mcp: ## Test MCP Server endpoints
	@echo "Testing MCP Server health..."
	@curl -s http://localhost:8080/health | jq .
	@echo ""
	@echo "Testing MCP Protocol initialization..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "make-test", "version": "1.0.0"}}}' | jq .
	@echo ""
	@echo "Testing MCP tools list..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | jq .

test-quick: ## Run quick test suite
	@echo "Running quick test suite..."
	@./quick-test.sh

test-full: ## Run comprehensive test suite
	@echo "Running comprehensive test suite..."
	@./test.sh

test-integration: ## Run integration test with mock k8s
	@echo "Running integration test..."
	@./integration-test.sh

test-kubectl: ## Test kubectl command via MCP
	@echo "Testing kubectl get pods via MCP Protocol..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "kubectl_get", "arguments": {"resource": "pods", "namespace": "default", "output": "json"}}}' | jq .

test-git: ## Test git command via MCP
	@echo "Testing git status via MCP Protocol..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "git_status", "arguments": {}}}' | jq .

test-flux: ## Test flux command via MCP
	@echo "Testing flux status via MCP Protocol..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "flux_status", "arguments": {"namespace": "flux-system"}}}' | jq .

test-git-tools: ## Test git tools via MCP
	@echo "Testing git status via MCP Protocol..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "git_status", "arguments": {}}}' | jq .
	@echo ""
	@echo "Testing git pull via MCP Protocol..."
	@curl -s -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "git_pull", "arguments": {}}}' | jq .

clean: ## Clean up containers and images
	@echo "Cleaning up..."
	docker-compose down -v
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest 2>/dev/null || true

env-setup: ## Setup environment from template
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.template .env; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

dev: ## Run container in development mode with live code reload
	@echo "Starting in development mode..."
	docker-compose run --rm \
		-v $(PWD)/src:/app/src:ro \
		-v $(PWD)/scripts:/app/scripts:ro \
		--entrypoint /bin/bash \
		ai-sre

init: env-setup ## Initialize project (create .env, directories)
	@echo "Creating required directories..."
	@mkdir -p k8s-repo logs work
	@echo "Project initialized!"

status: ## Check status of all components
	@echo "Container status:"
	@docker ps --filter name=$(CONTAINER_NAME) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "MCP Server status:"
	@curl -s http://localhost:8080/health 2>/dev/null && echo "✅ MCP Server is healthy" || echo "❌ MCP Server is not responding"

install-n8n-workflow: ## Install example N8N workflow
	@echo "Example N8N workflow configuration:"
	@echo "1. Add MCP Client node to your workflow"
	@echo "2. Configure MCP Client:"
	@echo "   - Connection Type: WebSocket"
	@echo "   - Server URL: ws://ai-sre.ai.svc.cluster.local:8080/mcp"
	@echo "   - Authentication: None"
	@echo "3. Use available MCP tools: kubectl_get, kubectl_logs, flux_status, etc."
	@echo "4. Test connection with health_check tool"

ci-test: ## Run CI tests locally
	@echo "Running CI tests locally..."
	@docker build -t ai-sre:ci-test .
	@docker run --rm -p 8080:8080 ai-sre:ci-test &
	@sleep 10
	@curl -f http://localhost:8080/health || exit 1
	@curl -f -X POST http://localhost:8080/mcp/http \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' || exit 1
	@pkill -f "ai-sre:ci-test" || true
	@echo "✅ CI tests passed!"

docker-push: ## Push Docker image to registry
	@echo "Pushing Docker image to registry..."
	@docker tag ai-sre:latest ghcr.io/nachtschatt3n/ai-sre:latest
	@docker push ghcr.io/nachtschatt3n/ai-sre:latest

security-scan: ## Run security scan locally
	@echo "Running security scan..."
	@docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image ai-sre:latest
