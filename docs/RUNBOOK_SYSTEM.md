# AI SRE Runbook System Documentation

## Overview

The AI SRE runbook system provides a comprehensive knowledge base for automated incident response and remediation. It combines static runbooks with dynamic AI learning capabilities to create an intelligent, self-improving incident response system.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Static        │    │   Dynamic        │    │   AI Learning   │
│   Runbooks      │    │   Runbooks       │    │   System        │
│                 │    │                  │    │                 │
│ • agent.md      │    │ • Generated      │    │ • Pattern       │
│ • Templates     │    │ • Auto-updated   │    │   Recognition   │
│ • Best Practices│    │ • Incident-based │    │ • Trend         │
│                 │    │ • Real-time      │    │   Analysis      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MCP Server    │
                    │   Runbook API   │
                    │                 │
                    │ • Search        │
                    │ • Execute       │
                    │ • Learn         │
                    │ • Update        │
                    └─────────────────┘
```

## Runbook Storage Structure

### Persistent Storage Layout

```
/app/runbooks/
├── static/                    # Static runbooks (agent.md, templates)
│   ├── agent.md              # Main knowledge base
│   ├── templates/            # Runbook templates
│   │   ├── incident.md       # Incident response template
│   │   ├── remediation.md    # Remediation template
│   │   └── postmortem.md     # Postmortem template
│   └── best-practices/       # Best practices documentation
├── dynamic/                   # AI-generated runbooks
│   ├── incidents/            # Incident-specific runbooks
│   │   ├── 2024-01-15-pod-crash.md
│   │   ├── 2024-01-16-network-issue.md
│   │   └── ...
│   ├── patterns/             # Learned patterns
│   │   ├── memory-pressure.md
│   │   ├── disk-space-low.md
│   │   └── ...
│   └── resolutions/          # Successful resolutions
│       ├── auto-generated/   # AI-generated resolutions
│       └── manual/           # Manually added resolutions
├── cache/                    # Cached runbook data
│   ├── search-index.json     # Search index
│   ├── patterns.json         # Pattern data
│   └── metrics.json          # Usage metrics
└── backups/                  # Backup storage
    ├── daily/                # Daily backups
    ├── weekly/               # Weekly backups
    └── monthly/              # Monthly backups
```

## Runbook Types

### 1. Static Runbooks (`agent.md`)

**Purpose**: Core knowledge base with standard incident response procedures.

**Structure**:
```markdown
# AI SRE Knowledge Base

## 🤖 AI Agent Capabilities
[Agent capabilities and features]

## 📊 Alert Categories
[Alert type definitions]

## Alert: [AlertName]
**Description**: [Alert description]
**Diagnosis Steps**: [Step-by-step diagnosis]
**Common Causes & Fixes**: [Causes and solutions]

## 🤖 AI Learning Section
[AI learning and pattern recognition]

## 📋 Best Practices
[Best practices organized by category]
```

**Features**:
- Manual updates by SRE team
- Version controlled in Git
- Template-based structure
- Comprehensive coverage of common issues

### 2. Dynamic Runbooks

**Purpose**: Auto-generated runbooks based on actual incidents and AI learning.

**Generation Triggers**:
- New incident types encountered
- Successful remediation patterns
- Recurring issue patterns
- Performance optimization insights

**Structure**:
```markdown
# Incident: [Incident ID] - [Brief Description]
**Date**: [Timestamp]
**Severity**: [Critical/High/Medium/Low]
**Duration**: [Resolution time]

## Incident Details
- **Trigger**: [What caused the incident]
- **Symptoms**: [Observable symptoms]
- **Impact**: [Service impact]

## Diagnosis Process
1. [Diagnosis step 1]
2. [Diagnosis step 2]
...

## Resolution Steps
1. [Resolution step 1]
2. [Resolution step 2]
...

## Lessons Learned
- [Key learnings]
- [Prevention measures]

## AI Insights
- **Pattern**: [Identified pattern]
- **Confidence**: [AI confidence score]
- **Similar Incidents**: [References to similar incidents]
```

### 3. Template Runbooks

**Purpose**: Reusable templates for common incident types.

**Templates**:
- **Incident Response**: Standard incident response flow
- **Remediation**: Common remediation procedures
- **Postmortem**: Post-incident analysis template
- **Capacity Planning**: Resource planning procedures

## Runbook API Endpoints

### Search and Retrieval

```http
GET /runbooks/search?q={query}&type={type}&severity={severity}
```

**Parameters**:
- `q`: Search query
- `type`: Runbook type (static, dynamic, template)
- `severity`: Incident severity filter
- `limit`: Maximum results (default: 10)

**Response**:
```json
{
  "results": [
    {
      "id": "pod-crash-001",
      "title": "Pod Crash Loop BackOff",
      "type": "static",
      "severity": "high",
      "relevance_score": 0.95,
      "summary": "Comprehensive guide for diagnosing and fixing pod crash issues",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "search_time": "0.023s"
}
```

### Execute Runbook

```http
POST /runbooks/execute
```

**Request**:
```json
{
  "runbook_id": "pod-crash-001",
  "context": {
    "namespace": "production",
    "pod_name": "my-app-7d4b8c9f-x2k9m",
    "cluster": "prod-cluster"
  },
  "parameters": {
    "auto_execute": false,
    "dry_run": true
  }
}
```

**Response**:
```json
{
  "execution_id": "exec-12345",
  "status": "completed",
  "steps": [
    {
      "step": 1,
      "description": "Get pod status",
      "command": "kubectl get pod my-app-7d4b8c9f-x2k9m -n production",
      "result": "success",
      "output": "Pod is in CrashLoopBackOff state"
    }
  ],
  "recommendations": [
    "Check pod logs for error messages",
    "Verify resource limits",
    "Check recent deployments"
  ]
}
```

### Create/Update Runbook

```http
POST /runbooks/create
PUT /runbooks/{id}
```

**Request**:
```json
{
  "title": "New Incident Response",
  "type": "dynamic",
  "severity": "high",
  "content": "# New Runbook\n\n## Steps\n1. First step\n2. Second step",
  "tags": ["kubernetes", "pods", "crash"],
  "metadata": {
    "incident_id": "INC-12345",
    "resolved_by": "ai-agent",
    "confidence": 0.85
  }
}
```

### AI Learning Integration

```http
POST /runbooks/learn
GET /runbooks/patterns
```

**Learn from Incident**:
```json
{
  "incident_data": {
    "type": "pod_crash",
    "diagnosis": ["memory_limit_exceeded"],
    "resolution": ["increase_memory_limit"],
    "success": true,
    "duration": "5m"
  },
  "context": {
    "namespace": "production",
    "pod_type": "web-app"
  }
}
```

**Response**:
```json
{
  "pattern_detected": true,
  "pattern_id": "memory-pressure-web-app",
  "confidence": 0.92,
  "new_runbook_created": true,
  "runbook_id": "memory-pressure-001",
  "recommendations": [
    "Add proactive monitoring for memory usage",
    "Implement auto-scaling for memory-intensive pods"
  ]
}
```

## Runbook Execution Engine

### Execution Modes

1. **Manual Execution**: Human-guided execution with AI assistance
2. **Semi-Automated**: AI suggests steps, human approval required
3. **Fully Automated**: AI executes steps automatically (for low-risk operations)

### Execution Context

```json
{
  "cluster_info": {
    "name": "prod-cluster",
    "version": "1.28.0",
    "provider": "AWS"
  },
  "namespace": "production",
  "resource": {
    "type": "pod",
    "name": "my-app-7d4b8c9f-x2k9m"
  },
  "incident": {
    "id": "INC-12345",
    "type": "pod_crash",
    "severity": "high"
  },
  "user": {
    "id": "ai-agent",
    "role": "automated"
  }
}
```

### Step Execution

Each runbook step is executed with:
- **Pre-checks**: Validate prerequisites
- **Command Execution**: Run diagnostic/remediation commands
- **Result Analysis**: Analyze command output
- **Decision Point**: Determine next steps based on results
- **Logging**: Record execution details

## AI Learning System

### Pattern Recognition

The AI system learns from:
- **Successful Resolutions**: What worked and why
- **Failed Attempts**: What didn't work and why
- **Common Patterns**: Recurring issues and solutions
- **Performance Metrics**: Resolution time and success rates

### Learning Data Structure

```json
{
  "incident_patterns": {
    "memory_pressure": {
      "frequency": 15,
      "avg_resolution_time": "3m",
      "success_rate": 0.95,
      "common_solutions": [
        "increase_memory_limit",
        "restart_pod",
        "scale_horizontally"
      ],
      "triggers": [
        "memory_usage > 90%",
        "oom_killed_events",
        "pod_restart_count > 5"
      ]
    }
  },
  "resolution_effectiveness": {
    "increase_memory_limit": {
      "success_rate": 0.85,
      "avg_time": "2m",
      "side_effects": ["increased_cost"]
    }
  }
}
```

### Auto-Generated Insights

The system automatically generates:
- **Proactive Alerts**: Based on learned patterns
- **Optimization Suggestions**: Resource allocation improvements
- **Prevention Measures**: Actions to prevent recurring issues
- **Workflow Enhancements**: Improvements to existing runbooks

## Integration with N8N

### N8N Workflow Integration

```json
{
  "trigger": "alert_received",
  "steps": [
    {
      "type": "http_request",
      "url": "http://ai-sre:8080/runbooks/search",
      "params": {
        "q": "{{$json.alert_type}}",
        "severity": "{{$json.severity}}"
      }
    },
    {
      "type": "http_request",
      "url": "http://ai-sre:8080/runbooks/execute",
      "params": {
        "runbook_id": "{{$json.runbook_id}}",
        "context": "{{$json.incident_context}}"
      }
    },
    {
      "type": "http_request",
      "url": "http://ai-sre:8080/runbooks/learn",
      "params": {
        "incident_data": "{{$json.resolution_data}}"
      }
    }
  ]
}
```

### Webhook Integration

```http
POST /webhooks/n8n/incident
Content-Type: application/json

{
  "alert": {
    "type": "pod_crash",
    "severity": "high",
    "namespace": "production",
    "resource": "my-app-pod"
  },
  "context": {
    "cluster": "prod-cluster",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Best Practices

### Runbook Creation

1. **Start with Templates**: Use existing templates as starting points
2. **Include Context**: Provide clear context and prerequisites
3. **Test Thoroughly**: Validate runbooks in non-production environments
4. **Version Control**: Track changes and maintain history
5. **Regular Updates**: Keep runbooks current with system changes

### AI Learning

1. **Quality Data**: Ensure high-quality incident data for learning
2. **Human Oversight**: Review AI-generated runbooks before deployment
3. **Feedback Loop**: Provide feedback on AI suggestions
4. **Continuous Improvement**: Regularly refine learning algorithms

### Storage Management

1. **Backup Strategy**: Regular backups of runbook data
2. **Retention Policy**: Implement appropriate retention periods
3. **Access Control**: Secure access to sensitive runbook data
4. **Monitoring**: Monitor storage usage and performance

## Monitoring and Metrics

### Key Metrics

- **Runbook Usage**: Most frequently used runbooks
- **Success Rate**: Resolution success rates by runbook type
- **Resolution Time**: Average time to resolution
- **AI Accuracy**: AI learning accuracy and confidence scores
- **Storage Usage**: Runbook storage utilization

### Dashboards

- **Runbook Performance**: Success rates and resolution times
- **AI Learning Progress**: Pattern recognition and learning metrics
- **Storage Health**: Storage usage and backup status
- **Incident Trends**: Incident frequency and types

## Troubleshooting

### Common Issues

1. **Runbook Not Found**: Check search parameters and runbook availability
2. **Execution Failures**: Verify permissions and cluster connectivity
3. **AI Learning Issues**: Check incident data quality and learning algorithms
4. **Storage Problems**: Monitor disk space and backup processes

### Debug Commands

```bash
# Check runbook storage
curl http://localhost:8080/runbooks/health

# View AI learning status
curl http://localhost:8080/runbooks/patterns

# Check storage usage
curl http://localhost:8080/storage/usage

# View recent executions
curl http://localhost:8080/runbooks/executions?limit=10
```
