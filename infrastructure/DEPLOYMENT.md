# 🚀 High-Load Deployment Guide

This guide provides step-by-step instructions for deploying the high-load optimizations to support 1000+ concurrent requests per second.

## 📋 Prerequisites

Before starting the deployment, ensure you have:

- [ ] Kubernetes cluster (GKE, EKS, AKS, or on-premises)
- [ ] kubectl configured with cluster access
- [ ] Minimum cluster capacity:
  - **Nodes**: 5-10 nodes minimum
  - **CPU**: 50+ vCPUs total
  - **Memory**: 100GB+ RAM total
  - **Storage**: 500GB+ available
- [ ] Helm 3.x installed (optional, for some components)
- [ ] Access to container registry (GCR, ECR, DockerHub, etc.)
- [ ] SSL certificates for your domain

## 🎯 Deployment Phases

### Phase 1: Infrastructure Preparation (1-2 hours)

#### 1.1 Review Current State

```bash
# Check current resource usage
kubectl top nodes
kubectl top pods -n aviladevops-saas

# Review current pod counts
kubectl get deployments -n aviladevops-saas
kubectl get hpa -n aviladevops-saas
```

#### 1.2 Backup Current Configuration

```bash
# Backup existing deployments
kubectl get all -n aviladevops-saas -o yaml > backup-$(date +%Y%m%d).yaml

# Backup ConfigMaps and Secrets
kubectl get configmaps,secrets -n aviladevops-saas -o yaml > backup-configs-$(date +%Y%m%d).yaml
```

#### 1.3 Prepare Secrets

```bash
# Create base64 encoded secrets
echo -n "your-secret-key" | base64
echo -n "postgresql://user:pass@host:5432/db" | base64
echo -n "your-redis-password" | base64

# Update secrets in the YAML file
# Edit: infrastructure/kubernetes/saas-high-load.yaml
# Replace <base64-encoded-*> placeholders with actual values
```

### Phase 2: Database Migration (2-3 hours)

#### 2.1 Deploy PostgreSQL Master

```bash
# Apply PostgreSQL master StatefulSet
kubectl apply -f - <<EOF
# Copy PostgreSQL master section from saas-high-load.yaml
EOF

# Wait for master to be ready
kubectl wait --for=condition=ready pod/postgres-master-0 -n aviladevops-saas --timeout=300s

# Verify master is running
kubectl logs postgres-master-0 -n aviladevops-saas
```

#### 2.2 Migrate Existing Data

```bash
# Dump existing database
kubectl exec -it <existing-postgres-pod> -n aviladevops-saas -- \
  pg_dump -U saas_user aviladevops_saas > backup.sql

# Restore to new master
kubectl exec -i postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user aviladevops_saas < backup.sql
```

#### 2.3 Deploy PostgreSQL Replicas

```bash
# Apply replicas StatefulSet
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# Wait for replicas
kubectl wait --for=condition=ready pod/postgres-replica-0 -n aviladevops-saas --timeout=300s
kubectl wait --for=condition=ready pod/postgres-replica-1 -n aviladevops-saas --timeout=300s

# Verify replication
kubectl exec -it postgres-master-0 -n aviladevops-saas -- \
  psql -U saas_user -c "SELECT * FROM pg_stat_replication;"
```

#### 2.4 Deploy PgBouncer

```bash
# Apply PgBouncer deployment
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# Verify PgBouncer is working
kubectl logs -l app=pgbouncer -n aviladevops-saas

# Test connection through PgBouncer
kubectl exec -it <app-pod> -n aviladevops-saas -- \
  psql -h pgbouncer -p 5432 -U saas_user aviladevops_saas -c "SELECT 1;"
```

### Phase 3: Redis Cluster Deployment (1-2 hours)

#### 3.1 Deploy Redis Cluster

```bash
# Apply Redis StatefulSet
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# Wait for all Redis pods
kubectl wait --for=condition=ready pod -l app=redis-cluster -n aviladevops-saas --timeout=300s

# Get Redis pod IPs
kubectl get pods -l app=redis-cluster -n aviladevops-saas -o wide
```

#### 3.2 Initialize Redis Cluster

```bash
# Create cluster (replace IPs with actual pod IPs)
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli --cluster create \
  <pod-0-ip>:6379 <pod-1-ip>:6379 <pod-2-ip>:6379 \
  <pod-3-ip>:6379 <pod-4-ip>:6379 <pod-5-ip>:6379 \
  --cluster-replicas 1 \
  --cluster-yes

# Verify cluster status
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli cluster info
```

#### 3.3 Test Redis Cluster

```bash
# Test set/get operations
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- \
  redis-cli set test-key "test-value"

kubectl exec -it redis-cluster-1 -n aviladevops-saas -- \
  redis-cli get test-key
```

### Phase 4: Application Deployment (2-3 hours)

#### 4.1 Update Application Configuration

```bash
# Update environment variables in applications
# Point to new PgBouncer and Redis endpoints

# DATABASE_URL: postgresql://user:pass@pgbouncer:5432/aviladevops_saas
# REDIS_URL: redis://redis-cluster:6379/0
```

#### 4.2 Deploy Applications with Gradual Rollout

```bash
# Start with one service at a time
# Landing Page
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml --selector=app=landing-page

# Wait for rollout
kubectl rollout status deployment/landing-page -n aviladevops-saas

# Verify health
kubectl get pods -l app=landing-page -n aviladevops-saas
```

#### 4.3 Deploy Remaining Services

```bash
# Deploy all services
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# Monitor rollout for each service
for service in recycling-system fiscal-system clinica-system main-app; do
  echo "Deploying $service..."
  kubectl rollout status deployment/$service -n aviladevops-saas
done
```

#### 4.4 Verify HPA Configuration

```bash
# Check HPA status
kubectl get hpa -n aviladevops-saas

# Should show:
# - Min replicas: 5-10
# - Max replicas: 40-50
# - Current metrics
```

### Phase 5: Nginx Deployment (1 hour)

#### 5.1 Backup Current Nginx Configuration

```bash
# If using Kubernetes Ingress
kubectl get ingress -n aviladevops-saas -o yaml > nginx-backup.yaml

# If using external Nginx
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
```

#### 5.2 Deploy New Nginx Configuration

**Option A: Kubernetes Ingress Controller**

```bash
# Update Ingress Controller ConfigMap
kubectl create configmap nginx-config \
  --from-file=nginx.conf=infrastructure/nginx/saas.high-load.conf \
  -n ingress-nginx \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart Ingress Controller
kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx
```

**Option B: External Nginx**

```bash
# Copy new configuration
sudo cp infrastructure/nginx/saas.high-load.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Reload Nginx (zero-downtime)
sudo nginx -s reload
```

#### 5.3 Verify Nginx Configuration

```bash
# Check Nginx status
curl http://your-domain/nginx-status

# Check health endpoint
curl http://your-domain/health

# Check metrics endpoint (internal only)
curl http://your-domain:9091/metrics
```

### Phase 6: Monitoring Deployment (1 hour)

#### 6.1 Deploy Prometheus

```bash
# Prometheus is included in the Kubernetes manifest
kubectl get pods -l app=prometheus -n aviladevops-saas

# Port-forward to access UI
kubectl port-forward svc/prometheus 9090:9090 -n aviladevops-saas

# Access at: http://localhost:9090
```

#### 6.2 Configure Prometheus Alerts

```bash
# Create ConfigMap for alert rules
kubectl create configmap prometheus-alerts \
  --from-file=alerts.yml=infrastructure/monitoring/prometheus-alerts.yml \
  -n aviladevops-saas

# Update Prometheus to use alerts
# (Already configured in the manifest)
```

#### 6.3 Deploy Grafana

```bash
# Grafana is included in the manifest
kubectl get pods -l app=grafana -n aviladevops-saas

# Get Grafana LoadBalancer IP
kubectl get svc grafana -n aviladevops-saas

# Import dashboard
# 1. Access Grafana UI
# 2. Go to Dashboards > Import
# 3. Upload infrastructure/monitoring/grafana-dashboard.json
```

### Phase 7: Load Testing (2-3 hours)

#### 7.1 Pre-flight Checks

```bash
# Verify all pods are running
kubectl get pods -n aviladevops-saas

# Check HPA status
kubectl get hpa -n aviladevops-saas

# Verify database connections
kubectl logs -l app=pgbouncer -n aviladevops-saas --tail=50

# Check Redis cluster health
kubectl exec -it redis-cluster-0 -n aviladevops-saas -- redis-cli cluster info
```

#### 7.2 Run Baseline Test (500 req/s)

```bash
# Start monitoring
kubectl port-forward svc/grafana 3000:3000 -n aviladevops-saas &

# Run test
cd scripts/setup
export BASE_URL=https://your-domain.com
./run-load-tests.sh

# Monitor in Grafana dashboard
```

#### 7.3 Analyze Results

Check the following metrics:
- [ ] Request rate sustained at target level
- [ ] Response time p95 < 300ms
- [ ] Error rate < 1%
- [ ] Pods scaled appropriately
- [ ] Database connections stable
- [ ] Redis operations smooth
- [ ] No CPU/memory throttling

#### 7.4 Run Full Load Test (1000 req/s)

```bash
# Ensure system recovered from baseline test
# Wait 10-15 minutes

# Run full test
./run-load-tests.sh

# Document results
```

## 🔍 Post-Deployment Validation

### Checklist

- [ ] All services running with correct replica counts
- [ ] HPA responding to load changes
- [ ] Database replication working (no lag)
- [ ] PgBouncer connection pool stable
- [ ] Redis cluster operating correctly
- [ ] Nginx handling high connection counts
- [ ] Monitoring and alerts configured
- [ ] Load test results meeting targets
- [ ] No error spikes or anomalies
- [ ] Documentation updated

### Key Metrics to Monitor

```bash
# Request rate
kubectl exec -it prometheus-xxx -n aviladevops-saas -- \
  promtool query instant http://localhost:9090 'sum(rate(http_requests_total[1m]))'

# Error rate
kubectl exec -it prometheus-xxx -n aviladevops-saas -- \
  promtool query instant http://localhost:9090 'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))'

# Response time p95
kubectl exec -it prometheus-xxx -n aviladevops-saas -- \
  promtool query instant http://localhost:9090 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))'
```

## 🚨 Rollback Procedures

If issues occur during deployment:

### Quick Rollback

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/<deployment-name> -n aviladevops-saas

# Restore previous configuration
kubectl apply -f backup-$(date +%Y%m%d).yaml
```

### Full Rollback

```bash
# Scale down new deployments
kubectl scale deployment --replicas=0 --all -n aviladevops-saas

# Restore from backup
kubectl delete namespace aviladevops-saas
kubectl apply -f backup-$(date +%Y%m%d).yaml

# Restore Nginx config
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
sudo nginx -s reload
```

## 📊 Success Criteria

The deployment is successful when:

1. **Performance Targets Met**
   - ✅ Request rate: 1000+ req/s sustained
   - ✅ Response time p95: <300ms
   - ✅ Error rate: <1%

2. **Infrastructure Stable**
   - ✅ All pods running and healthy
   - ✅ HPA scaling working correctly
   - ✅ Database replication lag <5 seconds
   - ✅ Redis cluster healthy

3. **Monitoring Active**
   - ✅ Prometheus collecting metrics
   - ✅ Grafana dashboards visible
   - ✅ Alerts configured and firing correctly

## 📞 Support

If you encounter issues:

1. Check logs: `kubectl logs <pod-name> -n aviladevops-saas`
2. Review events: `kubectl get events -n aviladevops-saas --sort-by='.lastTimestamp'`
3. Check monitoring dashboards for anomalies
4. Consult troubleshooting section in infrastructure/README.md
5. Contact DevOps team

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [PostgreSQL Tuning Guide](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
- [Redis Cluster Tutorial](https://redis.io/docs/manual/scaling/)
- [Nginx Tuning Guide](https://www.nginx.com/blog/tuning-nginx/)
- [k6 Load Testing](https://k6.io/docs/)

---

**Version**: 1.0  
**Last Updated**: 2024  
**Maintained by**: Ávila DevOps Team
