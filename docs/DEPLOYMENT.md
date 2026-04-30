# AirSense Deployment Guide

## Overview

This guide covers deploying AirSense in various environments, from local development to production cloud deployments.

---

## Prerequisites

### System Requirements

- **CPU:** 4+ cores recommended
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 20GB+ for data and models
- **OS:** Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### Software Requirements

- Python 3.9 or higher
- Java 11+ (for Apache Spark)
- Docker and Docker Compose (for containerized deployment)
- Git

---

## Local Development Deployment

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd AirSense

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Verify Java Installation

```bash
# Check Java version
java -version

# If not installed, install Java 11+
# Ubuntu/Debian:
sudo apt-get install openjdk-11-jre-headless

# macOS:
brew install openjdk@11

# Windows:
# Download from https://adoptium.net/
```

### 4. Run the System

```bash
# Run complete system
python src/main.py all

# Or use Makefile
make run-all

# Or run components separately
python src/main.py api        # API only
python src/main.py dashboard  # Dashboard only
python src/main.py pipeline   # Pipeline only
```

### 5. Access Services

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Dashboard:** http://localhost:8501

---

## Docker Deployment

### 1. Build Docker Image

```bash
# Build image
docker build -t airsense:latest .

# Or use docker-compose
docker-compose build
```

### 2. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Docker Compose Services

The `docker-compose.yml` includes:
- **airsense-api:** FastAPI backend
- **airsense-dashboard:** Streamlit frontend
- **redis:** Optional caching layer

### 4. Environment Variables

Create `.env` file with:

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Spark
SPARK_MASTER=local[*]

# Redis (optional)
REDIS_URL=redis://redis:6379/0
```

---

## Production Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**
   - Instance type: t3.xlarge or larger
   - OS: Ubuntu 20.04 LTS
   - Storage: 50GB+ EBS volume
   - Security group: Open ports 8000, 8501

2. **Install Dependencies**

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Deploy Application**

```bash
# Clone repository
git clone <repository-url>
cd AirSense

# Configure environment
cp .env.example .env
nano .env

# Start services
docker-compose up -d

# Setup nginx reverse proxy (optional)
sudo apt-get install nginx
sudo nano /etc/nginx/sites-available/airsense
```

4. **Nginx Configuration**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Using ECS (Elastic Container Service)

1. **Push Image to ECR**

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag airsense:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/airsense:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/airsense:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "airsense",
  "containerDefinitions": [
    {
      "name": "airsense-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/airsense:latest",
      "memory": 4096,
      "cpu": 2048,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ]
    }
  ]
}
```

3. **Create ECS Service**

```bash
aws ecs create-service \
  --cluster airsense-cluster \
  --service-name airsense-api \
  --task-definition airsense \
  --desired-count 2 \
  --launch-type FARGATE
```

---

### Google Cloud Platform (GCP)

#### Using Cloud Run

1. **Build and Push to Container Registry**

```bash
# Configure gcloud
gcloud auth configure-docker

# Build and push
docker build -t gcr.io/<project-id>/airsense:latest .
docker push gcr.io/<project-id>/airsense:latest
```

2. **Deploy to Cloud Run**

```bash
gcloud run deploy airsense \
  --image gcr.io/<project-id>/airsense:latest \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --port 8000 \
  --allow-unauthenticated
```

---

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name airsense-rg --location eastus

# Create container instance
az container create \
  --resource-group airsense-rg \
  --name airsense \
  --image airsense:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 8501 \
  --environment-variables \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO
```

---

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airsense-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: airsense-api
  template:
    metadata:
      labels:
        app: airsense-api
    spec:
      containers:
      - name: airsense-api
        image: airsense:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

**service.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: airsense-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: airsense-api
```

### 2. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/airsense-api
```

---

## Monitoring and Logging

### Application Logs

Logs are written to `logs/` directory in JSON format.

```bash
# View logs
tail -f logs/airsense_*.log

# Parse JSON logs
cat logs/airsense_*.log | jq '.'
```

### Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Docker health check
docker ps  # Check HEALTH status
```

### Monitoring with Prometheus

Add to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

---

## Backup and Recovery

### Data Backup

```bash
# Backup processed data
tar -czf backup_$(date +%Y%m%d).tar.gz data/processed/

# Backup models
tar -czf models_$(date +%Y%m%d).tar.gz models/
```

### Database Backup (if using PostgreSQL)

```bash
# Backup database
pg_dump -U airsense -d airsense_db > backup_$(date +%Y%m%d).sql

# Restore database
psql -U airsense -d airsense_db < backup_20260429.sql
```

---

## Security Best Practices

1. **Use HTTPS in production**
   - Configure SSL/TLS certificates
   - Use Let's Encrypt for free certificates

2. **Secure environment variables**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, Azure Key Vault)

3. **Enable authentication**
   - Implement API key authentication
   - Use OAuth2 for user authentication

4. **Network security**
   - Use VPC/private networks
   - Configure security groups/firewalls
   - Enable DDoS protection

5. **Regular updates**
   - Keep dependencies updated
   - Apply security patches
   - Monitor CVE databases

---

## Troubleshooting

### Common Issues

**Issue: Spark fails to start**
```bash
# Check Java installation
java -version

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

**Issue: Out of memory**
```bash
# Increase Docker memory limit
# Edit Docker Desktop settings or docker-compose.yml

# Reduce Spark memory usage
export SPARK_DRIVER_MEMORY=2g
export SPARK_EXECUTOR_MEMORY=2g
```

**Issue: Port already in use**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

---

## Performance Tuning

### Spark Configuration

```python
# In src/core/config.py
spark_config = {
    "spark.driver.memory": "4g",
    "spark.executor.memory": "4g",
    "spark.sql.shuffle.partitions": "200",
    "spark.default.parallelism": "100"
}
```

### API Performance

- Enable Redis caching
- Use connection pooling
- Implement rate limiting
- Enable gzip compression

---

## Scaling

### Horizontal Scaling

```bash
# Scale with Docker Compose
docker-compose up -d --scale airsense-api=3

# Scale with Kubernetes
kubectl scale deployment airsense-api --replicas=5
```

### Vertical Scaling

- Increase CPU/memory resources
- Optimize Spark configuration
- Use larger instance types

---

## Support

For deployment issues:
- Check logs: `logs/airsense_*.log`
- Review documentation: `docs/`
- Open GitHub issue
- Contact support team
