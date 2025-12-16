# Deployment Guide for GCP VM

This guide will help you deploy the Airbnb Python API to a Google Cloud Platform (GCP) VM using Docker.

## Prerequisites

1. **GCP Account**: You need a GCP account with billing enabled
2. **gcloud CLI**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install [Docker](https://docs.docker.com/get-docker/)
4. **GCP Project**: Create a GCP project or use an existing one

## Step 1: Set Up GCP Project

```bash
# Login to GCP
gcloud auth login

# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 2: Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
export MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy"
export NEXTJS_API_URL="https://your-nextjs-app.com"  # Your Next.js app URL
export PYTHON_API_URL="http://0.0.0.0:5000"
```

## Step 3: Build and Push Docker Image

### Option A: Using the deployment script

```bash
# Make script executable
chmod +x deploy-gcp.sh

# Edit the script and set your PROJECT_ID, ZONE, and VM_NAME
# Then run:
./deploy-gcp.sh
```

### Option B: Manual deployment

```bash
# Build the image
docker build -t airbnb-python-api:latest .

# Tag for GCP Container Registry
docker tag airbnb-python-api:latest gcr.io/$PROJECT_ID/airbnb-python-api:latest

# Configure Docker to use gcloud credentials
gcloud auth configure-docker

# Push to GCP Container Registry
docker push gcr.io/$PROJECT_ID/airbnb-python-api:latest
```

## Step 4: Create GCP VM Instance

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

## Step 5: Deploy Container to VM

```bash
# Deploy the container
gcloud compute instances update-container $VM_NAME \
    --zone=$ZONE \
    --container-image=gcr.io/$PROJECT_ID/airbnb-python-api:latest \
    --container-env="MONGODB_URI=$MONGODB_URI,NEXTJS_API_URL=$NEXTJS_API_URL,PYTHON_API_URL=http://0.0.0.0:5000" \
    --container-restart-policy=always
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

## Step 7: Get VM IP Address

```bash
# Get the external IP
gcloud compute instances describe $VM_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Your API will be available at: `http://<VM_IP_ADDRESS>:5000`

## Testing the Deployment

```bash
# Health check
curl http://<VM_IP_ADDRESS>:5000/api/health

# Test scheduler status
curl http://<VM_IP_ADDRESS>:5000/api/scheduler/status
```

## Updating the Deployment

When you make changes to the code:

```bash
# Rebuild and push
docker build -t airbnb-python-api:latest .
docker tag airbnb-python-api:latest gcr.io/$PROJECT_ID/airbnb-python-api:latest
docker push gcr.io/$PROJECT_ID/airbnb-python-api:latest

# Update the VM
gcloud compute instances update-container $VM_NAME \
    --zone=$ZONE \
    --container-image=gcr.io/$PROJECT_ID/airbnb-python-api:latest
```

## Viewing Logs

```bash
# View container logs
gcloud compute instances get-serial-port-output $VM_NAME --zone=$ZONE

# Or SSH into the VM and check Docker logs
gcloud compute ssh $VM_NAME --zone=$ZONE
sudo journalctl -u konlet-startup
```

## Stopping/Starting the VM

```bash
# Stop VM
gcloud compute instances stop $VM_NAME --zone=$ZONE

# Start VM
gcloud compute instances start $VM_NAME --zone=$ZONE
```

## Cost Optimization

- Use `e2-micro` or `e2-small` machine types for development
- Consider using preemptible instances for cost savings
- Set up auto-shutdown schedules if not needed 24/7

## Security Considerations

1. **Use Secret Manager**: Store sensitive data like MongoDB URI in GCP Secret Manager
2. **Restrict Firewall**: Only allow traffic from your Next.js app IP
3. **Use HTTPS**: Set up a load balancer with SSL certificate
4. **IAM Roles**: Use service accounts with minimal required permissions

## Troubleshooting

### Container not starting
```bash
# Check VM logs
gcloud compute instances get-serial-port-output $VM_NAME --zone=$ZONE
```

### Can't connect to API
- Check firewall rules
- Verify container is running: `gcloud compute ssh $VM_NAME --zone=$ZONE`
- Check if port 5000 is exposed correctly

### Scheduler not working
- Verify MongoDB connection string is correct
- Check environment variables are set properly
- Review container logs for errors

## Alternative: Using Cloud Run

For a serverless option, you can also deploy to Cloud Run:

```bash
# Build and push (same as above)
docker build -t gcr.io/$PROJECT_ID/airbnb-python-api:latest .
docker push gcr.io/$PROJECT_ID/airbnb-python-api:latest

# Deploy to Cloud Run
gcloud run deploy airbnb-python-api \
    --image gcr.io/$PROJECT_ID/airbnb-python-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars MONGODB_URI=$MONGODB_URI,NEXTJS_API_URL=$NEXTJS_API_URL
```

