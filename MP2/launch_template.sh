#!/bin/bash
export HOME=/home/ec2-user
sudo yum update -y
sudo yum install stress-ng -y
sudo yum install htop -y
sudo yum install python3-pip -y
pip3 install "fastapi[standard]" 
sudo yum install git -y
cd /home/ec2-user
git clone "https://<your-token>@github.com/HeavenAQ/UIUC-CCA-MP2"
cd /home/ec2-user/UIUC-CCA-MP2
fastapi run 2-serve.py --port 8080
