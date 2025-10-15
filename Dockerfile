# AI SRE - Self-Healing Toolbox Container
FROM alpine:3.19

LABEL maintainer="AI-SRE Team"
LABEL description="Lean CLI toolbox container for Kubernetes operations via N8N"
LABEL version="1.0.0"

# Install base system packages
RUN apk add --no-cache \
    # Core utilities
    curl wget git openssh-client \
    bash zsh coreutils findutils \
    grep sed gawk tree \
    # Python for MCP Server
    python3 py3-pip \
    # Processing tools
    jq yq \
    # Network tools
    bind-tools netcat-openbsd \
    # SSL support for Helm
    openssl

# Install kubectl
ARG KUBECTL_VERSION=v1.29.0
ARG ARCH=amd64
RUN curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && kubectl version --client

# Install Helm
ARG HELM_VERSION=v3.13.3
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && VERIFY_CHECKSUM=false ./get_helm.sh --version ${HELM_VERSION} \
    && rm get_helm.sh

# Install Flux CLI v2
ARG FLUX_VERSION=2.2.2
RUN curl -s https://fluxcd.io/install.sh | bash

# Install GitHub CLI
RUN apk add --no-cache github-cli

# Install Python packages for MCP Server
RUN apk add --no-cache \
    py3-aiohttp \
    py3-yaml \
    py3-dotenv

# Create application directory structure
RUN mkdir -p /app/src \
    /app/scripts \
    /app/logs \
    /app/work \
    /app/k8s-repo

# Copy application files
COPY src/mcp_server.py /app/src/
COPY scripts/entrypoint.sh /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Set working directory
WORKDIR /app

# Create non-root user for running the application
RUN addgroup -g 1000 aisre && \
    adduser -D -u 1000 -G aisre aisre && \
    chown -R aisre:aisre /app

# Switch to non-root user
USER aisre

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:8080/health || exit 1

# Default environment variables
ENV AGENT_MODE=executor \
    AGENT_LOG_LEVEL=INFO \
    MCP_SERVER_PORT=8080 \
    PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command - run MCP server
CMD ["python3", "/app/src/mcp_server.py"]
