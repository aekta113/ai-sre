# AI SRE Knowledge Base

This document serves as a reference for N8N workflows. It contains runbooks for common Kubernetes issues and their remediation steps.

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

## Learning Section

> This section is automatically updated by the AI agent when new issues are resolved

### Recent Resolutions

<!-- New resolutions will be added here -->

## Best Practices

1. **Always check logs first** - Most issues are evident in logs
2. **Verify recent changes** - Check Git history for recent deployments
3. **Test in staging first** - If possible, reproduce and fix in staging
4. **Document new issues** - Update this knowledge base with new patterns
5. **Use dry-run** - Test kubectl commands with --dry-run when possible
6. **Keep audit trail** - Log all remediation actions with timestamps
