#!/bin/bash
# Install Java 11 and pip
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
