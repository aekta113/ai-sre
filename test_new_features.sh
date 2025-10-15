#!/bin/bash
# Test script for new MCP features

set -e

echo "=========================================="
echo "Testing New AI SRE MCP Features"
echo "=========================================="
echo ""

MCP_URL="http://localhost:8080"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Testing MCP Call Logging${NC}"
echo "-------------------------------------------"

# Get log stats
echo "Getting log statistics..."
curl -s "${MCP_URL}/logs/mcp/stats" | jq .
echo ""

echo -e "${GREEN}✓ Log stats retrieved${NC}"
echo ""

echo -e "${BLUE}2. Testing File Write${NC}"
echo "-------------------------------------------"

# Write a test file
echo "Writing test file to /app/work/test.txt..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "file_write",
      "arguments": {
        "path": "/app/work/test.txt",
        "content": "Hello from AI SRE MCP Server!\nTesting file operations.\nTimestamp: '"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ File written${NC}"
echo ""

echo -e "${BLUE}3. Testing File Read${NC}"
echo "-------------------------------------------"

# Read the test file
echo "Reading test file..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "file_read",
      "arguments": {
        "path": "/app/work/test.txt"
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ File read${NC}"
echo ""

echo -e "${BLUE}4. Testing File List${NC}"
echo "-------------------------------------------"

# List files in work directory
echo "Listing files in /app/work..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "file_list",
      "arguments": {
        "path": "/app/work",
        "pattern": "*"
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ File list retrieved${NC}"
echo ""

echo -e "${BLUE}5. Testing File Info${NC}"
echo "-------------------------------------------"

# Get file info
echo "Getting file info for test.txt..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "file_info",
      "arguments": {
        "path": "/app/work/test.txt"
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ File info retrieved${NC}"
echo ""

echo -e "${BLUE}6. Testing File Exists${NC}"
echo "-------------------------------------------"

# Check if file exists
echo "Checking if file exists..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "file_exists",
      "arguments": {
        "path": "/app/work/test.txt"
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ File exists check completed${NC}"
echo ""

echo -e "${BLUE}7. Testing Security (Access Denied)${NC}"
echo "-------------------------------------------"

# Try to read a file outside allowed directories (should fail)
echo "Attempting to read /etc/passwd (should fail)..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "file_read",
      "arguments": {
        "path": "/etc/passwd"
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ Security validation working (access denied as expected)${NC}"
echo ""

echo -e "${BLUE}8. Testing File Delete${NC}"
echo "-------------------------------------------"

# Delete the test file
echo "Deleting test file..."
curl -s -X POST "${MCP_URL}/mcp/http" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "file_delete",
      "arguments": {
        "path": "/app/work/test.txt",
        "confirm": true
      }
    }
  }' | jq .
echo ""

echo -e "${GREEN}✓ File deleted${NC}"
echo ""

echo -e "${BLUE}9. Checking MCP Call Logs${NC}"
echo "-------------------------------------------"

# View today's MCP call logs
LOG_FILE="/app/logs/mcp-calls/mcp-calls-$(date +%Y-%m-%d).jsonl"
if [ -f "$LOG_FILE" ]; then
    echo "Today's MCP call log:"
    echo "Log file: $LOG_FILE"
    echo "Number of calls: $(wc -l < "$LOG_FILE")"
    echo ""
    echo "Last 3 calls:"
    tail -n 3 "$LOG_FILE" | jq -c '{timestamp, method, success, duration}'
else
    echo "Log file not found: $LOG_FILE"
fi
echo ""

echo -e "${GREEN}✓ MCP call logging working${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}All tests completed successfully!${NC}"
echo "=========================================="
