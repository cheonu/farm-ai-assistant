# Deploy to Google Cloud Platform (GKE)

## Why GCP?
- ✅ **$300 free credit** for 90 days
- ✅ **Real GKE** (Google Kubernetes Engine) - production-grade
- ✅ **Managed K8s** - Google handles control plane
- ✅ **Auto-healing** built-in
- ✅ **Auto-scaling** built-in
- ✅ **Best learning experience** for production K8s

## Cost Estimate
With $300 credit, you can run:
- 2-node cluster (e2-small instances)
- ~$50/month = 6 months free
- Or 3 months with larger instances

---

## Step 1: Set Up GCP Account

1. Go to: https://cloud.google.com/free
2. Click **Get started for free**
3. Sign in with Google account
4. Enter payment details (required but won't be charged during trial)
5. Activate $300 credit (90 days)

---

## Step 2: Install Google Cloud CLI

### On macOS:
```bash
# Install gcloud CLI
brew install --cask google-cloud-sdk

# Initialize
gcloud init

# Login
gcloud auth login

# Set project (replace PROJECT_ID with your project ID from console)
gcloud config set project PROJECT_ID
```

### Verify installation:
```bash
gcloud version
kubectl version --client
```

---

## Step 3: Enable Required APIs

```bash
# Enable Kubernetes Engine API
gcloud services enable container.googleapis.com

# Enable Container Registry API (for Docker images)
gcloud services enable containerregistry.googleapis.com
```

---

## Step 4: Create GKE Cluster

```bash
# Create cluster with 2 nodes (self-healing enabled by default)
gcloud container clusters create farm-ai-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --disk-size=30 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=4 \
  --enable-autorepair \
  --enable-autoupgrade

# This takes 3-5 minutes
```

**What you get:**
- 2 nodes (e2-medium: 2 vCPUs, 4GB RAM each)
- Auto-scaling: 2-4 nodes based on load
- Auto-repair: Unhealthy nodes automatically replaced
- Auto-upgrade: Kubernetes version kept up-to-date

---

## Step 5: Configure kubectl

```bash
# Get credentials for kubectl
gcloud container clusters get-credentials farm-ai-cluster --zone=us-central1-a

# Verify connection
kubectl get nodes
```

You should see 2 nodes in Ready state.

---

## Step 6: Build and Push Docker Image

### Option A: Push to Google Container Registry (GCR)
```bash
cd farm-ai-assistant

# Configure Docker for GCR
gcloud auth configure-docker

# Build image
docker build -t gcr.io/PROJECT_ID/farm-ai-assistant:latest .

# Push to GCR
docker push gcr.io/PROJECT_ID/farm-ai-assistant:latest
```

### Option B: Use Docker Hub (simpler)
```bash
# Build and push to Docker Hub
docker build -t cheonu85/farm-ai-assistant:latest .
docker push cheonu85/farm-ai-assistant:latest
```

---

## Step 7: Update Kubernetes Manifests for GKE

Your existing manifests work on GKE! Just verify the image name in `deployment.yaml`:

```yaml
image: cheonu85/farm-ai-assistant:latest
# OR if using GCR:
# image: gcr.io/PROJECT_ID/farm-ai-assistant:latest
```

---

## Step 8: Deploy to GKE

```bash
cd k8s

# Create/update secret with OpenAI API key (without committing key)
kubectl create secret generic farm-ai-secrets \
  --from-literal=openai-api-key="YOUR_OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy application
kubectl apply -f deployment.yaml

# Enable horizontal pod autoscaling
kubectl apply -f hpa.yaml

# Check deployment status
kubectl get pods
kubectl get svc
```

---

## Step 9: Access Your Application

```bash
# Get external IP (takes 1-2 minutes to provision)
kubectl get svc farm-ai-assistant-service

# Wait for EXTERNAL-IP to show (not <pending>)
# Example output:
# NAME                        TYPE           EXTERNAL-IP      PORT(S)
# farm-ai-assistant-service   LoadBalancer   34.123.45.67     80:30123/TCP

# Test your API
curl http://EXTERNAL_IP/health
```

Your API will be available at: `http://EXTERNAL_IP`

---

## Step 10: Update React Native App

Update `PigFarmNew/components/AIAssistant.js`:

```javascript
const API_URL = 'http://YOUR_GKE_EXTERNAL_IP';
```

Then build new APK:
```bash
cd PigFarmNew
eas build --platform android --profile preview
```

---

## Self-Healing Features (Built-in to GKE)

### 1. Pod-level healing (your manifests):
- Liveness probes restart unhealthy pods
- Readiness probes prevent traffic to unready pods
- 2 replicas for redundancy

### 2. Node-level healing (GKE):
- Auto-repair: Unhealthy nodes automatically replaced
- Auto-upgrade: Security patches applied automatically

### Test self-healing:
```bash
# Kill a pod - watch it restart
kubectl delete pod <pod-name>
kubectl get pods -w

# Simulate high load - watch HPA scale
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- \
  /bin/sh -c "while sleep 0.01; do wget -q -O- http://farm-ai-assistant-service/health; done"

# In another terminal, watch scaling
kubectl get hpa -w
```

---

## Monitoring & Logs

### View logs:
```bash
# All pods
kubectl logs -f deployment/farm-ai-assistant

# Specific pod
kubectl logs -f <pod-name>
```

### Check pod health:
```bash
kubectl describe pod <pod-name>
```

### View cluster in GCP Console:
```bash
# Open GKE dashboard
gcloud console
# Navigate to: Kubernetes Engine → Clusters → farm-ai-cluster
```

---

## Cost Management

### Check current spend:
```bash
# View billing in console
gcloud console
# Navigate to: Billing → Reports
```

### Monitor credit usage:
- Go to: https://console.cloud.google.com/billing
- Check remaining credit (starts at $300)

### Estimated costs:
- 2 x e2-medium nodes: ~$50/month
- Load balancer: ~$18/month
- Storage: ~$2/month
- **Total: ~$70/month** (covered by $300 credit for 4+ months)

---

## Cleanup (When Trial Ends)

### Delete cluster:
```bash
gcloud container clusters delete farm-ai-cluster --zone=us-central1-a
```

### Delete images:
```bash
gcloud container images delete gcr.io/PROJECT_ID/farm-ai-assistant:latest
```

---

## Advantages of GKE vs K3s

| Feature | GKE | K3s (Contabo/Oracle) |
|---------|-----|----------------------|
| Setup | Managed (easy) | Manual (more work) |
| Control plane | Google manages | You manage |
| Auto-repair | Built-in | Manual |
| Auto-upgrade | Built-in | Manual |
| Monitoring | Built-in dashboard | Setup required |
| Cost (after trial) | ~$70/month | €3.60/month |
| Learning value | Production-grade | Production-grade |

---

## Next Steps

1. ✅ Create GCP account and activate $300 credit
2. ✅ Install gcloud CLI
3. ✅ Create GKE cluster
4. ✅ Build and push Docker image
5. ✅ Deploy using existing manifests
6. ✅ Update React Native app with new IP
7. ✅ Build new APK

🎉 You'll have production-grade K8s with self-healing running on GCP!
