# 🔧 High-Load Operations Quick Reference

Quick reference guide for common operations when managing the high-load infrastructure.

## 🚀 Quick Commands

### Deployment

```bash
# Deploy complete high-load infrastructure
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# Deploy only specific service
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml --selector=app=landing-page

# Update Nginx configuration
sudo cp infrastructure/nginx/saas.high-load.conf /etc/nginx/nginx.conf
sudo nginx -t && sudo nginx -s reload
```

### Monitoring

```bash
# Check pod status
kubectl get pods -n aviladevops-saas -o wide

# Check HPA status
kubectl get hpa -n aviladevops-saas

# View pod logs
kubectl logs -f <pod-name> -n aviladevops-saas

# View recent events
kubectl get events -n aviladevops-saas --sort-by='.lastTimestamp' | tail -20
```

### Scaling

```bash
# Manual scale (override HPA temporarily)
kubectl scale deployment landing-page --replicas=20 -n aviladevops-saas

# Update HPA min/max replicas
kubectl patch hpa landing-page-hpa -n aviladevops-saas -p '{"spec":{"minReplicas":15}}'

# Check current replicas vs desired
kubectl get deployment -n aviladevops-saas
```

### Database Operations

```bash
# Check PostgreSQL replication status
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user -c "SELECT * FROM pg_stat_replication;"

# Check PgBouncer statistics
kubectl exec -it $(kubectl get pod -l app=pgbouncer -n aviladevops-saas -o jsonpath='{.items[0].metadata.name}') \
  -n aviladevops-saas -- psql -p 5432 -U pgbouncer pgbouncer -c "SHOW POOLS;"

# Check active database connections
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user -c "SELECT count(*) FROM pg_stat_activity;"
```

### Redis Operations

```bash
# Check Redis cluster status
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- redis-cli cluster info

# Check Redis cluster nodes
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- redis-cli cluster nodes

# Monitor Redis operations
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- redis-cli --stat

# Check memory usage
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- redis-cli info memory
```

### Load Testing

```bash
# Run complete load test
cd scripts/setup
BASE_URL=https://your-domain.com ./run-load-tests.sh

# Run specific test scenario
k6 run --vus 1000 --duration 10m scripts/setup/load-test-k6.js

# Run test with custom parameters
BASE_URL=https://staging.example.com k6 run \
  --vus 500 \
  --duration 5m \
  scripts/setup/load-test-k6.js
```

## 📊 Health Checks

### System Health

```bash
# Overall system health
curl https://your-domain.com/health

# Nginx status
curl https://your-domain.com/nginx-status

# Prometheus metrics
curl http://your-domain:9091/metrics
```

### Service Health

```bash
# Check all services
for service in landing-page recycling-system fiscal-system clinica-system main-app; do
  echo "=== $service ==="
  kubectl get pods -l app=$service -n aviladevops-saas
done

# Check service endpoints
kubectl get endpoints -n aviladevops-saas
```

### Resource Usage

```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods -n aviladevops-saas

# Namespace resource usage
kubectl top pods -n aviladevops-saas --sort-by=cpu
kubectl top pods -n aviladevops-saas --sort-by=memory
```

## 🔍 Troubleshooting

### High Error Rate

```bash
# Check pod logs for errors
kubectl logs -l app=landing-page -n aviladevops-saas --tail=100 | grep -i error

# Check recent pod restarts
kubectl get pods -n aviladevops-saas --field-selector=status.phase=Running \
  -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount

# Describe pod to see events
kubectl describe pod <pod-name> -n aviladevops-saas
```

### High Response Time

```bash
# Check database query performance
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check PgBouncer wait queue
kubectl exec -it $(kubectl get pod -l app=pgbouncer -n aviladevops-saas -o jsonpath='{.items[0].metadata.name}') \
  -n aviladevops-saas -- psql -p 5432 -U pgbouncer pgbouncer -c "SHOW STATS;"

# Check Redis latency
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli --latency-history
```

### Scaling Issues

```bash
# Check HPA status and conditions
kubectl describe hpa landing-page-hpa -n aviladevops-saas

# Check metrics server
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml

# Check resource requests/limits
kubectl get pods -n aviladevops-saas -o json | \
  jq '.items[] | {name: .metadata.name, resources: .spec.containers[0].resources}'
```

### Database Issues

```bash
# Check PostgreSQL logs
kubectl logs postgres-master-0 -n aviladevops-saas --tail=100

# Check replication lag
kubectl exec -it postgres-replica-0 -n aviladevops-saas -- \
  psql -U saas_user -c "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;"

# Check database size
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user -c "SELECT pg_size_pretty(pg_database_size('aviladevops_saas'));"
```

### Redis Issues

```bash
# Check Redis logs
kubectl logs redis-cluster-0 -n aviladevops-saas --tail=100

# Check cluster health
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli --cluster check redis-cluster-0:6379

# Check for memory issues
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli info memory | grep -E "used_memory|maxmemory|evicted_keys"
```

## 🔄 Common Maintenance Tasks

### Rolling Restart

```bash
# Restart all pods in a deployment (rolling)
kubectl rollout restart deployment/landing-page -n aviladevops-saas

# Watch rollout status
kubectl rollout status deployment/landing-page -n aviladevops-saas

# Restart all deployments
for deployment in landing-page recycling-system fiscal-system clinica-system main-app; do
  kubectl rollout restart deployment/$deployment -n aviladevops-saas
done
```

### Update Configuration

```bash
# Update ConfigMap
kubectl create configmap saas-config \
  --from-literal=ENVIRONMENT=production \
  --from-literal=DEBUG=False \
  -n aviladevops-saas \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new config
kubectl rollout restart deployment/landing-page -n aviladevops-saas
```

### Backup Operations

```bash
# Backup PostgreSQL database
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  pg_dump -U saas_user aviladevops_saas | gzip > backup-$(date +%Y%m%d).sql.gz

# Backup Redis data
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli --rdb /tmp/dump.rdb

# Backup Kubernetes resources
kubectl get all -n aviladevops-saas -o yaml > k8s-backup-$(date +%Y%m%d).yaml
```

## 📈 Performance Tuning

### Optimize Database

```bash
# Analyze tables
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user aviladevops_saas -c "ANALYZE VERBOSE;"

# Reindex if needed
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user aviladevops_saas -c "REINDEX DATABASE aviladevops_saas;"

# Vacuum
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user aviladevops_saas -c "VACUUM ANALYZE;"
```

### Optimize Redis

```bash
# Clear cache if needed
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli FLUSHDB

# Check slow log
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli SLOWLOG GET 10
```

### Optimize Nginx

```bash
# Reload configuration without downtime
sudo nginx -s reload

# Test configuration
sudo nginx -t

# View access log analysis
tail -f /var/log/nginx/access.log | \
  awk '{print $7}' | sort | uniq -c | sort -rn | head
```

## 🎯 Performance Metrics

### Quick Metrics Check

```bash
# Using Prometheus (if port-forwarded)
# Request rate
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total[1m]))' | jq

# Error rate
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{status=~"5.."}[5m]))/sum(rate(http_requests_total[5m]))' | jq

# Response time p95
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(http_request_duration_seconds_bucket[5m]))by(le))' | jq
```

## 📞 Emergency Contacts

### Immediate Actions

1. **Service Down**: Check pod status, restart if needed
2. **Database Issues**: Check replication, connection pool
3. **High Load**: Monitor HPA, check if scaling is working
4. **Out of Memory**: Check pod memory usage, scale up if needed
5. **Network Issues**: Check service endpoints, ingress rules

### Escalation Path

1. Check monitoring dashboards
2. Review recent deployments/changes
3. Check logs and events
4. Contact DevOps team
5. Escalate to infrastructure team if needed

---

**Quick Ref Version**: 1.0  
**Last Updated**: 2024  
**Maintained by**: Ávila DevOps Team
