# Simple GCP VM Deployment Guide

## Prerequisites

1. **Install Google Cloud SDK**: Download from [here](https://cloud.google.com/sdk/docs/install)
2. **GCP Account**: Sign up at [cloud.google.com](https://cloud.google.com)
3. **Docker**: Already installed (you're using it locally)

## Step-by-Step Deployment

### Step 1: Login and Setup GCP

```bash
# Login to GCP
gcloud auth login

# Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Build and Push Docker Image

```bash
# Navigate to python server directory
cd "airbnb next/python server"

# Set your project ID
set PROJECT_ID=YOUR_PROJECT_ID

# Build the image
docker build -t airbnb-python-api .

# Tag for GCP Container Registry
docker tag airbnb-python-api gcr.io/%PROJECT_ID%/airbnb-python-api:latest

# Configure Docker to use gcloud credentials
gcloud auth configure-docker

# Push to GCP Container Registry
docker push gcr.io/%PROJECT_ID%/airbnb-python-api:latest
```

### Step 3: Create GCP VM Instance

```bash
# Set variables
set ZONE=us-central1-a
set VM_NAME=airbnb-python-api

# Create VM with Container-Optimized OS
gcloud compute instances create %VM_NAME% ^
    --zone=%ZONE% ^
    --machine-type=e2-small ^
    --image-family=cos-stable ^
    --image-project=cos-cloud ^
    --boot-disk-size=10GB ^
    --tags=http-server
```

### Step 4: Configure Firewall

```bash
# Allow HTTP traffic on port 5000
gcloud compute firewall-rules create allow-http-5000 ^
    --allow tcp:5000 ^
    --source-ranges 0.0.0.0/0 ^
    --description "Allow HTTP traffic on port 5000" ^
    --target-tags http-server
```

### Step 5: Deploy Container to VM

```bash
# Set environment variables (replace with your actual values)
set MONGODB_URI=mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy
set NEXTJS_API_URL=https://your-nextjs-app.com

# Deploy the container
gcloud compute instances update-container %VM_NAME% ^
    --zone=%ZONE% ^
    --container-image=gcr.io/%PROJECT_ID%/airbnb-python-api:latest ^
    --container-env=MONGODB_URI=%MONGODB_URI%,NEXTJS_API_URL=%NEXTJS_API_URL%,PYTHON_API_URL=http://0.0.0.0:5000 ^
    --container-restart-policy=always
```

### Step 6: Get Your VM IP Address

```bash
# Get the external IP
gcloud compute instances describe %VM_NAME% --zone=%ZONE% --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

Your API will be available at: `http://<VM_IP_ADDRESS>:5000`

## Testing the Deployment

```bash
# Health check
curl http://<VM_IP_ADDRESS>:5000/api/health

# Scheduler status
curl http://<VM_IP_ADDRESS>:5000/api/scheduler/status
```

## Updating the Deployment

When you make code changes:

```bash
# Rebuild and push
docker build -t airbnb-python-api .
docker tag airbnb-python-api gcr.io/%PROJECT_ID%/airbnb-python-api:latest
docker push gcr.io/%PROJECT_ID%/airbnb-python-api:latest

# Update the VM
gcloud compute instances update-container %VM_NAME% --zone=%ZONE% --container-image=gcr.io/%PROJECT_ID%/airbnb-python-api:latest
```

## Viewing Logs

```bash
# View VM logs
gcloud compute instances get-serial-port-output %VM_NAME% --zone=%ZONE%
```

## Stopping/Starting VM

```bash
# Stop VM (saves money)
gcloud compute instances stop %VM_NAME% --zone=%ZONE%

# Start VM
gcloud compute instances start %VM_NAME% --zone=%ZONE%
```

## Cost Estimate

- **e2-small VM**: ~$10-15/month (if running 24/7)
- **Container Registry**: Free for first 0.5GB storage
- **Network**: Free egress up to 1GB/month

## Troubleshooting

### Container not starting
```bash
# Check VM logs
gcloud compute instances get-serial-port-output %VM_NAME% --zone=%ZONE%
```

### Can't access API
- Check firewall rules: `gcloud compute firewall-rules list`
- Verify VM is running: `gcloud compute instances list`
- Check if port 5000 is exposed in container

### Scheduler not working
- Verify MongoDB connection string is correct
- Check environment variables are set properly
- Review container logs

