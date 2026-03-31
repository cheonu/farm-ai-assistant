# Deploy to Oracle Cloud Free Tier with K3s

## Self-Healing Features
- ✅ **Liveness Probe**: Automatically restarts unhealthy pods
- ✅ **Readiness Probe**: Only sends traffic to healthy pods
- ✅ **2 Replicas**: If one pod fails, the other handles traffic
- ✅ **Auto-scaling**: Scales up to 4 pods under load
- ✅ **Persistent Storage**: Vector database survives pod restarts

## Step 1: Set Up Oracle Cloud (Free Forever)

1. Sign up: https://www.oracle.com/cloud/free/
2. Create 2 ARM VMs (Always Free tier):
   - Shape: VM.Standard.A1.Flex
   - 2 OCPUs, 12GB RAM each
   - Ubuntu 22.04

## Step 2: Install K3s

### On Master Node (VM1):
```bash
# Install K3s
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

# Get node token
sudo cat /var/lib/rancher/k3s/server/node-token

# Get kubeconfig
sudo cat /etc/rancher/k3s/k3s.yaml
```

### On Worker Node (VM2):
```bash
# Replace MASTER_IP and TOKEN
curl -sfL https://get.k3s.io | K3S_URL=https://MASTER_IP:6443 K3S_TOKEN=YOUR_TOKEN sh -
```

## Step 3: Build and Push Docker Image

```bash
cd farm-ai-assistant

# Build image
docker build -t YOUR_DOCKERHUB_USERNAME/farm-ai-assistant:latest .

# Push to Docker Hub
docker login
docker push YOUR_DOCKERHUB_USERNAME/farm-ai-assistant:latest
```

## Step 4: Update Kubernetes Manifests

Edit `k8s/deployment.yaml`:
- Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username

Do not commit real credentials in `k8s/secrets.yaml`.
Create/update the secret directly from your shell instead:

```bash
kubectl create secret generic farm-ai-secrets \
  --from-literal=openai-api-key="YOUR_OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Step 5: Deploy to K3s

```bash
# Copy kubeconfig from master node
scp ubuntu@MASTER_IP:/etc/rancher/k3s/k3s.yaml ~/.kube/config

# Edit ~/.kube/config and replace 127.0.0.1 with MASTER_IP

# Create/update secret (safe; no key stored in git)
kubectl create secret generic farm-ai-secrets \
  --from-literal=openai-api-key="YOUR_OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Enable auto-scaling
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get pods
kubectl get svc
```

## Step 6: Access Your Application

```bash
# Get external IP
kubectl get svc farm-ai-assistant-service

# Test
curl http://EXTERNAL_IP/health
```

## Self-Healing in Action

### Test Pod Failure:
```bash
# Kill a pod
kubectl delete pod <pod-name>

# Watch it automatically restart
kubectl get pods -w
```

### Test High Load:
```bash
# Generate load
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://farm-ai-assistant-service/health; done"

# Watch pods scale up
kubectl get hpa -w
```

## Monitoring

```bash
# View logs
kubectl logs -f deployment/farm-ai-assistant

# Check pod health
kubectl describe pod <pod-name>

# View events
kubectl get events --sort-by='.lastTimestamp'
```

## Cost: $0/month (Free Forever)

Oracle Cloud Free Tier includes:
- 4 ARM VMs (24GB RAM total)
- 200GB storage
- Load balancer
- Network egress

🎉 Your RAG system is now running with self-healing on a free K8s cluster!
