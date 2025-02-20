#!/bin/bash

# Define container and image name
CONTAINER_NAME="wasca-container"
IMAGE_NAME="wasca"

echo "Updating the server..."

# Pull the latest changes from Git
echo "Pulling latest changes from Git..."
git pull || { echo "Git pull failed!"; exit 1; }

# Stop and remove the existing Docker container
echo "Stopping the running container..."
docker stop $CONTAINER_NAME 2>/dev/null
echo "Removing the old container..."
docker rm $CONTAINER_NAME 2>/dev/null

# Build a new Docker image
echo "Building a new Docker image..."
docker build -t $IMAGE_NAME . || { echo "Docker build failed!"; exit 1; }

# Run a new container with the updated image
echo "Starting a new container..."
docker run -d -p 8080:8080 --name $CONTAINER_NAME $IMAGE_NAME || { echo "Docker run failed!"; exit 1; }

echo "Server update complete!"
