#!/bin/bash

# Install Docker prerequisites
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install npm
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2

# Clone cortex.t repository
git clone https://github.com/corcel-api/cortex.t.git
cd cortex.t

# Install cortex.t dependencies
pip install -e .

cd ..

# Clone subtensor repository
git clone https://github.com/opentensor/subtensor.git

# Start subtensor using Docker Compose
cd subtensor
sudo docker-compose up -d

cd ..

echo "Setup completed!"
