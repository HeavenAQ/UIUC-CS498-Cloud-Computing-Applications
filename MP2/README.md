# Load Balancing and Auto-scaling

## Overview

## Requirements

- `ssh`

## 0. Environment Setup

```bash
# ensure the aws cli is installed
aws --version

# export the profile to use
export AWS_PROFILE=<profile-name>

# check the profile is set
aws sts get-caller-identity
aws configure get region
```

---

## Part 1 Load Balancing

## 1. Create an EC2 Instance 

1. Take a look at [here](https://github.com/HeavenAQ/UIUC-CS498-Cloud-Computing-Applications/tree/main/MP1-V2) for the detailed steps.
2. Open port `8080` for security group ingress.

```bash
# we will expose our app to port 8080, so the port is 8080
aws ec2 authorize-security-group-ingress \
--group-name uiuc-sg \
--protocol tcp \
--port 8080 \
--cidr 0.0.0.0/0
```

3. After successfully creating an `EC2` instance, copy its 
    - `SubnetId`: will be used for `NACL` setup.
    - `InstanceId`: just in case you forget anything.
    - `PublicIpAddress`: will be used for `ssh` connection

> [!TIP]
> 
> If you forget to copy the information that you need, use:
>
> ```bash
> aws ec2 describe-instances \
>   --instance-id i-XXXXXXXX \
>   --query "Reservations[0].Instances[0].<the-info-you-want>" \
>   --output json
> ``` 



## 2. Set up Data Access Service

### 1. SSH into the instance

```bash
ssh -i <pem-file> ec2-user@13.231.104.90
```

### 2. Set up the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade "fastapi[standard]" 
```

> [!NOTE]
>
> - Personally, I use [`uv`](https://docs.astral.sh/uv/) for `Python` package management. For the purpose of demonstration, I chose the simplest way here.

### 3. Write a simple FastAPI server based on the requirements

```python
import os
from fastapi import FastAPI
from typing import Literal
from pydantic import BaseModel
import asyncio

app_read = FastAPI()
app_update = FastAPI()
seed_lock = asyncio.Lock()
seed_file = "seed.txt"


class UpdateSeedReq(BaseModel):
    num: int


class UpdateSeedRes(BaseModel):
    num: int
    status: Literal["ok", "error"]


@app_update.post("/")
async def set_seed(body: UpdateSeedReq):
    global seed
    async with seed_lock:
        with open(seed_file, "w") as f:
            _ = f.write(f"{body.num}")
        return UpdateSeedRes(num=body.num, status="ok")


@app_read.get("/")
async def get_seed():
    async with seed_lock:
        if not os.path.exists(seed_file):
            return 0
        else:
            with open(seed_file, "r") as f:
                return f.read()
```

> [!WARNING] 
>
> Using `Redis` should be a best practice. But for simplicity, I chose to use file I/O.

### 4. Spin up the server

```bash
fastapi run server.py --port 8080
```

### 5. Test your server with the following commands

```bash
# get seed, should see 0
curl http://<public-ip-address>:8080/ 

# set seed
curl -X POST http://<public-ip-address>:8080/  \
     -H "Content-Type: application/json" \
     -d '{"num": 1000}'

# get seed, should see 1000
curl http://<public-ip-address>:8080/ 
```

## 3. Set up Receiver Service

### 1. Launch 2 other receiver EC2 instances

> [!NOTE]
> 
> As required by the assignment, we need to assign the two receiver instances a subnet different from the first `EC2` instance

#### 1. Get the default VPC ID

```bash
aws ec2 describe-vps --filters Name=isDefault,Values=true
```

#### 2. Get the list of subnets and choose a different one

```bash
aws ec2 describe-subnets --filters Name=vpc-id,Values=<your-vpc-id>
```

#### 3. Get the security group ID

- Since we can't using both `--subnet-id` and `--security-groups` at the same time when using the `run-instances` command, we need to get the security group ID of your chosen security group and use it with `--security-group-ids` flag latter.

```bash
aws ec2 describe-security-groups \
  --filters Name=group-name,Values=<your-sg-name> \
  --query "SecurityGroups[].GroupId" \
  --output text
```

#### 4. Create the instances

```bash
# Launch Instances
aws ec2 run-instances \
--image-id  ami-06cce67a5893f85f9 \
--instance-type t2.micro \
--subnet-id <subnet-id> \
--key-name <key-name> \
--security-groups <sg-name> \
--count 2 \
--tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=MyCLIInstance}]"
```


> [!TIP]
> 
> Remember to copy their `InstanceId`, `SubnetId`, and `PublicIpAddress`

#### 5. Create the IAM Role with AmazonVPCFullAccess

- In `trust-policy.json`

```json
{
  "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
}
```

- run the following command

```bash
aws iam create-role \
--role-name ec2-vpc-full-access \
--assume-role-policy-document file://trust-policy.json
```

#### 6. Attach policy to the role

```bash
aws iam attach-role-policy \
--role-name ec2-vpc-full-access \
--policy-arn arn:aws:iam::aws:policy/AmazonVPCFullAccess

```

#### 7. Create an instance profile and add the role to it

```bash
aws iam create-instance-profile --instance-profile ec2-vpc-full-access-profile
aws iam add-role-to-instance-profile \
--instance-profile ec2-vpc-full-access-profile \
--role-name ec2-vpc-full-access
```

#### 8. Associate the EC2 Instances with the profile

```bash
for id in \
i-XXXXXXX  \
i-YYYYYYY 
do
        aws ec2 associate-iam-instance-profile \
        --instance-id $id \
        --iam-instance-profile Name="ec2-vpc-full-access-profile"
done
```

### 2. Create a Receiver Script `receiver.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import boto3

app = FastAPI()

DATA_ACCESS_SERVICE_GET_URL = ""
DATA_ACCESS_SERVICE_POST_URL = ""
NACL_ID = ""
AWS_REGION = ""

ec2_client = boto3.client("ec2", region_name=AWS_REGION)


class UpdateSeedReq(BaseModel):
    num: int


async def get_public_ip():
    async with httpx.AsyncClient(timeout=2.0) as client:
        token_resp = await client.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        )
        token = token_resp.text

        ip_resp = await client.get(
            "http://169.254.169.254/latest/meta-data/public-ipv4",
            headers={"X-aws-ec2-metadata-token": token},
        )

        return ip_resp.text.strip()


@app.get("/")
async def route_get():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DATA_ACCESS_SERVICE_GET_URL)
            seed_value = response.json()

        public_ip = await get_public_ip()

        return {"seed": seed_value, "server_ip_address": public_ip}

    except Exception:
        return "Error in processing request"


@app.post("/")
async def route_post(body: UpdateSeedReq):
    try:
        # Forward POST to data service
        async with httpx.AsyncClient() as client:
            await client.post(DATA_ACCESS_SERVICE_POST_URL, json={"num": body.num})

        nacl_response = ec2_client.describe_network_acls(NetworkAclIds=[NACL_ID])

        return nacl_response

    except Exception:
        return "Error in processing request"
```


### 3. Write a Setup Script and scp It to the Instances

#### Setup Script `setup.sh`

```bash
#!/bin/bash

# Download 
yum update -y
yum install -y python3
yum install -y python3-pip

# Create the app folder
mkdir -p /home/ec2-user/app
cd /home/ec2-user/app

# Set up env
python3 -m venv .venv
source .venv/bin/activate
pip3 install "fastapi[standard]" httpx
```

#### scp

```bash
for ip in xxx.xxx.xxx.xxx yyy.yyy.yyy.yyy
do
  scp -i <pem-file> receiver.py setup.sh ec2-user@$ip:/home/ec2-user/ && \
  ssh -i <pem-file> ec2-user@$ip "chmod +x setup.sh && sudo ./setup.sh"
done
```

### 4. `ssh` into instances to spin up the services 

```bash
ssh -i <pem-file> ec2-user@ip
source /home/ec2-user/app/.venv/bin/activate && \
fastapi run receiver.py --port 8080
```

## 3. Set up NACL for the Data Access Subnet

### 0. (Optional) Tag subnets

```bash
# For the Data Access subnet -> Subnet1
aws ec2 create-tags \
--resources subnet-XXXXXXX \
--tags Key=Name,Value=Subnet1 

# For the Receiver subnet -> Subnet2
aws ec2 create-tags \
--resources subnet-XXXXXXX \
--tags Key=Name,Value=Subnet2
```

### 1. Get `VpcId`

```bash
aws ec2 describe-vpcs \
--filters Name=isDefault,Values=true \
--query "Vpcs[0].VpcId"
```

### 2. Create an NACL for the data access subnet

```bash
aws ec2 create-network-acl \
--vpc-id vpc-XXXXXXX \
--tag-specifications "Tags=[{Key=Name,Value=elb-acl}]"
```

### 3. Get the current `NetworkAclAssociationId` for our data access subnet

```bash
aws ec2 describe-network-acls \
--filters "Name=association.subnet-id,Values=subnet-XXXXXXX" \
--query "NetworkAcls[].Associations[?SubnetId=='subnet-XXXXXXX'].NetworkAclAssociationId" \
--output text
```

### 4. Replace the subnet's NACL to our newly created one

```bash
aws ec2 replace-network-acl-association \
--network-acl-id acl-XXXXXXXX \
--association-id aclassoc-XXXXXXX 
```

- You should get a new association id after this command

### 5. Set up inbound rules

> [!WARNING]
>
> As `NACL` is stateless, you have to set up inbound (`ingress`) and outbound `egress` rules to ensure proper access control.

#### Egress

```bash
aws ec2 create-network-acl-entry \
--network-acl-id acl-XXXXXXXX \ 
--rule-number 100 \
--protocol tcp \
--port-range From=0,To=65535 \
--cidr-block  0.0.0.0/0 \
--rule-action allow \
--egress
```

#### SSH

```bash
aws ec2 create-network-acl-entry \
--network-acl-id acl-XXXXXXXX \
--rule-number 100 \
--protocol tcp \
--port-range From=22,To=22 \
--cidr-block  0.0.0.0/0 \
--rule-action allow \
--ingress
```

#### Port 8080

```bash
# get the cidr block of your receiver subnet 
aws ec2 describe-subnets \
--filters Name=subnet-id,Values=subnet-XXXXXXX \
--query "Subnets[0].CidrBlock"

aws ec2 create-network-acl-entry \
--network-acl-id acl-XXXXXXXX \ 
--rule-number 200 \
--protocol tcp \
--port-range From=8080,To=8080 \
--cidr-block  172.31.16.0/20 \
--rule-action allow \
--ingress
```

#### Port 5000

```bash
aws ec2 create-network-acl-entry \
--network-acl-id acl-XXXXXXXX \
--rule-number 300 \
--protocol tcp \
--port-range From=5000,To=5000 \
--cidr-block  0.0.0.0/0 \
--rule-action allow \
--ingress
```

#### Ensure everything is set up correctly

```bash
aws ec2 describe-network-acls \
--network-acl-ids acl-XXXXXXX \
--query "NetworkAcls[0].Entries"
```

### 6. Set up security group authorization

#### 1. Create a new security group for data access service

```bash
aws ec2 create-security-group \
--group-name data-access-sg \
--description "sg for data access service"

aws ec2 authorize-security-group-ingress \
--group-name data-access-sg \
--protocol tcp \
--port 5000 \
--cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
--group-name data-access-sg \
--protocol tcp \
--port 8080 \
--cidr 172.31.16.0/20
```

#### 2. Create a new security group for receiver services

```bash
aws ec2 create-security-group \
--group-name receiver-sg \
--description "sg for receiver service" 

aws ec2 authorize-security-group-ingress \
--group-name receiver-sg \
--protocol tcp \
--port 8080 \
--cidr 0.0.0.0/0
```


#### 3. Attach the new sg to the respective instances

```bash
# find out the network interface
aws ec2 describe-instances \
--instance-ids i-XXXXXXX \
--query "Reservations[].Instances[].NetworkInterfaces[].NetworkInterfaceId" \
--output text

# modify the network interface with new sg
aws ec2 modify-network-interface-attribute \
--network-interface-id eni-XXXXXXX  \
--groups sg-XXXXXXX sg-YYYYYYY  
```

> [!WARNING] 
>
> `modify-network-interface-attribute` will overwrite the current security groups, so you have to include all the security groups that you want.

## 4. Create a Load Balancer

### 1. Create a security group for the load balancer

```bash
aws ec2 create-security-group \
--group-name load-blancer-sg \
--description "sg for load balancer"

# allow traffic from anywhere
aws ec2 authorize-security-group-ingress \
--group-name load-balancer-sg \
--protocol tcp \
--port 80 \
--cidr 0.0.0.0/0
```

### 2. Create a load balancer

```bash
aws elbv2 create-load-balancer \
--name data-access-load-balancer \
--type application \
--subnets subnet-XXXXXXX subnet-XXXXXXX \
--security-groups sg-XXXXXXX
```


> [!TIP]
>
> Remember to copy the load balancer arn

### 3. Create a target group for receivers

```bash
aws elbv2 create-target-group \
--name receiver-tg \
--protocol HTTP \
--port 8080 \
--vpc-id vpc-XXXXXXX \
--target-type instance
```

> [!TIP]
>
> Remember to copy the target group arn


### 4. Register EC2 instances

```bash
aws elbv2 register-targets \
--target-group-arn <your-tg-arn> \
--targets Id=i-XXXXXXX Id=i-YYYYYYY 
```

### 5. Create a listener

```bash
aws elbv2 create-listener \
--load-balancer-arn <load-balancer-arn> \
--protocol HTTP \
--port 80 \
--default-actions Type=forward,TargetGroupArn=<target-group-arn>
```


### 6. Get load balancer DNS 

```bash
aws elbv2 describe-load-balancers \
--name data-access-load-balancer \
--query "LoadBalancers[0].DNSName"
```

### 7. Test it with `curl`

```bash
curl http://<dns-name>
```

---

## Part 2 - Auto Scaling Group

## 1. Write a Python script based on the given requirements

```python
from fastapi import FastAPI
import subprocess
import socket

app = FastAPI()


@app.post("/")
def stress_cpu():
    sub = subprocess.Popen(["python3", "./stress_cpu.py"])
    return {"status": "success"}


@app.get("/")
def get_private_ip():
    return socket.gethostname()
```

> [!TIP]
> 
> The setup process is the same as [here](#setup-script-setupsh) 

## 2. Generate a GitHub Access Token

> [!IMPORTANT]
>
> Just follow [this](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## 3. Create an Internet Facing Load Balancer

> [!NOTE]
>
> By default, the load balancer should be `internet-facing`, but we include the `--scheme` flag just in case.

### 1. Create a load balancer

```bash
aws elbv2 create-load-balancer \
--name asg-load-balancer \
--type application \
--subnets subnet-XXXXXXX \
--security-groups sg-XXXXXXX \
--scheme internet-facing
```

### 2. Create a target group

```bash
aws elbv2 create-target-group \
--name asg-tg \
--protocol HTTP \
--port 8080 \
--vpc-id vpc-XXXXXXX \
--target-type instance
```

### 3. Create a listener

```bash
aws elbv2 create-listener \
--protocol HTTP \
--port 80 \
--load-balancer-arn <load-balancer-arn> \
--default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

## 4. Create a Launch Template

### 1. Copy the provided script and paste your token

```bash
#!/bin/bash
export HOME=/home/ec2-user
sudo yum update -y
sudo yum install stress-ng -y
sudo yum install htop -y
sudo yum install python3-pip -y
pip3 install "fastapi[standard]" 
sudo yum install git -y
cd /home/ec2-user
git clone https://<github-personal-access-token>@github.com/username/repository_name
cd /home/ec2-user/YOUR_CODECOMMIT_REPO_NAME
python3 serve.py
```

### 2. Base64 encode it

```bash
base64 -i launch_template.sh -o launch_template.txt
```

### 3. Create a template

```bash
aws ec2 create-launch-template \
  --launch-template-name asg-launch-template \
  --version-description "v1" \
  --launch-template-data '{
  "ImageId": "ami-06cce67a5893f85f9",
  "InstanceType": "t2.micro",
  "KeyName": "ec2-keypair",
  "SecurityGroupIds": [],
  "UserData": "BASE64_ENCODED_SCRIPT"
}'
```

## 5. Create an Auto-scaling Group

```bash
aws autoscaling create-autoscaling-group \
--auto-scaling-group-name my-asg \
--launch-template LaunchTemplateName=asg-launch-template,Version=1 \
--min-size 0 \
--max-size 3 \
--desired-capacity 1 \
--default-instance-warmup 300 \
--vpc-zone-identifier "subnet-XXXXXXX,subnet-YYYYYY" \
--target-group-arns <your-arn>
```

## 6. Update the scaling policy

- What we want:
  - `CPU > 50%`: scale out 
  - `CPU < 50%`: scale in

```bash
aws autoscaling put-scaling-policy \
--auto-scaling-group-name my-asg \
--policy-name cpu-target-tracking \
--policy-type TargetTrackingScaling \
--target-tracking-configuration '{
      "PredefinedMetricSpecification": {
          "PredefinedMetricType": "ASGAverageCPUUtilization"
      },
      "TargetValue": 50.0
  }'
```

## 7. Test

- For the remaining parts, here are some useful commands for you test out your auto scaling groups

### Get load balancer's domain name

```bash
aws elbv2 describe-load-balancers \
--name asg-load-balancer \
--query "LoadBalancers[0].DNSName"
```

### List out instance ids and their public address

```bash
aws ec2 describe-instances \
  --instance-ids $(aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names my-asg \
    --query "AutoScalingGroups[0].Instances[].InstanceId" \
    --output text) \
  --query "Reservations[].Instances[].{ID:InstanceId,PublicIP:PublicIpAddress}" \
  --output table
```

### Send requests iteratively

```bash
for i in {1..10}; do
  curl -X POST http://domain-name 
done
```
