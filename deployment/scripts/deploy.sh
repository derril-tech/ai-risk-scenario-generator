#!/bin/bash

# AI Risk Scenario Generator Deployment Script
set -e

# Configuration
ENVIRONMENT=${1:-staging}
NAMESPACE="ai-risk-generator"
DOCKER_REGISTRY="gcr.io/ai-risk-generator"

echo "🚀 Deploying AI Risk Scenario Generator to $ENVIRONMENT"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "❌ Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is required but not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build and push Docker images
echo "🐳 Building Docker images..."

# Backend
echo "Building backend image..."
docker build -f deployment/docker/Dockerfile.backend -t $DOCKER_REGISTRY/backend:latest .
docker push $DOCKER_REGISTRY/backend:latest

# Workers
echo "Building workers image..."
docker build -f deployment/docker/Dockerfile.workers -t $DOCKER_REGISTRY/workers:latest .
docker push $DOCKER_REGISTRY/workers:latest

echo "✅ Docker images built and pushed"

# Deploy to Kubernetes
echo "☸️ Deploying to Kubernetes..."

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/backend-deployment.yaml
kubectl apply -f deployment/kubernetes/workers-deployment.yaml
kubectl apply -f deployment/kubernetes/ingress.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments..."
kubectl rollout status deployment/ai-risk-backend -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/ai-risk-workers -n $NAMESPACE --timeout=300s

echo "✅ Kubernetes deployment completed"

# Deploy frontend to Vercel (if production)
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "🌐 Deploying frontend to Vercel..."
    
    if command -v vercel &> /dev/null; then
        cd apps/frontend
        vercel --prod --yes
        cd ../..
        echo "✅ Frontend deployed to Vercel"
    else
        echo "⚠️ Vercel CLI not found. Please deploy frontend manually"
    fi
fi

# Run health checks
echo "🏥 Running health checks..."

# Wait for services to be ready
sleep 30

# Check backend health
BACKEND_URL="https://api.ai-risk-generator.com"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    BACKEND_URL="https://staging-api.ai-risk-generator.com"
fi

if curl -f "$BACKEND_URL/api/v1/health" > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Check workers health
WORKERS_URL="https://workers.ai-risk-generator.com"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    WORKERS_URL="https://staging-workers.ai-risk-generator.com"
fi

if curl -f "$WORKERS_URL/health" > /dev/null 2>&1; then
    echo "✅ Workers health check passed"
else
    echo "❌ Workers health check failed"
    exit 1
fi

# Display deployment summary
echo ""
echo "🎉 Deployment completed successfully!"
echo "Environment: $ENVIRONMENT"
echo "Backend: $BACKEND_URL"
echo "Workers: $WORKERS_URL"

if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "Frontend: https://ai-risk-generator.com"
else
    echo "Frontend: https://staging.ai-risk-generator.com"
fi

echo ""
echo "📊 Useful commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl logs -f deployment/ai-risk-backend -n $NAMESPACE"
echo "  kubectl logs -f deployment/ai-risk-workers -n $NAMESPACE"

# Run smoke tests
echo "🧪 Running smoke tests..."
python tests/load/load_test.py --environment $ENVIRONMENT --smoke-test

echo "✅ Deployment and smoke tests completed successfully!"
