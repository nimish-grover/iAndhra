#!/bin/bash

# Define container and image name
CONTAINER_NAME="wasca-container"
IMAGE_NAME="wasca"
VERSION_FILE="version.txt"
NGINX_CONF="/etc/nginx/sites-enabled/default"
MAINTENANCE_CONF="/etc/nginx/sites-enabled/maintenance.conf"

echo "Updating the server..."

# Enable maintenance mode
echo "Switching to maintenance mode..."
if [ -f "$MAINTENANCE_CONF" ]; then
    ln -sf "$MAINTENANCE_CONF" "$NGINX_CONF"
    nginx -s reload
    echo "Maintenance page activated."
else
    echo "Warning: Maintenance configuration not found!"
fi

# Pull the latest changes from Git
echo "Pulling latest changes from Git..."
git pull || { echo "Git pull failed!"; exit 1; }

# Display version information
if [ -f "$VERSION_FILE" ]; then
    VERSION=$(cat "$VERSION_FILE")
    echo "Current Version: $VERSION"
else
    echo "Warning: $VERSION_FILE not found!"
fi

# Stop and remove the existing Docker container
echo "Stopping the running container..."
docker stop $CONTAINER_NAME 2>/dev/null
echo "Removing the old container..."
docker rm $CONTAINER_NAME 2>/dev/null

# Remove unused images (dangling images)
echo "Removing unused Docker images..."
docker image prune -f

# Remove old versions of the image
echo "Removing old Docker images of $IMAGE_NAME..."
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep "^$IMAGE_NAME" | awk '{print $2}' | xargs -r docker rmi -f

# Remove unused build cache
echo "Clearing unused build cache..."
docker builder prune -a -f

# Build a new Docker image
echo "Building a new Docker image..."
docker build --no-cache -t $IMAGE_NAME . || { echo "Docker build failed!"; exit 1; }

# Run a new container with the updated image
echo "Starting a new container..."
docker run -d -p 8080:8080 --name $CONTAINER_NAME $IMAGE_NAME || { echo "Docker run failed!"; exit 1; }

# Restore the original Nginx configuration
echo "Restoring live Nginx configuration..."
ln -sf "/etc/nginx/sites-available/live.conf" "$NGINX_CONF"
nginx -s reload
echo "Live site is back online."

echo "Server update complete!"
