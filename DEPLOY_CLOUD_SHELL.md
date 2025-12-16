# Deploy Python API to GCP VM using Cloud Shell

This guide uses GCP Cloud Shell (browser-based SSH) to deploy your Python Docker container.

## Step 1: Open GCP Cloud Shell

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the **Cloud Shell** icon (top right) or press `Ctrl+Shift+` (backtick)
3. Wait for Cloud Shell to initialize

## Step 2: Upload Your Code to Cloud Shell

### Option A: Using Cloud Shell Editor

1. Click the **Open Editor** button (pencil icon) in Cloud Shell
2. Create a new folder: `airbnb-python-api`
3. Upload all files from `python server` folder:
   - `app.py`
   - `scheduler.py`
   - `utils.py`
   - `requirements.txt`
   - `Dockerfile`
   - `.dockerignore`

### Option B: Using Git (if your code is in a repo)

```bash
# Clone your repository
git clone YOUR_REPO_URL
cd YOUR_REPO/airbnb\ next/python\ server
```

### Option C: Manual Upload via Cloud Shell

```bash
# Create directory
mkdir -p ~/airbnb-python-api
cd ~/airbnb-python-api

# You'll need to manually create/edit files using nano or vi
# Or use the Cloud Shell Editor
```

## Step 3: Set Up GCP Project

```bash
# Set your project ID (replace with your actual project ID)
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 4: Build and Push Docker Image

```bash
# Make sure you're in the python server directory
cd ~/airbnb-python-api  # or wherever you uploaded the files

# Build the Docker image
docker build -t airbnb-python-api .

# Tag for GCP Container Registry
docker tag airbnb-python-api gcr.io/$PROJECT_ID/airbnb-python-api:latest

# Configure Docker authentication
gcloud auth configure-docker

# Push to GCP Container Registry
docker push gcr.io/$PROJECT_ID/airbnb-python-api:latest
```

## Step 5: Create VM Instance

```bash
# Set variables
export ZONE="us-central1-a"
export VM_NAME="airbnb-python-api"

# Create VM with Container-Optimized OS
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=e2-small \
    --image-family=cos-stable \
    --image-project=cos-cloud \
    --boot-disk-size=10GB \
    --tags=http-server
```

## Step 6: Configure Firewall

```bash
# Allow HTTP traffic on port 5000
gcloud compute firewall-rules create allow-http-5000 \
    --allow tcp:5000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic on port 5000" \
    --target-tags http-server
```

## Step 7: Deploy Container to VM

```bash
# Set environment variables (replace with your actual values)
export MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy"
export NEXTJS_API_URL="https://your-nextjs-app.com"  # Your Next.js app URL

# Deploy the container
gcloud compute instances update-container $VM_NAME \
    --zone=$ZONE \
    --container-image=gcr.io/$PROJECT_ID/airbnb-python-api:latest \
    --container-env="MONGODB_URI=$MONGODB_URI,NEXTJS_API_URL=$NEXTJS_API_URL,PYTHON_API_URL=http://0.0.0.0:5000" \
    --container-restart-policy=always
```

## Step 8: Get Your VM IP Address

```bash
# Get the external IP
gcloud compute instances describe $VM_NAME --zone=$ZONE \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

Your API will be available at: `http://<VM_IP_ADDRESS>:5000`

## Step 9: Test the Deployment

```bash
# Get the IP first
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

# Test health endpoint
curl http://$VM_IP:5000/api/health

# Test scheduler status
curl http://$VM_IP:5000/api/scheduler/status
```

## Updating the Deployment

When you make code changes:

```bash
# Navigate to your code directory
cd ~/airbnb-python-api

# Rebuild and push
docker build -t airbnb-python-api .
docker tag airbnb-python-api gcr.io/$PROJECT_ID/airbnb-python-api:latest
docker push gcr.io/$PROJECT_ID/airbnb-python-api:latest

# Update the VM
gcloud compute instances update-container $VM_NAME \
    --zone=$ZONE \
    --container-image=gcr.io/$PROJECT_ID/airbnb-python-api:latest
```

## Viewing Logs

```bash
# View VM serial port output (container logs)
gcloud compute instances get-serial-port-output $VM_NAME --zone=$ZONE
```

## Quick Reference Commands

```bash
# Stop VM (saves money)
gcloud compute instances stop $VM_NAME --zone=$ZONE

# Start VM
gcloud compute instances start $VM_NAME --zone=$ZONE

# Delete VM (when you're done)
gcloud compute instances delete $VM_NAME --zone=$ZONE

# List all VMs
gcloud compute instances list
```

## Troubleshooting

### Container not starting
```bash
# Check VM logs
gcloud compute instances get-serial-port-output $VM_NAME --zone=$ZONE | tail -50
```

### Can't access API
- Check if VM is running: `gcloud compute instances list`
- Verify firewall rule: `gcloud compute firewall-rules list`
- Check if container is running: SSH into VM and check

### SSH into VM (if needed)
```bash
gcloud compute ssh $VM_NAME --zone=$ZONE
# Then inside VM:
sudo journalctl -u konlet-startup
```

