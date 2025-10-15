#!/bin/bash
# AI SRE Container Entrypoint

set -e

echo "=========================================="
echo "AI SRE - Self-Healing Toolbox Container"
echo "=========================================="

# Configure Git
if [ -n "$GITHUB_USER" ]; then
    git config --global user.name "$GITHUB_USER"
fi

if [ -n "$GITHUB_EMAIL" ]; then
    git config --global user.email "$GITHUB_EMAIL"
fi

# Setup GitHub authentication
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Setting up GitHub authentication..."
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
fi

# Setup kubeconfig
if [ -f "$KUBECONFIG" ]; then
    echo "Kubeconfig found at: $KUBECONFIG"
    kubectl config current-context || true
else
    echo "Warning: Kubeconfig not found at: $KUBECONFIG"
fi

# Create working directories
mkdir -p /app/work /app/logs

# Check Flux installation
if command -v flux &> /dev/null; then
    echo "Flux version: $(flux version --client)"
fi

# Start the MCP Server
echo "Starting MCP Server..."
exec "$@"
