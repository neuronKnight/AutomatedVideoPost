#!/bin/bash

# Deploy script for Video Automation System
echo "Deploying Video Automation System to production..."

# Switch to production environment
cp .env.prod .env

# Build and start production containers
docker-compose -f docker-compose.prod.yml up -d

echo "Deployment completed! System is running in production mode."
