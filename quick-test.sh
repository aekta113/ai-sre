#!/bin/bash
# AI SRE Quick Test Script
# Basic functionality test for the AI SRE container

set -e

echo "🚀 AI SRE Quick Test"
echo "==================="

# Build container first
echo "🔨 Building AI SRE container..."
docker build -t ai-sre:quick-test .

# Start container
echo "📦 Starting AI SRE container..."
docker run -d --name ai-sre-quick-test -p 8080:8080 ai-sre:quick-test

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 10

# Test basic endpoints
echo "🔍 Testing basic endpoints..."

echo "Testing health endpoint..."
curl -s http://localhost:8080/health | jq .

echo "Testing ready endpoint..."
curl -s http://localhost:8080/ready | jq .

echo "Testing version endpoint..."
curl -s http://localhost:8080/version | jq .

# Test kubectl
echo "🔧 Testing kubectl functionality..."
curl -s -X POST http://localhost:8080/kubectl/version \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

# Test git
echo "📝 Testing git functionality..."
curl -s -X POST http://localhost:8080/git/status \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

# Test container tools
echo "🛠️ Testing container tools..."
echo "kubectl version:"
docker exec ai-sre-quick-test kubectl version --client

echo "helm version:"
docker exec ai-sre-quick-test helm version --client

echo "flux version:"
docker exec ai-sre-quick-test flux version --client

echo "git version:"
docker exec ai-sre-quick-test git --version

# Check container stats
echo "📊 Container stats:"
docker stats --no-stream ai-sre-quick-test

# Cleanup
echo "🧹 Cleaning up..."
docker stop ai-sre-quick-test
docker rm ai-sre-quick-test

echo "✅ Quick test completed!"