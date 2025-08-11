# eBookVoice-AI CUDA Deployment Guide

## Overview
This guide explains how to deploy the eBookVoice-AI application on a CUDA-capable VM with secure cloud storage integration.

## Prerequisites

### Hardware Requirements
- NVIDIA GPU with CUDA 11.8+ support
- Minimum 8GB GPU VRAM (16GB+ recommended)
- 16GB+ system RAM
- 100GB+ storage space

### Software Requirements
- Ubuntu 20.04 LTS or newer
- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit
- Git

## Step 1: VM Setup

### 1.1 CUDA VM Creation
**AWS EC2:**
```bash
# Launch p3.2xlarge or g4dn.xlarge instance
# Choose Deep Learning AMI (Ubuntu 20.04)
# Configure security groups for ports 80, 443, 5000
```

**Google Cloud:**
```bash
# Create instance with GPU
gcloud compute instances create ebookvoice-gpu \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --maintenance-policy=TERMINATE
```

### 1.2 Install Docker and NVIDIA Container Toolkit

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-docker2
sudo systemctl restart docker

# Test NVIDIA Docker
sudo docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

## Step 2: Cloud Storage Setup

### 2.1 AWS S3 Setup
```bash
# Create S3 bucket
aws s3 mb s3://your-ebookvoice-bucket --region us-east-1

# Set bucket policy for secure access
aws s3api put-bucket-encryption \
    --bucket your-ebookvoice-bucket \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket your-ebookvoice-bucket \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### 2.2 Google Cloud Storage Setup
```bash
# Create bucket
gsutil mb -p your-project-id -c STANDARD -l us-central1 gs://your-ebookvoice-bucket

# Set encryption
gsutil encryption set -k projects/your-project-id/locations/global/keyRings/your-ring/cryptoKeys/your-key gs://your-ebookvoice-bucket

# Create service account
gcloud iam service-accounts create ebookvoice-storage \
    --description="eBookVoice Storage Service Account" \
    --display-name="eBookVoice Storage"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:ebookvoice-storage@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Download service account key
gcloud iam service-accounts keys create ~/gcp-credentials.json \
    --iam-account=ebookvoice-storage@your-project-id.iam.gserviceaccount.com
```

## Step 3: Application Deployment

### 3.1 Clone Repository
```bash
git clone https://github.com/your-username/eBookVoice-AI-Current.git
cd eBookVoice-AI-Current/backend
```

### 3.2 Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required environment variables:**
```env
# Application
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
FLASK_ENV=production

# Cloud Storage (choose one)
CLOUD_STORAGE_PROVIDER=aws
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-ebookvoice-bucket
AWS_REGION=us-east-1

# OR for GCP
# CLOUD_STORAGE_PROVIDER=gcp
# GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json
# GCP_STORAGE_BUCKET=your-ebookvoice-bucket
# GCP_PROJECT_ID=your-project-id

# Redis
REDIS_PASSWORD=your-redis-password

# Security
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60

# GPU
CUDA_VISIBLE_DEVICES=0
```

### 3.3 Setup SSL Certificates (Production)
```bash
# Create nginx directory
mkdir -p nginx/ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/nginx.key \
    -out nginx/ssl/nginx.crt

# For production, use Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

### 3.4 Create Nginx Configuration
```bash
mkdir -p nginx
```

Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server ebookvoice-backend:5000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        client_max_body_size 50M;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
}
```

## Step 4: Build and Deploy

### 4.1 Build Application
```bash
# Build the application
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f ebookvoice-backend
```

### 4.2 Production Deployment with SSL
```bash
# Deploy with production profile
docker-compose --profile production up -d

# Verify deployment
curl -k https://yourdomain.com/health
```

### 4.3 Enable Monitoring (Optional)
```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Grafana at http://yourdomain.com:3001
# Default login: admin/admin
```

## Step 5: Security Hardening

### 5.1 Firewall Configuration
```bash
# UFW firewall setup
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5000/tcp   # Block direct backend access
sudo ufw deny 6379/tcp   # Block direct Redis access
```

### 5.2 Docker Security
```bash
# Create non-root user for containers
sudo groupadd docker-users
sudo usermod -aG docker-users ebookvoice

# Set up log rotation
sudo nano /etc/logrotate.d/docker-containers
```

### 5.3 Regular Updates
```bash
# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
set -e

echo "Updating eBookVoice-AI..."
git pull origin main
docker-compose build --no-cache
docker-compose up -d
docker system prune -f

echo "Update complete!"
EOF

chmod +x update.sh
```

## Step 6: Monitoring and Maintenance

### 6.1 Health Checks
```bash
# Application health
curl https://yourdomain.com/health

# Docker containers
docker-compose ps

# GPU utilization
nvidia-smi

# Resource usage
htop
```

### 6.2 Log Management
```bash
# View application logs
docker-compose logs -f ebookvoice-backend

# View specific service logs
docker-compose logs redis
docker-compose logs nginx

# Clean old logs
docker system prune -f
```

### 6.3 Backup Strategy
```bash
# Backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/ebookvoice_$DATE"

mkdir -p $BACKUP_DIR
docker-compose exec redis redis-cli --rdb /tmp/dump.rdb
docker cp $(docker-compose ps -q redis):/tmp/dump.rdb $BACKUP_DIR/
cp .env $BACKUP_DIR/
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: $BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh

# Schedule backups
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## Troubleshooting

### Common Issues

1. **CUDA not detected:**
   ```bash
   # Check NVIDIA drivers
   nvidia-smi
   
   # Restart Docker with GPU support
   sudo systemctl restart docker
   ```

2. **Out of memory errors:**
   ```bash
   # Check GPU memory
   nvidia-smi
   
   # Reduce batch size in TTS config
   export TTS_BATCH_SIZE=1
   ```

3. **Storage permission errors:**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 uploads audiobooks chapters logs
   ```

4. **Network connectivity:**
   ```bash
   # Check container networking
   docker network ls
   docker-compose exec ebookvoice-backend ping redis
   ```

### Performance Optimization

1. **TTS Model Optimization:**
   - Use smaller models for faster processing
   - Enable model caching
   - Adjust batch sizes based on GPU memory

2. **Storage Optimization:**
   - Enable compression for uploads
   - Implement cleanup policies
   - Use CDN for file delivery

3. **Scaling:**
   - Use load balancer for multiple instances
   - Implement horizontal scaling with Kubernetes
   - Use GPU clusters for high-volume processing

## Support

For issues and support:
- Check application logs: `docker-compose logs`
- Monitor system resources: `htop`, `nvidia-smi`
- Review security logs: `/var/log/auth.log`
- Check firewall status: `sudo ufw status`