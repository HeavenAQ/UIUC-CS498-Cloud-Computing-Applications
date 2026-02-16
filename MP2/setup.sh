#!/bin/bash

# Download 
sudo yum update -y
sudo yum install -y python3
sudo yum install -y python3-pip

# Create the app folder
mkdir -p /home/ec2-user/app
cd /home/ec2-user/app

# Set up env
python3 -m venv .venv
source .venv/bin/activate
pip3 install "fastapi[standard]" httpx
