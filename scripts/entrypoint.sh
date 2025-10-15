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

# Setup SSH keys for Git operations
if [ -d "/home/aisre/.ssh" ]; then
    echo "Setting up SSH keys..."
    chmod 700 /home/aisre/.ssh
    chmod 600 /home/aisre/.ssh/* 2>/dev/null || true
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    ssh-add /home/aisre/.ssh/* 2>/dev/null || true
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

# Initialize Git repository if configured
if [ -n "$K8S_GIT_REPO" ]; then
    echo "Initializing Kubernetes Git repository..."
    
    REPO_PATH="/app/k8s-repo"
    
    if [ -d "$REPO_PATH" ]; then
        if [ -d "$REPO_PATH/.git" ]; then
            echo "Git repository already exists at $REPO_PATH"
            echo "Pulling latest changes..."
            cd "$REPO_PATH"
            
            # Set remote URL if it's different
            CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
            if [ "$CURRENT_REMOTE" != "$K8S_GIT_REPO" ]; then
                echo "Updating remote URL to: $K8S_GIT_REPO"
                git remote set-url origin "$K8S_GIT_REPO"
            fi
            
            # Pull latest changes
            git fetch origin || echo "Warning: Failed to fetch from origin"
            CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
            git pull origin "$CURRENT_BRANCH" || echo "Warning: Failed to pull latest changes"
        else
            echo "Directory exists but is not a git repository. Re-initializing..."
            rm -rf "$REPO_PATH"
            git clone "$K8S_GIT_REPO" "$REPO_PATH"
        fi
    else
        echo "Cloning Kubernetes repository from: $K8S_GIT_REPO"
        git clone "$K8S_GIT_REPO" "$REPO_PATH"
    fi
    
    # Set default branch if specified
    if [ -n "$K8S_GIT_BRANCH" ]; then
        echo "Checking out branch: $K8S_GIT_BRANCH"
        cd "$REPO_PATH"
        git checkout "$K8S_GIT_BRANCH" 2>/dev/null || echo "Warning: Failed to checkout branch $K8S_GIT_BRANCH"
    fi
    
    echo "Kubernetes repository ready at: $REPO_PATH"
    cd "$REPO_PATH"
    echo "Repository status:"
    git status --porcelain || true
    echo "Latest commit:"
    git log --oneline -1 || true
else
    echo "No Kubernetes Git repository configured (K8S_GIT_REPO not set)"
    echo "Creating empty k8s-repo directory..."
    mkdir -p /app/k8s-repo
fi

# Check Flux installation
if command -v flux &> /dev/null; then
    echo "Flux version: $(flux version --client)"
fi

# Start the MCP Server
echo "Starting MCP Server..."
exec "$@"
