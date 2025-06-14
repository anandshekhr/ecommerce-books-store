#!/bin/bash

set -e  # Stop on any error

echo "🚀 Starting Docker installation and build process..."

# Check if Docker is already installed
if ! command -v docker &> /dev/null
then
    echo "🐳 Docker not found. Installing Docker..."

    # Install Docker for Debian/Ubuntu-based systems
    apt-get update
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
    echo "✅ Docker is already installed."
fi

# Verify Docker version
docker --version

echo "🔧 Building Docker image from deploy/image/Dockerfile..."

docker build -f deploy/image/Dockerfile -t bookstore:latest .

echo "💾 Saving Docker image to tar archive..."
docker save bookstore:latest -o django_app.tar

echo "🎉 Docker build and save completed successfully!"
