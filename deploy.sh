#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Install Docker prerequisites
sudo apt update -yq

sudo apt install -yq apt-transport-https ca-certificates curl software-properties-common

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install npm
sudo apt install -yq nodejs npm

# Install PM2
sudo npm install -g pm2

# Install pip
sudo apt install -yq python3-pip

# Install Bittensor
curl -fsSL https://raw.githubusercontent.com/opentensor/bittensor/master/scripts/install.sh

# Clone cortex.t repository
git clone https://github.com/corcel-api/cortex.t.git
cd cortex.t

# Install cortex.t dependencies
pip install -e .

# Install dotenv
pip install python-dotenv

cd ..

# Clone subtensor repository
git clone https://github.com/opentensor/subtensor.git

# Start subtensor using Docker Compose
cd subtensor
sudo docker-compose up -d

cd ..

# Refresh the shell environment
source ~/.bashrc

echo "Initial setup completed!"
