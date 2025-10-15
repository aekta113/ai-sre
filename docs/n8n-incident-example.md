# N8N Incident Response Example

## 🚨 Real Incident Scenario: Pod CrashLoopBackOff

### **N8N Agent Node Prompt**

```
You are an AI SRE agent responding to a critical production incident.

INCIDENT ALERT: 
- Service: web-frontend
- Issue: Pod CrashLoopBackOff in production namespace
- Severity: High
- Users Affected: ~500 concurrent users
- Impact: 503 errors on main website

IMMEDIATE RESPONSE REQUIRED:

1. **ASSESSMENT (2 minutes)**:
   - Use health_check to verify MCP server connectivity
   - Use kubectl_get to check pod status in production namespace
   - Identify pods in CrashLoopBackOff state
   - Use kubectl_describe to get detailed pod information

2. **DIAGNOSIS (3 minutes)**:
   - Use kubectl_logs to examine pod logs for error messages
   - Look for OOMKilled, configuration errors, or dependency failures
   - Check resource limits and usage patterns
   - Identify the root cause

3. **RESOLUTION (5 minutes)**:
   - Apply appropriate fix based on diagnosis:
     * Memory issues: Increase memory limits using kubectl patch
     * Config errors: Fix configuration and restart
     * Dependency issues: Check service dependencies
   - Use kubectl rollout restart to apply changes
   - Monitor pod startup and health

4. **VERIFICATION (2 minutes)**:
   - Use kubectl_get to verify pods are running
   - Use health_check to confirm service is responding
   - Monitor for 2 minutes to ensure stability

5. **DOCUMENTATION**:
   - Use git_status to check repository state
   - Use git_commit with message: "fix: resolve web-frontend pod crashloop - [root-cause]"
   - Use git_push to deploy any configuration changes
   - Document incident in runbook for future reference

CRITICAL: Prioritize service restoration while maintaining system stability.
```

### **Expected MCP Tool Sequence**

```json
[
  {
    "step": 1,
    "tool": "health_check",
    "purpose": "Verify MCP server connectivity",
    "arguments": {}
  },
  {
    "step": 2,
    "tool": "kubectl_get",
    "purpose": "Check pod status in production",
    "arguments": {
      "resource": "pods",
      "namespace": "production",
      "output": "json"
    }
  },
  {
    "step": 3,
    "tool": "kubectl_describe",
    "purpose": "Get detailed pod information",
    "arguments": {
      "resource": "pod",
      "name": "web-frontend-7d4b8c9f6-x2k9m",
      "namespace": "production"
    }
  },
  {
    "step": 4,
    "tool": "kubectl_logs",
    "purpose": "Examine pod logs for errors",
    "arguments": {
      "pod": "web-frontend-7d4b8c9f6-x2k9m",
      "namespace": "production",
      "lines": 100
    }
  },
  {
    "step": 5,
    "tool": "cli_tool",
    "purpose": "Apply memory limit fix",
    "arguments": {
      "tool": "kubectl",
      "args": [
        "patch", 
        "deployment", 
        "web-frontend", 
        "-p", 
        "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"web-frontend\",\"resources\":{\"limits\":{\"memory\":\"512Mi\"}}}]}}}}"
      ]
    }
  },
  {
    "step": 6,
    "tool": "cli_tool",
    "purpose": "Restart deployment",
    "arguments": {
      "tool": "kubectl",
      "args": ["rollout", "restart", "deployment/web-frontend"]
    }
  },
  {
    "step": 7,
    "tool": "git_status",
    "purpose": "Check repository state",
    "arguments": {}
  },
  {
    "step": 8,
    "tool": "git_commit",
    "purpose": "Commit configuration changes",
    "arguments": {
      "message": "fix: increase memory limits for web-frontend pods due to OOMKilled events",
      "files": ["manifests/web-frontend-deployment.yaml"],
      "all": false
    }
  },
  {
    "step": 9,
    "tool": "git_push",
    "purpose": "Deploy changes",
    "arguments": {
      "branch": "main"
    }
  },
  {
    "step": 10,
    "tool": "health_check",
    "purpose": "Verify service recovery",
    "arguments": {
      "service": "web-frontend"
    }
  }
]
```

### **Learning Integration Prompt**

```
After resolving the incident, update the knowledge base with learnings:

LEARNING TASK: Document web-frontend memory pressure incident

1. **Incident Documentation**:
   - Create incident file: 2025-10-15-web-frontend-memory-pressure.md
   - Document root cause: Memory limit too low (256Mi) for application workload
   - Record resolution: Increased memory limit to 512Mi
   - Note resolution time: 12 minutes

2. **Pattern Recognition**:
   - Check if this matches existing memory-pressure pattern
   - Update pattern frequency and success metrics
   - Identify if this is a new variation of existing pattern

3. **Runbook Updates**:
   - Update memory-pressure pattern with web-frontend specifics
   - Add prevention measures for similar applications
   - Include memory limit calculation guidelines

4. **Automation Opportunities**:
   - Suggest automated memory limit adjustment based on usage patterns
   - Propose monitoring alerts for memory usage trends
   - Recommend memory stress testing in CI/CD pipeline

5. **Repository Updates**:
   - Use git_commit with message: "learn: document web-frontend memory incident and update memory-pressure pattern"
   - Update runbook metrics and success rates
   - Add new prevention measures to knowledge base

KEY LEARNINGS TO CAPTURE:
- Memory limits should be set based on actual usage patterns, not estimates
- Web applications with image processing need higher memory limits
- Proactive monitoring of memory usage trends can prevent incidents
- Memory limit increases should include 30% safety margin
```

### **Expected Learning Output**

```json
{
  "incident_learnings": {
    "root_cause": "Memory limit too low for application workload",
    "resolution": "Increased memory limit from 256Mi to 512Mi",
    "resolution_time": "12 minutes",
    "success_rate": "100%",
    "prevention_measures": [
      "Monitor memory usage trends proactively",
      "Set memory limits based on actual usage + 30% margin",
      "Include memory stress testing in CI/CD",
      "Alert on memory usage approaching limits"
    ]
  },
  "pattern_updates": {
    "pattern_name": "memory-pressure",
    "frequency_increase": 1,
    "success_rate": "96%",
    "new_variations": ["web-application-memory-pressure"]
  },
  "automation_opportunities": [
    "Automated memory limit adjustment based on usage patterns",
    "Memory usage trend monitoring and alerting",
    "Memory stress testing automation"
  ],
  "runbook_changes": [
    "Updated memory-pressure pattern with web-frontend specifics",
    "Added memory limit calculation guidelines",
    "Included prevention measures for web applications"
  ]
}
```

### **N8N Workflow Integration**

```json
{
  "workflow": {
    "trigger": "AlertManager webhook",
    "nodes": [
      {
        "name": "AI SRE Agent",
        "type": "Agent",
        "prompt": "[Incident Response Prompt Above]",
        "mcp_tools": [
          "health_check",
          "kubectl_get", 
          "kubectl_describe",
          "kubectl_logs",
          "cli_tool",
          "git_status",
          "git_commit",
          "git_push"
        ]
      },
      {
        "name": "Learning Agent",
        "type": "Agent", 
        "prompt": "[Learning Integration Prompt Above]",
        "mcp_tools": [
          "git_status",
          "git_commit",
          "git_push",
          "cli_tool"
        ]
      },
      {
        "name": "Notification",
        "type": "Telegram",
        "message": "Incident resolved: {incident_summary}"
      }
    ]
  }
}
```

### **Success Metrics**

- **Resolution Time**: 12 minutes (target: <15 minutes)
- **Service Uptime**: Restored within 5 minutes
- **User Impact**: Minimal (503 errors resolved)
- **Knowledge Update**: Pattern updated, prevention measures added
- **Automation**: New automation opportunities identified
- **Documentation**: Complete incident and learning documentation

This example demonstrates a complete incident response cycle with learning integration, showing how N8N Agent nodes can effectively use the AI SRE MCP tools to resolve incidents and continuously improve the system.
