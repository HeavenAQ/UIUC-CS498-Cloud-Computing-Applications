# Homework 7

## 1. Set up an EC2 instance

### 1.1. Get an image for later EC2 instance credation

```bash
aws ec2 describe-images \
--owners amazon \
--filters "Name=name,Values=al2023-ami-*" \
--query "Images[*].[ImageId,Name]" \
--output table
```

- You should see an output like this

```bash
-------------------------------------------------------------------------------------------
|                                     DescribeImages                                      |
+------------------------+----------------------------------------------------------------+
|  ami-00ab017cba8471ebf |  al2023-ami-ecs-neuron-hvm-2023.0.20250821-kernel-6.1-x86_64   |
|  ami-00d65eac88e8a5816 |  al2023-ami-ecs-hvm-2023.0.20240312-kernel-6.1-arm64           |
|  ami-0096aa2831d78b30c |  al2023-ami-ecs-hvm-2023.0.20250516-kernel-6.1-x86_64          |
|  ami-0066fc6d0f069eeea |  al2023-ami-ecs-hvm-2023.0.20260108-kernel-6.1-x86_64          |
|  ami-00b51e1266717f944 |  al2023-ami-ecs-hvm-2023.0.20250613-kernel-6.1-arm64           |
|  ami-00afec874ecbf7b2c |  al2023-ami-ecs-neuron-hvm-2023.0.20241003-kernel-6.1-x86_64   |
...
```

- Copy an image id that you want to use. 
-  In my case, I chose `ami-06cce67a5893f85f9` as it does not require extra cost and support the instance type `t2.micro` (a free-tier instance).

### 1.2. Create a key pair for `SSH` connection

```bash
aws ec2 create-key-pair \
  --key-name my-keypair \
  --query "KeyMaterial" \
  --output text > my-keypair.pem
chmod 400 my-keypair.pem
```


### 1.3. Create a security group

```bash
aws ec2 create-security-group \
--group-name my-sg \
--description "SSH Access for EC2 instances"
```
- This allows you to specify the `user`, `protocol`, and `port` that your EC2 instance is allowed to have communication.

### 1.4. Allow access through `ssh` and `tcp` through port `22`, `5000`, and `9098` respectively

```bash
aws ec2 authorize-security-group-ingress \
--group-name my-sg \
--protocol tcp \
--port 22 \
--cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
--group-name my-sg \
--protocol tcp \
--port 5000 \
--cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
--group-name my-sg \
--protocol tcp \
--port 9092 \
--cidr 0.0.0.0/0
```

> [!WARNING]
> This may not be the best practice for as the allowed inbound address range is too large, but it works for this assignment.

### 1.5. Start an instance

```bash
aws ec2 run-instances \
--image-id  ami-06cce67a5893f85f9 \
--instance-type t2.micro \
--key-name my-keypair \
--security-groups my-sg \
--count 1 \
--tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=MyCLIInstance}]"
```

> [!TIP]
> 
> After you successfully create an instance, copy the instance id specified by `"InstanceId"`. It should be in the format of `i-XXXXXXXXXXXXXXXXX`.


### 1.6 `scp` the finished `section1_consumer.py` to the instance

- On your local host:

```bash
pip freeze > requirements.txt # remember to remove the dependency versions
scp -i my-keypair.pem section1_consumer.py requirements.txt ec2-user@<ip-address>:/home/ec2-user
```

- On your EC2 instance:

```bash
sudo yum install htop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## 2. Create a Lambda Function

### 2.1. Zip the file

```bash
mkdir section1
cp section1_producer.py section1/lambda_function.py
pip install urllib3 -t section1/
cd section1
zip -r ../section1_producer.zip .
```

### 2.2. Create a IAM Role for lambda function execution 

#### 1. Create a policy file

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```


#### 2.2. Create the role
```bash
aws iam create-role \
--role-name mp6-lambda \
--assume-role-policy-document file://lambda_function_policy.json
```

#### 2.3. Attach function execution policy

```bash
aws iam attach-role-policy \
--role-name mp6-lambda \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

#### 2.4. Create a lambda function

```bash
aws lambda create-function \
  --function-name mp6-section1-producer \
  --runtime python3.14 \
  --role <role-arn> \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://section1_producer.zip \
  --timeout 60 \
  --memory-size 128
```

#### 2.5. Invoke the lambda function to stress test the EC2 instance

```bash
aws lambda invoke \
  --function-name mp6-section1-producer \
  --payload '{}' \
  --log-type Tail \
  response.json \
  --query 'LogResult' \
  --output text | base64 --decode
```

> [!TIP]
>
> If you need to update your code, you can use the following command:
>
> ```bash 
> aws lambda update-function-code \
> --function-name mp6-section1-producer \
> --zip-file fileb://section1_producer.zip
> ```

## 2. Configure Kafka to Handle Traffic 

### 2.1. Create an MSK cluster

#### 2.1.1. Get 2 subnets from different AZ zones

```bash
aws ec2 describe-subnets
```

> [!WARNING]
> Don't pick the one in `us-east-1e`. That AZ does not support kafka cluster.

#### 2.1.2. Get a security group id with a proper TCP inbound

```bash
aws ec2 describe-security-groups
```

#### 2.1.3. Create a `msk` config file

```json
{
  "ClusterName": "mp6-kafka-cluster",
  "Provisioned": {
    "KafkaVersion": "3.6.0",
    "NumberOfBrokerNodes": 2,
    "BrokerNodeGroupInfo": {
      "InstanceType": "kafka.t3.small",
      "ClientSubnets": ["subnet-YYYYYYY", "subnet-XXXXXXX"],
      "SecurityGroups": ["sg-ZZZZZZZ"]
    }
  }
}
```

#### 2.1.4. Create the cluster

```bash
aws kafka create-cluster-v2 \
--cli-input-json file://msk-cluster.json
```

> [!IMPORTANT]
> Wait for 10 - 15 minutes before you proceed to the next step


#### 2.1.5. Get the bootstrap broker info

```bash
aws kafka get-bootstrap-brokers --cluster-arn <your-cluster-arn>
```


### 3. Create a bucket and upload the provided csv file

```bash
aws s3 mb "s3://uiuc-cca-new-mp6"
aws s3 cp Engagement\ Data.csv "s3://uiuc-cca-new-mp6"
```

### 4. Create a lambda function for the traffic generator

```bash
mkdir section2
cp ./traffic_generator_lambda.py ./section2/lambda_function.py
cd section2
pip install boto3 requests -t .
zip -r ../section2_generator.zip .
aws lambda create-function \
  --function-name mp6-section2-generator \
  --runtime python3.14 \
  --role <aws-role-arn> \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://section2_generator.zip \
  --timeout 300 \
  --memory-size 128
```

### 5. Create an EC2 instance as a Kafka Producer

#### 5.1. Create necessary role json files

- EC2 service

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

- Kafka Related Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "KafkaFullWriteAccess",
      "Effect": "Allow",
      "Action": [
        "kafka-cluster:Connect",
        "kafka-cluster:DescribeCluster",
        "kafka-cluster:WriteData",
        "kafka-cluster:ReadData",
        "kafka-cluster:DescribeGroup",
        "kafka:DescribeClusterV2",
        "kafka:GetBootstrapBrokers"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["kafka-cluster:DescribeGroup", "kafka-cluster:AlterGroup"],
      "Resource": "<group-arn>"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kafka-cluster:CreateTopic",
        "kafka-cluster:AlterTopic",
        "kafka-cluster:DeleteTopic",
        "kafka-cluster:DescribeTopic"
      ],
      "Resource": "topic-arn"
    }
  ]
}
```

#### 5.2. Create a role and an instance profile, attach the role to the instance profile, and create an EC2 instance and associate the instance profile to it.

```bash
# IAM Role
aws iam create-role \
--role-name mp6-ec2-msk \
--assume-role-policy-document file://ec2-service.json

aws iam attach-role-policy \
--role-name mp6-ec2-msk \
--policy-arn arn:aws:iam::aws:policy/AmazonEMRFullAccessPolicy_v2

aws iam attach-role-policy \
--role-name mp6-ec2-msk \
--policy-arn arn:aws:iam::aws:policy/AmazonMSKFullAccess

aws iam attach-role-policy \
--role-name mp6-ec2-msk \
--policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam put-role-policy \
--role-name mp6-ec2-msk \
--policy-name mp6-kafka \
--policy-document file://kafka_role.json

# Instance Profile
aws iam create-instance-profile \
--instance-profile mp6-ec2-msk-profile 

aws iam add-role-to-instance-profile \
--instance-profile mp6-ec2-msk-profile \
--role-name mp6-ec2-msk

# EC2 Instance
aws ec2 run-instances \
--image-id ami-00c24525bc6b608cb \
--instance-type t2.micro \
--key-name ec2-keypair \
--security-groups uiuc-sg \
--count 1 \
--tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=MyCLIInstance}]"

aws ec2 associate-iam-instance-profile \
--instance-id i-XXXXXXX \
--iam-instance-profile Name="mp6-ec2-msk-profile"
```

### 6. `ssh` to the instance, install the necessary dependencies, and create the topic

```bash
#!/bin/bash
# Install Java 11 and pip
sudo yum -y install wget 
sudo yum -y install java-11
sudo yum -y install python3-pip

# Install Kafka
cd /home/ec2-user
wget https://archive.apache.org/dist/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz

# Install MSK IAM Auth jar
wget https://github.com/aws/aws-msk-iam-auth/releases/download/v2.3.0/aws-msk-iam-auth-2.3.0-all.jar
mv aws-msk-iam-auth-2.3.0-all.jar kafka_2.13-3.6.0/libs/

# Configure Kafka client properties
cat <<EOT >> kafka_2.13-3.6.0/config/client.properties
security.protocol=SASL_SSL
sasl.mechanism=AWS_MSK_IAM
sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler
EOT

# Install Python packages
sudo pip3 install boto3 kafka-python aws-msk-iam-sasl-signer-python flask

# create the social_engagement topic
KAFKA_ROOT=kafka_2.13-3.6.0
BOOTSTRAP_SERVER=<your-bootstrap-server-domain-name>
$KAFKA_ROOT/bin/kafka-topics.sh \
  --create \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --command-config $KAFKA_ROOT/config/client.properties \
  --replication-factor 2 \
  --partitions 1 \
  --topic social-engagement
```

### 7. Edit your `section2_producer.py` and spin it up in the instance

### 8. Invoke your lambda producer function to test the endpoint

### 9. Verify your changes on the producer server

```bash
$KAFKA_ROOT/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
  --command-config $KAFKA_ROOT/config/client.properties \
  --broker-list $BOOTSTRAP_SERVER \
  --topic social_engagement
```

- If everything works fine, you should see sth like:

```bash
# partition 0 has 42 messages
social_engagement:0:42
```

- ec2(1): i-0c497a4f9559d1f4e
  - 184.72.132.199
- ec2(2): i-0875d8cc9d17abbe9
  - 3.84.184.136
- ec2(3): i-0156d70520fa6bec6
  - 3.90.207.252

- vpc: vpc-02d7989f95f249774
- (us-east-1a): subnet-0879782dd5ce45525
- (us-east-1b): subnet-0021c5b791ec13bbd
- security group: sg-02e4caac01d9eebf1
- cluster-arn: arn:aws:kafka:us-east-1:221840298051:cluster/mp6-msk-cluster/2edbcd22-f2b0-402b-b0b5-6dddeda969c1-21

- bootstrap-broker: b-2.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098,b-1.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098
