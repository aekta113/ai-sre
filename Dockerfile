# AI SRE - Self-Healing Toolbox Container
# Multi-stage build for security
FROM alpine:3.20 AS builder

LABEL maintainer="AI-SRE Team"
LABEL description="Lean CLI toolbox container for Kubernetes operations via N8N"
LABEL version="2.1.1"

# Update package index and install base system packages
RUN apk update && apk upgrade && apk add --no-cache \
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
    openssl \
    # Security updates
    ca-certificates

# Install kubectl
ARG KUBECTL_VERSION=v1.31.0
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; fi && \
    if [ "$ARCH" = "aarch64" ]; then ARCH="arm64"; fi && \
    curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/ && \
    kubectl version --client

# Install Helm
ARG HELM_VERSION=v3.15.4
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && VERIFY_CHECKSUM=false ./get_helm.sh --version ${HELM_VERSION} \
    && rm get_helm.sh

# Install Flux CLI v2
ARG FLUX_VERSION=2.3.0
RUN curl -s https://fluxcd.io/install.sh | bash

# Install GitHub CLI
RUN apk add --no-cache github-cli

# Install mise (modern runtime version manager)
RUN curl https://mise.run | sh && \
    mv ~/.local/bin/mise /usr/local/bin/mise

# Install Node.js 18 via mise
ENV MISE_DATA_DIR=/usr/local/share/mise
ENV MISE_CACHE_DIR=/usr/local/share/mise/cache
RUN mise use --global node@18 && \
    mise install node@18

# Install Claude CLI
RUN eval "$(mise activate bash)" && \
    npm install -g @anthropics/claude-code

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
COPY src/mcp_server_protocol.py /app/src/
COPY scripts/entrypoint.sh /app/scripts/

# Make scripts executable and secure
RUN chmod +x /app/scripts/*.sh && \
    chmod 755 /app/src/mcp_server_protocol.py

# Final runtime stage - minimal Alpine image
FROM alpine:3.20

# Install only runtime dependencies and essential tools
RUN apk update && apk upgrade && apk add --no-cache \
    python3 \
    py3-aiohttp \
    py3-yaml \
    py3-dotenv \
    ca-certificates \
    # Essential tools for runtime
    bash \
    curl \
    wget \
    git \
    jq \
    yq \
    grep \
    sed \
    gawk \
    tree \
    findutils \
    netcat-openbsd \
    github-cli \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Copy only the essential binaries from builder stage
COPY --from=builder /usr/local/bin/kubectl /usr/local/bin/
COPY --from=builder /usr/local/bin/helm /usr/local/bin/
COPY --from=builder /usr/local/bin/flux /usr/local/bin/

# Copy mise and Node.js from builder stage
COPY --from=builder /usr/local/bin/mise /usr/local/bin/
COPY --from=builder /usr/local/share/mise /usr/local/share/mise

# Copy application files from builder stage
COPY --from=builder /app /app

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
    PYTHONUNBUFFERED=1 \
    MISE_DATA_DIR=/usr/local/share/mise \
    MISE_CACHE_DIR=/usr/local/share/mise/cache \
    PATH="/usr/local/share/mise/installs/node/18/bin:${PATH}"

# Entry point
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command - run MCP protocol server
CMD ["python3", "/app/src/mcp_server_protocol.py"]
