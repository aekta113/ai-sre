# Post-Mortem Template

## 🚨 Incident Summary

**Incident ID**: `INCIDENT-YYYY-MM-DD-HHMM`
**Title**: `[Incident title]`
**Date**: `[Incident date]`
**Duration**: `[Total duration]`
**Severity**: `[Critical/High/Medium/Low]`
**Status**: `[Resolved/Closed]`

## 📊 Executive Summary

**What Happened**: 
```
[Brief 2-3 sentence summary of the incident]
```

**Impact**:
- **Users Affected**: `[Number or percentage]`
- **Downtime**: `[Duration]`
- **Business Impact**: `[Financial or operational impact]`
- **Services Affected**: `[List of affected services]`

**Root Cause**: 
```
[Brief description of the root cause]
```

**Resolution**: 
```
[Brief description of how it was resolved]
```

## 🔍 Incident Timeline

### Discovery Phase
| Time | Event | Action Taken |
|------|-------|--------------|
| `[HH:MM]` | `[First detection/alert]` | `[Initial response]` |
| `[HH:MM]` | `[Investigation started]` | `[Investigation actions]` |
| `[HH:MM]` | `[Root cause identified]` | `[Analysis actions]` |

### Response Phase
| Time | Event | Action Taken |
|------|-------|--------------|
| `[HH:MM]` | `[Response initiated]` | `[Response actions]` |
| `[HH:MM]` | `[Fix implemented]` | `[Implementation details]` |
| `[HH:MM]` | `[Service restored]` | `[Verification actions]` |

### Recovery Phase
| Time | Event | Action Taken |
|------|-------|--------------|
| `[HH:MM]` | `[Monitoring stabilized]` | `[Monitoring actions]` |
| `[HH:MM]` | `[Full service confirmed]` | `[Final verification]` |
| `[HH:MM]` | `[Incident closed]` | `[Documentation completed]` |

## 🔍 Root Cause Analysis

### Primary Cause
```
[Detailed explanation of the primary cause]
```

### Contributing Factors
1. **Factor 1**: `[Description and why it contributed]`
2. **Factor 2**: `[Description and why it contributed]`
3. **Factor 3**: `[Description and why it contributed]`

### Evidence
```bash
# Logs, metrics, and diagnostic information
[Relevant log excerpts]
[Error messages]
[Monitoring data]
```

### Why It Happened
- **Technical Reason**: `[Technical explanation]`
- **Process Reason**: `[Process or procedure gaps]`
- **Human Reason**: `[Human factors, if any]`
- **System Reason**: `[System or infrastructure issues]`

## 🛠️ Resolution Details

### What Was Done
1. **Step 1**: `[Action taken]`
   - **Tool Used**: `[MCP tool or manual action]`
   - **Command**: 
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "<tool-name>",
       "arguments": {
         "<param1>": "<value1>"
       }
     }
   }
   ```
   - **Result**: `[Outcome]`

2. **Step 2**: `[Action taken]`
   - **Tool Used**: `[MCP tool or manual action]`
   - **Command**: 
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "<tool-name>",
       "arguments": {
         "<param1>": "<value1>"
       }
     }
   }
   ```
   - **Result**: `[Outcome]`

3. **Step 3**: `[Action taken]`
   - **Tool Used**: `[MCP tool or manual action]`
   - **Command**: 
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "<tool-name>",
       "arguments": {
         "<param1>": "<value1>"
       }
     }
   }
   ```
   - **Result**: `[Outcome]`

### Why It Worked
```
[Explanation of why the resolution was successful]
```

## 📈 Impact Analysis

### Technical Impact
- **Service Downtime**: `[Duration and affected services]`
- **Performance Degradation**: `[Metrics before/during/after]`
- **Data Loss**: `[Any data that was lost or corrupted]`
- **Security Impact**: `[Any security implications]`

### Business Impact
- **Revenue Loss**: `[Estimated financial impact]`
- **Customer Impact**: `[Number and type of affected customers]`
- **Reputation Impact**: `[Any reputation damage]`
- **Operational Impact**: `[Impact on business operations]`

### Team Impact
- **Resources Used**: `[Team members and time spent]`
- **External Dependencies**: `[Any external teams or services involved]`
- **Escalation Required**: `[Any escalations that were needed]`

## 📚 Lessons Learned

### What Went Well
1. **Detection**: `[What worked well in detection]`
2. **Response**: `[What worked well in response]`
3. **Communication**: `[What worked well in communication]`
4. **Resolution**: `[What worked well in resolution]`
5. **Teamwork**: `[What worked well in team coordination]`

### What Went Wrong
1. **Detection**: `[What didn't work well in detection]`
2. **Response**: `[What didn't work well in response]`
3. **Communication**: `[What didn't work well in communication]`
4. **Resolution**: `[What didn't work well in resolution]`
5. **Process**: `[What process issues occurred]`

### What We Learned
1. **Technical Insights**: `[New technical knowledge gained]`
2. **Process Insights**: `[Process improvements identified]`
3. **Tool Insights**: `[Tool or automation improvements needed]`
4. **Team Insights**: `[Team dynamics or coordination learnings]`

## 🎯 Action Items

### Immediate Actions (Next 24 hours)
- [ ] `[Action 1 - Owner: Name, Due: Date]`
- [ ] `[Action 2 - Owner: Name, Due: Date]`
- [ ] `[Action 3 - Owner: Name, Due: Date]`

### Short-term Actions (Next week)
- [ ] `[Action 1 - Owner: Name, Due: Date]`
- [ ] `[Action 2 - Owner: Name, Due: Date]`
- [ ] `[Action 3 - Owner: Name, Due: Date]`

### Medium-term Actions (Next month)
- [ ] `[Action 1 - Owner: Name, Due: Date]`
- [ ] `[Action 2 - Owner: Name, Due: Date]`
- [ ] `[Action 3 - Owner: Name, Due: Date]`

### Long-term Actions (Next quarter)
- [ ] `[Action 1 - Owner: Name, Due: Date]`
- [ ] `[Action 2 - Owner: Name, Due: Date]`
- [ ] `[Action 3 - Owner: Name, Due: Date]`

## 🛠️ Prevention Measures

### Technical Improvements
1. **Monitoring**: `[Monitoring improvements needed]`
2. **Alerting**: `[Alerting improvements needed]`
3. **Automation**: `[Automation improvements needed]`
4. **Infrastructure**: `[Infrastructure improvements needed]`
5. **Testing**: `[Testing improvements needed]`

### Process Improvements
1. **Incident Response**: `[Process improvements needed]`
2. **Communication**: `[Communication process improvements]`
3. **Documentation**: `[Documentation improvements needed]`
4. **Training**: `[Training improvements needed]`
5. **Escalation**: `[Escalation process improvements]`

### Tool Improvements
1. **MCP Tools**: `[MCP tool enhancements needed]`
2. **Monitoring Tools**: `[Monitoring tool improvements]`
3. **Communication Tools**: `[Communication tool improvements]`
4. **Documentation Tools**: `[Documentation tool improvements]`

## 📊 Metrics and KPIs

### Response Metrics
- **Time to Detection**: `[Duration]`
- **Time to Investigation**: `[Duration]`
- **Time to Resolution**: `[Duration]`
- **Total Downtime**: `[Duration]`

### Automation Metrics
- **Automated Steps**: `[Number and percentage]`
- **Manual Steps**: `[Number and percentage]`
- **AI Suggestions Used**: `[Number]`
- **Human Override Required**: `[Yes/No - Details if yes]`

### Quality Metrics
- **Customer Complaints**: `[Number]`
- **Internal Escalations**: `[Number]`
- **Process Deviations**: `[Number]`
- **Documentation Gaps**: `[Number]`

## 🔄 Follow-up Plan

### Review Schedule
- **1 Week Review**: `[Date] - Review immediate actions`
- **1 Month Review**: `[Date] - Review short-term actions`
- **3 Month Review**: `[Date] - Review long-term actions`
- **6 Month Review**: `[Date] - Comprehensive review`

### Success Criteria
- [ ] `[All immediate actions completed]`
- [ ] `[All short-term actions completed]`
- [ ] `[All medium-term actions completed]`
- [ ] `[All long-term actions completed]`
- [ ] `[No similar incidents occurred]`
- [ ] `[Process improvements implemented]`

### Communication Plan
- [ ] `[Stakeholder notification completed]`
- [ ] `[Team debrief conducted]`
- [ ] `[Lessons learned shared]`
- [ ] `[Best practices updated]`

## 📝 Appendix

### Related Documentation
- [Incident Response Log](#)
- [Technical Analysis Report](#)
- [Customer Impact Report](#)
- [Monitoring Data](#)

### Commands and Logs
```bash
# Key commands used during incident response
kubectl get pods --all-namespaces
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

### Team Members
**Incident Commander**: `[Name]`
**Technical Lead**: `[Name]`
**Communications Lead**: `[Name]`
**Post-Mortem Facilitator**: `[Name]`
**Scribe**: `[Name]`

### Attendees
- `[Name 1] - [Role]`
- `[Name 2] - [Role]`
- `[Name 3] - [Role]`

---

**Post-Mortem Completed By**: `[Name]`
**Date**: `[Date]`
**Next Review Date**: `[Date]`

*Template Version: 1.0*
*Last Updated: 2025-10-15*
