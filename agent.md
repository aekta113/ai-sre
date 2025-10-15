# AI SRE Knowledge Base

This document serves as a comprehensive reference for AI-powered Site Reliability Engineering workflows. It contains runbooks for common Kubernetes, Flux, and infrastructure issues with their automated remediation steps.

## 🤖 AI Agent Capabilities

The AI SRE agent can automatically:
- Diagnose Kubernetes cluster issues
- Execute remediation workflows
- Update GitOps repositories
- Manage Flux deployments
- Monitor system health
- Learn from incident resolutions

## 📊 Alert Categories

## Alert: PodCrashLoopBackOff

**Description**: A pod is continuously crashing and restarting.

**Diagnosis Steps**:
1. Get pod status: `kubectl get pod <pod-name> -n <namespace>`
2. Check pod logs: `kubectl logs <pod-name> -n <namespace> --previous`
3. Describe pod: `kubectl describe pod <pod-name> -n <namespace>`
4. Check events: `kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name>`

**Common Causes & Fixes**:
- **Bad Image**: Roll back to previous version
  - `kubectl set image deployment/<deployment> <container>=<previous-image>`
- **Config Error**: Fix ConfigMap/Secret and restart pod
  - `kubectl delete pod <pod-name> -n <namespace>`
- **Resource Limits**: Increase memory/CPU limits
  - Update deployment manifest with higher limits
  - `kubectl apply -f updated-deployment.yaml`

## Alert: NodeNotReady

**Description**: A Kubernetes node is not in Ready state.

**Diagnosis Steps**:
1. Check node status: `kubectl get nodes`
2. Describe node: `kubectl describe node <node-name>`
3. Check kubelet logs on node
4. Check disk space on node

**Common Causes & Fixes**:
- **Disk Pressure**: Clean up disk space
  - SSH to node and clean docker images/logs
  - `docker system prune -a`
- **Memory Pressure**: Evict pods or add resources
  - `kubectl drain <node-name> --ignore-daemonsets`
- **Network Issue**: Check CNI plugin status
  - Restart CNI pods in kube-system

## Alert: HighMemoryUsage

**Description**: Service is using >90% of memory limit.

**Diagnosis Steps**:
1. Check pod metrics: `kubectl top pod <pod-name> -n <namespace>`
2. Check for memory leaks in logs
3. Review recent deployments

**Common Causes & Fixes**:
- **Memory Leak**: Restart pod for temporary relief
  - `kubectl rollout restart deployment/<deployment> -n <namespace>`
- **Under-provisioned**: Increase memory limits
  - Edit deployment: `kubectl edit deployment/<deployment> -n <namespace>`
  - Increase `resources.limits.memory`

## Alert: ServiceDown

**Description**: HTTP endpoint returning 5xx errors or not responding.

**Diagnosis Steps**:
1. Check service endpoints: `kubectl get endpoints <service> -n <namespace>`
2. Check pod status: `kubectl get pods -l <selector> -n <namespace>`
3. Test connectivity: `kubectl exec -it <pod> -- curl <service-url>`
4. Check ingress/load balancer status

**Common Causes & Fixes**:
- **All pods down**: Check deployment status and restart
  - `kubectl rollout status deployment/<deployment>`
  - `kubectl rollout restart deployment/<deployment>`
- **Bad deployment**: Roll back to previous version
  - `kubectl rollout undo deployment/<deployment>`
- **Service misconfiguration**: Verify service selector matches pod labels

## Alert: DiskSpaceLow

**Description**: Node or PVC running low on disk space.

**Diagnosis Steps**:
1. Check node disk usage: `kubectl describe node <node-name>`
2. Check PVC usage: `kubectl exec <pod> -- df -h`
3. Find large files: `kubectl exec <pod> -- du -sh /*`

**Common Causes & Fixes**:
- **Log accumulation**: Clear old logs
  - Exec into pod and clear logs
  - Implement log rotation
- **Cache/temp files**: Clean temporary data
  - Clear application cache
  - Remove old backup files
- **Insufficient PVC size**: Resize PVC
  - Edit PVC to increase size (if storage class supports it)

## Alert: DeploymentReplicasMismatch

**Description**: Deployment has fewer ready replicas than desired.

**Diagnosis Steps**:
1. Check deployment status: `kubectl get deployment <name> -n <namespace>`
2. Check replica set: `kubectl get rs -n <namespace>`
3. Check pods: `kubectl get pods -n <namespace> -l <selector>`
4. Check HPA if applicable: `kubectl get hpa -n <namespace>`

**Common Causes & Fixes**:
- **Insufficient resources**: Scale down or add nodes
  - `kubectl scale deployment/<name> --replicas=<lower-number>`
- **Image pull errors**: Fix registry credentials
  - Check imagePullSecrets
- **Failing readiness probes**: Adjust probe settings or fix application

## Alert: CertificateExpiringSoon

**Description**: TLS certificate will expire within 7 days.

**Diagnosis Steps**:
1. Check certificate: `kubectl get certificate <name> -n <namespace>`
2. Check cert-manager logs
3. Verify DNS challenges if using Let's Encrypt

**Common Causes & Fixes**:
- **Cert-manager issue**: Restart cert-manager
  - `kubectl rollout restart deployment/cert-manager -n cert-manager`
- **DNS challenge failed**: Verify DNS records
- **Manual cert**: Update certificate secret
  - `kubectl create secret tls <name> --cert=<cert> --key=<key> --dry-run=client -o yaml | kubectl apply -f -`

## Alert: FluxReconciliationFailed

**Description**: Flux GitOps reconciliation has failed for a source or workload.

**Diagnosis Steps**:
1. Check Flux sources: `flux get sources all -A`
2. Check Flux workloads: `flux get kustomizations -A`
3. Check Flux events: `flux get events -A`
4. Check Git repository connectivity

**Common Causes & Fixes**:
- **Git authentication**: Update Git credentials
  - `flux create secret git <name> --url=<repo> --username=<user> --password=<token>`
- **Branch/Path issues**: Verify repository path exists
  - Check Git repository structure
- **Resource conflicts**: Resolve Kubernetes resource conflicts
  - `kubectl get events -A --sort-by=.metadata.creationTimestamp`

## Alert: FluxSourceNotReady

**Description**: Flux Git source is not ready or has sync issues.

**Diagnosis Steps**:
1. Check source status: `flux get sources git -A`
2. Check source events: `flux get events --kind GitRepository -A`
3. Verify repository access and permissions

**Common Causes & Fixes**:
- **Network issues**: Check cluster network connectivity
- **Authentication**: Verify Git credentials are valid
- **Repository moved**: Update source URL if repository was moved

## Alert: JobFailed

**Description**: A Kubernetes Job has failed.

**Diagnosis Steps**:
1. Check job status: `kubectl get job <job-name> -n <namespace>`
2. Check pod logs: `kubectl logs job/<job-name> -n <namespace>`
3. Check job events: `kubectl describe job <job-name> -n <namespace>`

**Common Causes & Fixes**:
- **Transient error**: Retry the job
  - Delete and recreate: `kubectl delete job <job-name> && kubectl apply -f job.yaml`
- **Configuration error**: Fix job spec and rerun
- **Resource constraints**: Increase resources or adjust parallelism

## 🤖 AI Learning Section

> This section is automatically updated by the AI agent when new issues are resolved and patterns are learned

### Recent Resolutions

<!-- New resolutions will be added here by the AI agent -->

### Pattern Recognition

The AI agent learns from:
- Successful remediation workflows
- Common failure patterns
- Resource usage trends
- GitOps reconciliation issues
- Performance bottlenecks

### Auto-Generated Insights

- **Trend Analysis**: Identifies recurring issues across clusters
- **Predictive Alerts**: Proactive monitoring based on learned patterns
- **Optimization Suggestions**: Resource allocation and performance improvements
- **Workflow Enhancements**: Continuous improvement of remediation procedures

## 📋 Best Practices

### 🚨 Incident Response
1. **Always check logs first** - Most issues are evident in logs
2. **Verify recent changes** - Check Git history for recent deployments
3. **Test in staging first** - If possible, reproduce and fix in staging
4. **Document new issues** - Update this knowledge base with new patterns
5. **Use dry-run** - Test kubectl commands with --dry-run when possible
6. **Keep audit trail** - Log all remediation actions with timestamps

### 🔄 GitOps & Flux
7. **Source of Truth** - Always use Git repository as the source of truth
8. **Atomic Changes** - Make atomic commits for easier rollbacks
9. **Automated Testing** - Use CI/CD pipelines for validation
10. **Immutable Infrastructure** - Never make manual changes to running systems
11. **Monitoring Sync** - Monitor Flux reconciliation status continuously
12. **Secret Management** - Use proper secret management (SOPS, Sealed Secrets)

### 🏗️ Kubernetes Operations
13. **Resource Limits** - Always set resource requests and limits
14. **Health Checks** - Implement proper liveness and readiness probes
15. **Namespace Isolation** - Use namespaces for logical separation
16. **RBAC** - Implement proper role-based access control
17. **Network Policies** - Use network policies for security
18. **Backup Strategy** - Regular backups of critical data and configurations

### 📊 Monitoring & Observability
19. **Comprehensive Metrics** - Monitor application and infrastructure metrics
20. **Log Aggregation** - Centralized logging for easier troubleshooting
21. **Distributed Tracing** - Track requests across microservices
22. **Alert Fatigue** - Avoid over-alerting, focus on actionable alerts
23. **SLI/SLO Definition** - Define clear service level indicators and objectives
24. **Incident Postmortems** - Learn from incidents to prevent recurrence

## 🔧 AI Agent Configuration

### Environment Variables
```bash
# Kubernetes Configuration
KUBECONFIG_PATH=/path/to/kubeconfig
KUBE_NAMESPACE=default

# Flux Configuration  
FLUX_NAMESPACE=flux-system
GIT_REPOSITORY=https://github.com/org/repo

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# AI Learning
ENABLE_LEARNING=true
PATTERN_RECOGNITION=true
```

### MCP Server Endpoints
- `POST /ai/learn` - Record successful resolution
- `GET /ai/patterns` - Retrieve learned patterns
- `POST /ai/predict` - Get predictive insights
- `GET /ai/insights` - Get optimization suggestions
