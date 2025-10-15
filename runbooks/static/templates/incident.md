# Incident Response Template

## 🚨 Incident Information

**Incident ID**: `INCIDENT-YYYY-MM-DD-HHMM`
**Severity**: `[Critical/High/Medium/Low]`
**Status**: `[Open/Investigating/Resolved/Closed]`
**Reported By**: `[Name/System]`
**Reported At**: `[Timestamp]`
**Resolved At**: `[Timestamp]`
**Duration**: `[Resolution time]`

## 📋 Incident Summary

**Title**: `[Brief description of the incident]`

**Description**: 
```
[Detailed description of what happened, including symptoms and impact]
```

**Affected Services**: 
- `[Service 1]`
- `[Service 2]`
- `[Service 3]`

**Impact**: 
- **Users Affected**: `[Number or percentage]`
- **Business Impact**: `[Description of business impact]`
- **Geographic Impact**: `[Affected regions/locations]`

## 🔍 Investigation

### Initial Symptoms
```
[What was first observed - error messages, alerts, user reports, etc.]
```

### Timeline
| Time | Event | Action Taken |
|------|-------|--------------|
| `[HH:MM]` | `[Event description]` | `[Action taken]` |
| `[HH:MM]` | `[Event description]` | `[Action taken]` |
| `[HH:MM]` | `[Event description]` | `[Action taken]` |

### Diagnostic Commands Executed
```bash
# MCP Commands used during investigation
kubectl get pods --all-namespaces
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

### Root Cause Analysis
```
[Detailed analysis of what caused the incident]
```

**Primary Cause**: `[Main cause]`
**Contributing Factors**: 
- `[Factor 1]`
- `[Factor 2]`
- `[Factor 3]`

## 🛠️ Resolution

### Resolution Steps
1. **Step 1**: `[Action taken]`
   - **Command**: `[MCP command or manual action]`
   - **Result**: `[Outcome]`

2. **Step 2**: `[Action taken]`
   - **Command**: `[MCP command or manual action]`
   - **Result**: `[Outcome]`

3. **Step 3**: `[Action taken]`
   - **Command**: `[MCP command or manual action]`
   - **Result**: `[Outcome]`

### Verification Steps
- [ ] `[Verification step 1]`
- [ ] `[Verification step 2]`
- [ ] `[Verification step 3]`
- [ ] `[Service is fully operational]`
- [ ] `[All monitoring is green]`

### Commands Used for Resolution
```json
{
  "resolution_commands": [
    {
      "tool": "kubectl_get",
      "arguments": {
        "resource": "pods",
        "namespace": "<namespace>"
      }
    },
    {
      "tool": "kubectl_describe",
      "arguments": {
        "resource": "pod",
        "name": "<pod-name>",
        "namespace": "<namespace>"
      }
    },
    {
      "tool": "kubectl_logs",
      "arguments": {
        "pod": "<pod-name>",
        "namespace": "<namespace>",
        "lines": 100
      }
    }
  ]
}
```

## 📊 Impact Assessment

### Technical Impact
- **Service Downtime**: `[Duration]`
- **Data Loss**: `[Yes/No - Description if yes]`
- **Performance Impact**: `[Description]`
- **Security Impact**: `[Any security implications]`

### Business Impact
- **Revenue Impact**: `[Estimated financial impact]`
- **Customer Impact**: `[Number of customers affected]`
- **Reputation Impact**: `[Any reputation damage]`
- **Compliance Impact**: `[Any compliance issues]`

### Operational Impact
- **Team Resources**: `[Team members involved]`
- **External Dependencies**: `[Any external services/teams involved]`
- **Escalation Required**: `[Yes/No - Details if yes]`

## 📚 Lessons Learned

### What Went Well
- `[Positive aspect 1]`
- `[Positive aspect 2]`
- `[Positive aspect 3]`

### What Could Be Improved
- `[Improvement area 1]`
- `[Improvement area 2]`
- `[Improvement area 3]`

### Prevention Measures
- `[Prevention measure 1]`
- `[Prevention measure 2]`
- `[Prevention measure 3]`

### Process Improvements
- `[Process improvement 1]`
- `[Process improvement 2]`
- `[Process improvement 3]`

## 🎯 Action Items

### Immediate Actions (Next 24 hours)
- [ ] `[Action item 1]`
- [ ] `[Action item 2]`
- [ ] `[Action item 3]`

### Short-term Actions (Next week)
- [ ] `[Action item 1]`
- [ ] `[Action item 2]`
- [ ] `[Action item 3]`

### Long-term Actions (Next month)
- [ ] `[Action item 1]`
- [ ] `[Action item 2]`
- [ ] `[Action item 3]`

## 📈 Metrics

### Resolution Metrics
- **Time to Detection**: `[Duration]`
- **Time to Investigation**: `[Duration]`
- **Time to Resolution**: `[Duration]`
- **Total Downtime**: `[Duration]`

### Automation Metrics
- **Automated Steps**: `[Number]`
- **Manual Steps**: `[Number]`
- **AI Suggestions Used**: `[Number]`
- **Human Override Required**: `[Yes/No]`

## 🔄 Follow-up

### Communication
- [ ] `[Stakeholder 1 notified]`
- [ ] `[Stakeholder 2 notified]`
- [ ] `[Customer communication sent]`
- [ ] `[Internal team debrief completed]`

### Documentation Updates
- [ ] `[Runbook updated]`
- [ ] `[Monitoring rules updated]`
- [ ] `[Alerting thresholds adjusted]`
- [ ] `[Process documentation updated]`

### Training
- [ ] `[Team training scheduled]`
- [ ] `[New procedures documented]`
- [ ] `[Best practices shared]`

---

**Incident Commander**: `[Name]`
**Technical Lead**: `[Name]`
**Communications Lead**: `[Name]`
**Post-Mortem Scheduled**: `[Date/Time]`

*Template Version: 1.0*
*Last Updated: 2025-10-15*
