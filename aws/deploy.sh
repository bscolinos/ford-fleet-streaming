#!/bin/bash
# Ford Fleet Demo - AWS Deployment Script
# This script builds and pushes Docker images to ECR, then updates ECS services

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT="${AWS_ACCOUNT:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REGISTRY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECS_CLUSTER="${ECS_CLUSTER:-ford-fleet-demo}"
ECS_SERVICE="${ECS_SERVICE:-ford-fleet-service}"

echo "=============================================="
echo "Ford Fleet Demo - AWS Deployment"
echo "=============================================="
echo "Region: ${AWS_REGION}"
echo "Account: ${AWS_ACCOUNT}"
echo "ECR Registry: ${ECR_REGISTRY}"
echo "ECS Cluster: ${ECS_CLUSTER}"
echo "=============================================="

# Login to ECR
echo ""
echo "Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create ECR repositories if they don't exist
echo ""
echo "Ensuring ECR repositories exist..."
for repo in ford-fleet-backend ford-fleet-producer ford-fleet-consumer ford-fleet-frontend; do
    aws ecr describe-repositories --repository-names ${repo} --region ${AWS_REGION} 2>/dev/null || \
        aws ecr create-repository --repository-name ${repo} --region ${AWS_REGION}
done

# Build and push images
echo ""
echo "Building and pushing Docker images..."

# Backend
echo "Building backend..."
docker build -t ${ECR_REGISTRY}/ford-fleet-backend:latest ./backend
docker push ${ECR_REGISTRY}/ford-fleet-backend:latest

# Producer
echo "Building producer..."
docker build -t ${ECR_REGISTRY}/ford-fleet-producer:latest ./kafka/producer
docker push ${ECR_REGISTRY}/ford-fleet-producer:latest

# Consumer
echo "Building consumer..."
docker build -t ${ECR_REGISTRY}/ford-fleet-consumer:latest ./kafka/consumer
docker push ${ECR_REGISTRY}/ford-fleet-consumer:latest

# Frontend (nginx with static files)
echo "Building frontend..."
cat > /tmp/Dockerfile.frontend << 'EOF'
FROM nginx:alpine
COPY frontend/ /usr/share/nginx/html/
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EOF
docker build -t ${ECR_REGISTRY}/ford-fleet-frontend:latest -f /tmp/Dockerfile.frontend .
docker push ${ECR_REGISTRY}/ford-fleet-frontend:latest

# Update ECS task definition
echo ""
echo "Updating ECS task definition..."
# Replace ACCOUNT placeholder with actual account ID
sed "s/ACCOUNT/${AWS_ACCOUNT}/g" aws/ecs-task-def.json > /tmp/task-def.json

# Register new task definition
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-def.json \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "New task definition: ${TASK_DEF_ARN}"

# Update ECS service (if exists)
echo ""
echo "Updating ECS service..."
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE} \
    --task-definition ${TASK_DEF_ARN} \
    --force-new-deployment \
    --region ${AWS_REGION} 2>/dev/null || \
    echo "Service ${ECS_SERVICE} not found. Create it manually or update this script."

echo ""
echo "=============================================="
echo "Deployment complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Ensure MSK cluster is running and topics are created"
echo "2. Ensure SingleStore Helios workspace is configured"
echo "3. Update Secrets Manager with connection details"
echo "4. Create/update ECS service if not exists"
echo "5. Configure ALB target groups and listeners"
echo ""

