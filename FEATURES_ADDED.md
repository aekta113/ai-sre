# New Features Added to AI SRE MCP Server

## 1. MCP Call Logging with Automatic Retention

### What Was Added
- All MCP calls are now automatically logged to daily JSON log files
- Logs are stored in `/app/logs/mcp-calls/` directory
- 5-day automatic retention with daily cleanup
- Log files are named `mcp-calls-YYYY-MM-DD.jsonl` (JSON Lines format)

### Features
- **Automatic Logging**: Every MCP call is logged with timestamp, method, params, result, error, and duration
- **Daily Log Files**: One log file per day for easy management
- **Automatic Cleanup**: Background task runs daily to delete logs older than 5 days
- **Manual Cleanup**: POST endpoint to trigger cleanup on demand
- **Statistics**: GET endpoint to view log file statistics

### Configuration
```bash
# Environment variables (optional, defaults shown)
MCP_LOG_DIR=/app/logs/mcp-calls
MCP_LOG_RETENTION_DAYS=5
```

### API Endpoints
```bash
# Get log statistics
GET /logs/mcp/stats

# Manually trigger cleanup
POST /logs/mcp/cleanup
```

### Log Entry Format
```json
{
  "timestamp": "2025-10-15T10:30:00.123Z",
  "method": "tools/call",
  "params": {"name": "kubectl_get", "arguments": {...}},
  "success": true,
  "result": {...},
  "duration": 0.234
}
```

### Testing
```bash
# View log statistics
curl http://localhost:8080/logs/mcp/stats

# Manually trigger cleanup
curl -X POST http://localhost:8080/logs/mcp/cleanup

# View log files
ls -lh /app/logs/mcp-calls/
cat /app/logs/mcp-calls/mcp-calls-$(date +%Y-%m-%d).jsonl | jq .
```

---

## 2. File Read/Write Operations

### What Was Added
Six new MCP tools for file operations with security controls:

1. **file_read** - Read file contents
2. **file_write** - Write content to files
3. **file_list** - List directory contents
4. **file_delete** - Delete files (with confirmation)
5. **file_exists** - Check if path exists
6. **file_info** - Get file metadata

### Security Features
- **Restricted Access**: Only allowed directories can be accessed
- **Path Validation**: All paths checked with `_is_path_allowed()` method
- **Delete Confirmation**: file_delete requires `confirm: true` parameter

### Allowed Directories
```python
/app/k8s-repo    # Kubernetes GitOps repository
/app/runbooks    # Runbook storage (static and dynamic)
/app/work        # Working directory
/app/logs        # Log files
```

### Tool Usage Examples

#### 1. Read File
```bash
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "file_read",
      "arguments": {
        "path": "/app/runbooks/static/agent.md",
        "encoding": "utf-8"
      }
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "path": "/app/runbooks/static/agent.md",
  "content": "# AI SRE Knowledge Base\n...",
  "size": 12345,
  "lines": 456
}
```

#### 2. Write File
```bash
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "file_write",
      "arguments": {
        "path": "/app/k8s-repo/manifests/deployment.yaml",
        "content": "apiVersion: apps/v1\nkind: Deployment\n...",
        "create_dirs": true
      }
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "path": "/app/k8s-repo/manifests/deployment.yaml",
  "size": 1234,
  "lines": 45,
  "message": "Successfully wrote 1234 bytes to /app/k8s-repo/manifests/deployment.yaml"
}
```

#### 3. List Files
```bash
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "file_list",
      "arguments": {
        "path": "/app/runbooks",
        "pattern": "*.md",
        "recursive": true
      }
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "path": "/app/runbooks",
  "files": [
    "static/agent.md",
    "static/templates/incident.md",
    "dynamic/incidents/2025-10-15-pod-crashloop.md"
  ],
  "count": 3,
  "recursive": true,
  "pattern": "*.md"
}
```

#### 4. Get File Info
```bash
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "file_info",
      "arguments": {
        "path": "/app/runbooks/static/agent.md"
      }
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "path": "/app/runbooks/static/agent.md",
  "name": "agent.md",
  "is_file": true,
  "is_dir": false,
  "is_symlink": false,
  "size": 12345,
  "size_mb": 0.01,
  "created": "2025-10-01T08:00:00",
  "modified": "2025-10-15T10:30:00",
  "accessed": "2025-10-15T11:00:00",
  "permissions": "644",
  "lines": 456
}
```

#### 5. Check File Exists
```bash
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "file_exists",
      "arguments": {
        "path": "/app/k8s-repo/deployment.yaml"
      }
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "path": "/app/k8s-repo/deployment.yaml",
  "exists": true,
  "is_file": true,
  "is_dir": false
}
```

#### 6. Delete File
```bash
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "file_delete",
      "arguments": {
        "path": "/app/work/temp.txt",
        "confirm": true
      }
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "path": "/app/work/temp.txt",
  "message": "Successfully deleted temp.txt (1234 bytes)"
}
```

---

## Use Cases

### 1. Dynamic Runbook Management
```python
# Read existing runbook
file_read(path="/app/runbooks/static/agent.md")

# Update runbook with new incident
file_write(
    path="/app/runbooks/dynamic/incidents/2025-10-15-memory-leak.md",
    content="# Incident: Memory Leak\n..."
)

# List all incidents
file_list(
    path="/app/runbooks/dynamic/incidents",
    pattern="*.md",
    recursive=True
)
```

### 2. GitOps Workflow
```python
# Read current deployment
deployment = file_read(path="/app/k8s-repo/deployment.yaml")

# Modify deployment (AI can parse and update)
updated_deployment = modify_deployment(deployment['content'])

# Write updated deployment
file_write(
    path="/app/k8s-repo/deployment.yaml",
    content=updated_deployment
)

# Commit changes via git_commit tool
git_commit(
    message="fix: update memory limits",
    files=["deployment.yaml"]
)

# Push to trigger Flux reconciliation
git_push(branch="main")
```

### 3. Log Analysis
```python
# List all MCP call logs
logs = file_list(
    path="/app/logs/mcp-calls",
    pattern="mcp-calls-*.jsonl"
)

# Read specific log file
log_content = file_read(
    path="/app/logs/mcp-calls/mcp-calls-2025-10-15.jsonl"
)

# Get log statistics
stats = http_get("/logs/mcp/stats")
```

---

## Implementation Details

### File Structure Changes
```
src/mcp_server_protocol.py
├── MCPCallLogger class (NEW)
│   ├── log_call()
│   ├── cleanup_old_logs()
│   └── get_log_stats()
├── MCPServer class (UPDATED)
│   ├── call_logger instance
│   ├── allowed_directories list
│   ├── _is_path_allowed() (NEW)
│   ├── _file_read() (NEW)
│   ├── _file_write() (NEW)
│   ├── _file_list() (NEW)
│   ├── _file_delete() (NEW)
│   ├── _file_exists() (NEW)
│   ├── _file_info() (NEW)
│   └── process_message() (UPDATED - adds logging)
└── MCPHTTPServer class (UPDATED)
    ├── background_log_cleanup() (NEW)
    ├── handle_log_stats() (NEW)
    ├── handle_log_cleanup() (NEW)
    ├── startup() (NEW)
    └── cleanup() (NEW)
```

### Security Considerations
1. **Path Validation**: All file operations validate paths before execution
2. **Directory Restrictions**: Only 4 directories accessible (/app/k8s-repo, /app/runbooks, /app/work, /app/logs)
3. **Delete Confirmation**: Requires explicit confirmation flag to delete files
4. **No Directory Deletion**: Only files can be deleted, not directories
5. **Read-Only Logs**: Logs directory readable but write operations should be carefully controlled

---

## Testing the Features

### Test MCP Call Logging
```bash
# Make some MCP calls
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

# Check log stats
curl http://localhost:8080/logs/mcp/stats

# View log file
cat /app/logs/mcp-calls/mcp-calls-$(date +%Y-%m-%d).jsonl
```

### Test File Operations
```bash
# Create test file
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "file_write", "arguments": {"path": "/app/work/test.txt", "content": "Hello World"}}}'

# Read it back
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "file_read", "arguments": {"path": "/app/work/test.txt"}}}'

# Test security (should fail)
curl -X POST http://localhost:8080/mcp/http \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "file_read", "arguments": {"path": "/etc/passwd"}}}'
```

---

## Summary

Both features are now fully integrated into the MCP server:

✅ **MCP Call Logging**: All calls logged automatically to daily files with 5-day retention
✅ **File Operations**: 6 new tools for secure file management in allowed directories
✅ **Security**: Path validation and access controls
✅ **Automation**: Background cleanup task for old logs
✅ **Documentation**: CLAUDE.md updated with all new features
✅ **Testing**: Manual and automated testing support

The server is ready to use these features immediately after restart!
