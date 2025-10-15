# AI SRE Knowledge Base

## 🤖 AI Agent Capabilities

The AI SRE agent can execute the following operations through MCP Protocol:

### Kubernetes Operations
- **kubectl_get**: Retrieve Kubernetes resources (pods, nodes, services, etc.)
- **kubectl_describe**: Get detailed information about specific resources
- **kubectl_logs**: Fetch pod logs for troubleshooting

### Git Operations
- **git_status**: Check repository status
- **git_pull**: Pull latest changes from repository
- **git_commit**: Commit changes with custom messages
- **git_push**: Push changes to remote repository

### GitOps Operations
- **flux_status**: Check Flux GitOps synchronization status

### CLI Tools
- **cli_tool**: Execute various CLI tools (jq, grep, sed, curl, cat, tree, find)

### System Health
- **health_check**: Check system and service health status

## 📊 Alert Categories

### 🔴 Critical Alerts
- **Pod CrashLoopBackOff**: Pod repeatedly failing to start
- **Node NotReady**: Kubernetes node is not ready
- **Disk Space Critical**: Disk space below 10%
- **Memory Pressure**: High memory usage causing evictions
- **Service Down**: Critical service unavailable

### 🟡 Warning Alerts
- **High CPU Usage**: CPU usage above 80%
- **High Memory Usage**: Memory usage above 80%
- **Pod Restart**: Pod restarted unexpectedly
- **Network Issues**: Network connectivity problems
- **Resource Limits**: Approaching resource limits

### 🟢 Info Alerts
- **Deployment Success**: Successful deployment
- **Scaling Events**: Auto-scaling triggered
- **Backup Complete**: Backup operation completed

## Alert: Pod CrashLoopBackOff

**Description**: A pod is repeatedly failing to start and crashing, causing a loop of restart attempts.

**Diagnosis Steps**:
1. Check pod status: `kubectl get pods -n <namespace>`
2. Describe the pod: `kubectl describe pod <pod-name> -n <namespace>`
3. Check pod logs: `kubectl logs <pod-name> -n <namespace> --previous`
4. Check events: `kubectl get events -n <namespace> --sort-by='.lastTimestamp'`
5. Verify image and configuration

**Common Causes & Fixes**:
- **Image Issues**: Update to correct image tag
- **Resource Limits**: Increase memory/CPU limits
- **Configuration Errors**: Fix environment variables or config maps
- **Dependencies**: Ensure required services are available
- **Permissions**: Check RBAC and security contexts

**MCP Commands**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "kubectl_describe",
    "arguments": {
      "resource": "pod",
      "name": "<pod-name>",
      "namespace": "<namespace>"
    }
  }
}
```

## Alert: Node NotReady

**Description**: A Kubernetes node is not ready, potentially affecting pod scheduling and availability.

**Diagnosis Steps**:
1. Check node status: `kubectl get nodes`
2. Describe the node: `kubectl describe node <node-name>`
3. Check node conditions and events
4. Verify kubelet status on the node
5. Check system resources (disk, memory, network)

**Common Causes & Fixes**:
- **Disk Pressure**: Free up disk space
- **Memory Pressure**: Free up memory or add more RAM
- **Network Issues**: Fix network connectivity
- **Kubelet Issues**: Restart kubelet service
- **Hardware Issues**: Check hardware health

## Alert: Disk Space Critical

**Description**: Disk space is critically low (below 10%), potentially causing system instability.

**Diagnosis Steps**:
1. Check disk usage: `df -h`
2. Find large files: `find / -type f -size +100M 2>/dev/null`
3. Check Docker space: `docker system df`
4. Check Kubernetes logs: `kubectl logs --previous`
5. Check for old images and containers

**Common Causes & Fixes**:
- **Log Files**: Rotate or compress log files
- **Docker Images**: Clean up unused images: `docker system prune -a`
- **Temporary Files**: Clean up /tmp and cache directories
- **Database Logs**: Archive old database logs
- **Application Logs**: Implement log rotation

**MCP Commands**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "cli_tool",
    "arguments": {
      "tool": "df",
      "args": ["-h"]
    }
  }
}
```

## Alert: Memory Pressure

**Description**: High memory usage is causing pod evictions and potential system instability.

**Diagnosis Steps**:
1. Check memory usage: `free -h`
2. Check pod resource usage: `kubectl top pods --all-namespaces`
3. Check node resource usage: `kubectl top nodes`
4. Check for memory leaks in applications
5. Review resource limits and requests

**Common Causes & Fixes**:
- **Resource Limits**: Increase memory limits for pods
- **Memory Leaks**: Restart applications with memory leaks
- **High Load**: Scale applications or add more nodes
- **Inefficient Applications**: Optimize application memory usage
- **System Processes**: Kill unnecessary system processes

## Alert: Service Down

**Description**: A critical service is unavailable or not responding to requests.

**Diagnosis Steps**:
1. Check service status: `kubectl get svc <service-name> -n <namespace>`
2. Check endpoints: `kubectl get endpoints <service-name> -n <namespace>`
3. Check pod status: `kubectl get pods -l app=<app-label> -n <namespace>`
4. Test service connectivity: `curl <service-url>`
5. Check ingress/load balancer configuration

**Common Causes & Fixes**:
- **Pod Issues**: Restart failing pods
- **Service Configuration**: Fix service selector or port configuration
- **Network Issues**: Check network policies and connectivity
- **DNS Issues**: Verify DNS resolution
- **Load Balancer**: Check ingress controller and load balancer

## 🤖 AI Learning Section

### Pattern Recognition
The AI system learns from successful incident resolutions and identifies patterns:

1. **Common Error Messages**: Maps error messages to solutions
2. **Resource Patterns**: Identifies resource-related issues
3. **Time Patterns**: Recognizes time-based issues (backups, scheduled tasks)
4. **Dependency Patterns**: Understands service dependencies
5. **Geographic Patterns**: Identifies location-specific issues

### Continuous Improvement
- **Success Tracking**: Records successful resolution steps
- **Failure Analysis**: Analyzes failed attempts to improve future responses
- **Feedback Integration**: Incorporates human feedback and corrections
- **Template Updates**: Automatically updates runbook templates based on new patterns

### Learning Metrics
- **Resolution Time**: Tracks average time to resolve incidents
- **Success Rate**: Monitors percentage of successful automated resolutions
- **Pattern Accuracy**: Measures accuracy of pattern recognition
- **Human Intervention**: Tracks frequency of human intervention needed

## 📋 Best Practices

### Incident Response
1. **Immediate Assessment**: Quickly assess severity and impact
2. **Communication**: Notify stakeholders immediately for critical issues
3. **Documentation**: Document all steps taken during resolution
4. **Post-Incident Review**: Conduct post-mortem for significant incidents
5. **Knowledge Sharing**: Update runbooks with new learnings

### Monitoring and Alerting
1. **Meaningful Alerts**: Set up alerts that indicate real problems
2. **Alert Fatigue Prevention**: Avoid too many low-priority alerts
3. **Escalation Procedures**: Define clear escalation paths
4. **Regular Review**: Periodically review and tune alerting rules
5. **Multi-Channel Notifications**: Use multiple notification channels

### Automation
1. **Start Small**: Begin with simple, low-risk automations
2. **Test Thoroughly**: Test automation in non-production environments
3. **Human Oversight**: Maintain human oversight for critical operations
4. **Rollback Plans**: Always have rollback procedures ready
5. **Documentation**: Document all automated procedures

### Security
1. **Least Privilege**: Use minimal required permissions
2. **Secure Communication**: Use secure channels for all communications
3. **Access Control**: Implement proper access controls and authentication
4. **Audit Logging**: Log all actions for audit purposes
5. **Regular Updates**: Keep all systems and tools updated

### Performance
1. **Resource Monitoring**: Continuously monitor resource usage
2. **Capacity Planning**: Plan for future capacity needs
3. **Optimization**: Regularly optimize system performance
4. **Load Testing**: Perform regular load testing
5. **Performance Baselines**: Establish and monitor performance baselines

## 🔧 Troubleshooting Quick Reference

### Quick Commands
```bash
# Check cluster status
kubectl get nodes
kubectl get pods --all-namespaces

# Check resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n <namespace> --previous
```

### Emergency Procedures
1. **Service Restart**: `kubectl rollout restart deployment/<deployment-name>`
2. **Pod Deletion**: `kubectl delete pod <pod-name> -n <namespace>`
3. **Scale Down/Up**: `kubectl scale deployment <deployment-name> --replicas=0`
4. **Resource Cleanup**: `kubectl delete pods --field-selector=status.phase=Succeeded`
5. **Network Reset**: Restart network components if needed

---

*Last Updated: 2025-10-15*
*Version: 1.0.0*
