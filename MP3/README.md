# AWS Lambda Function + API Gateway + Lex + DyanmoDB

## Overview

This assignment creates a `Lambda` function to perform shortest distance search with the breadth-first search (`BFS`) algorithm and store the paths and distances to the `DynamoDB`. The API endpoint is provided by the `API Gateway` while Lex is used as a chatbot interface. 


## 0. Setup

> [!WARNING] 
>
> Given that `Lex` is only provided in `us-east-1` and `us-west-2`, this sets the region to `us-east-1` first.

1. Change the region to `us-east-1`

```bash
aws configure set region us-east-1
```

## 1. BFS Script

### 1-1. Set up Your Environment

```bash
# --bare for not initializing as a git repo
uv init . --bare
uv add pytest boto3 "boto3-stubs[dynamodb]"
source .venv/bin/activate
```


### 1-2. Write Your Lambda Function Based on the Requirements

- Save it as `lambda_function.py`.

```python
import json
import boto3

def lambda_handler(event: str, context: Any):
    # event will be a stringified json object, so load it as a python dict first.
    body = json.loads(event)
    
    # write your code based on the assignment 
```

> [!IMPORTANT]
>
> - If you need some help, check my `lambda_function.py` file. **DO NOT** copy and paste it. 
> - If you only want to know how to use `DynamoDB`, take a look at [this](https://docs.aws.amazon.com/boto3/latest/guide/dynamodb.html).



### 1-3. (Optional) Write Unit Tests for Your Code

```python
import json
import lambda_func

def test_lambda_func():
    event = json.dumps(
        {"graph": "Chicago->Urbana,Urbana->Springfield,Chicago->Lafayette"}
    )
    res = lambda_func.lambda_handler(event, context)

    # add your own assertions here
    assert res.get("statusCode") == 200
```

### 1-4. Run `pytest` to Verify It

```bash
pytest -v
```

### 1-5 Zip Your Code Files with Dependencies

```bash
uv pip freeze > requirements.txt
mkdir lambda && cd lambda
cp ../lambda_function.py .
pip install -r ../requirements.txt -t .
zip -r ../lambda.zip . 
```


## 2. Lambda Function

### 2-1. Create a Trust Policy File

- Save it as `trust-policy.json`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 2-2. Create Role and Attach Policies

```bash
aws iam create-role \
--role-name lambda-role \
--assume-role-policy-document file://trust-policy.json
```

```bash
for policy in \
arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
do
    aws iam attach-role-policy \
    --role-name lambda-role \
    --policy $policy
done
```

### 2-3. Create a Lambda Function

```bash
aws lambda create-function \
  --function-name shortest_path_bfs \
  --runtime python3.14 \
  --role arn:aws:iam::<your-account-id>:role/lambda-role \
  --handler lambda_func.lambda_handler \
  --zip-file fileb://lambda.zip
```

## 3. API Gateway

### 3-1. Create an API

```bash
aws apigatewayv2 create-api \
--name shortest-path-bfs \
--protocol-type HTTP
```

> [!TIP]
>
> Copy your `ApiId`

### 3-2. Get Your Lambda Function ARN and Create the Integration

```bash
# Get your lambda function arn
aws lambda get-function \
--function-name shortest_path_bfs \
--query "Role" \
--output text

# integrate them
aws apigatewayv2 create-integration \
--api-id <your-api-id> \
--integration-type AWS_PROXY \
--integration-uri <your-lambda-arn> \
--payload-format-version 2.0
```

> [!TIP]
>
> Copy your `IntegrationId`.

### 3-3. Create a `POST` Route

```bash
aws apigatewayv2 create-route \
  --api-id <your-api-id> \
  --route-key "POST /" \
  --target integrations/<your-integration-id>
```


### 3-4. Grant Permission

```bash
aws lambda add-permission \
  --function-name my-function \
  --statement-id apigateway-access \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:<region>:<your-account-id>:<your-api-id>/*/*"
```

> [!IMPORTANT]
>
> You can follow the same steps to create the lambda function for `lex2`

## 4. Lex

1. Create a draft bot
2. Create locale
3. Create intent
4. Create slots
5. Build locale
6. Create a bot version
7. Create a bot alias
8. Deploy the bot

### 4-1. Create a Lex Bot

```bash
aws lexv2-models create-bot \
  --bot-name CityDistanceBot \
  --role-arn arn:aws:iam::<your-account-id>:role/LexServiceRole \
  --data-privacy childDirected=false \
  --idle-session-ttl-in-seconds 300
```

> [!TIP]
>
> Copy your `botId`

### 4-2. Create a Bot Locale

```bash
aws lexv2-models create-bot-locale \
  --bot-id XXXXXXX \
  --bot-version DRAFT \
  --locale-id en_US \
  --nlu-intent-confidence-threshold 0.40
```

### 4-3. Create an Intent with Utterances

```bash
aws lexv2-models create-intent \
  --bot-id CXQJBTBUOK \
  --bot-version DRAFT \
  --locale-id en_US \
  --fulfillment-code-hook '{"enabled":true}' \
  --intent-name GetDistanceIntent \
  --sample-utterances \
      "utterance='What is the distance from {source} to {destination} ?'"
```

> [!WARNING]
>
> The slots (i.e. `{destination}`) should be enclosed with white spaces. Otherwise, the bot will fail to be built.


### 4-4. Create Slots


```bash
aws lexv2-models create-slot \
  --bot-id XXXXXXX \
  --bot-version DRAFT \
  --locale-id en_US \
  --intent-id XXXXXXX \
  --slot-type AMAZON.City \
  --slot-name source \
  --value-elicitation-setting '{
    "slotConstraint":"Required",
    "promptSpecification": {
        "messageGroups": [
            {
                "message": {
                    "plainTextMessage": {
                        "value": "Source?"
                    }
                }
            }
        ],
        "maxRetries": 2
    }
}'

aws lexv2-models create-slot \
  --bot-id XXXXXXX \
  --bot-version DRAFT \
  --locale-id en_US \
  --intent-id XXXXXXX \
  --slot-type AMAZON.City \
  --slot-name destination \
  --value-elicitation-setting '{
    "slotConstraint":"Required",
    "promptSpecification": {
        "messageGroups": [
            {
                "message": {
                    "plainTextMessage": {
                        "value": "Destination?"
                    }
                }
            }
        ],
        "maxRetries": 2
    }
}'
```

### 4-5. Build Bot Locale

```bash
aws lexv2-models build-bot-locale \
  --bot-id <bot-id> \
  --bot-version DRAFT \
  --locale-id en_US
```

### 4-6. Create a Bot Version

```bash
aws lexv2-models create-bot-version \
  --bot-id <bot-id> \
  --bot-version-locale-specification '{"en_US":{"sourceBotVersion":"DRAFT"}}'
```

### 4-7. Create a Bot Alias

```bash
aws lexv2-models create-bot-alias \
  --bot-id CXQJBTBUOK \
  --bot-version 1 \
  --bot-alias-name prod \
  --bot-alias-locale-settings \
  '{
      "en_US": {
          "enabled": true,
          "codeHookSpecification": {
              "lambdaCodeHook": {
                  "lambdaARN": "arn:aws:lambda:REGION:<your-account-id>:function:<your-function>",
                  "codeHookInterfaceVersion": "1.0"
              }
          }
      }
  }'
```

### 4-8. Add Permission to Lambda Function and Link It to the Lex Bot

```bash
aws lambda add-permission \
  --function-name distance_retrieval \
  --statement-id lexv2-invoke \
  --action lambda:InvokeFunction \
  --principal lexv2.amazonaws.com \
  --source-arn "arn:aws:lex:us-east-1:<your-account-id>:bot-alias/CXQJBTBUOK/*"

aws lexv2-models update-bot-alias \
  --bot-id <bot-id> \
  --bot-alias-id <bot-alias-id> \
  --bot-version <version-number> \
  --bot-alias-locale-settings '{
    "en_US": {
      "enabled": true,
      "codeHookSpecification": {
        "lambdaCodeHook": {
          "lambdaARN": "arn:aws:lambda:us-east-1:<your-account-id>:function:distance_retrieval",
          "codeHookInterfaceVersion": "1.0"
        }
      }
    }
  }'
```

### 4-9 Deploy Lex Bot

#### 4-9-1. Create an workload identity pool

```bash
aws cognito-identity create-identity-pool \
--identity-pool-name LexGuestPool \
--allow-unauthenticated-identities
```


> [!TIP]
>
> Copy `IdentityPoolId`

#### 4-9-2. Create an IAM role for guest users

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "cognito-identity.amazonaws.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "cognito-identity.amazonaws.com:aud": "<workload-identity-id>"
        },
        "ForAnyValue:StringLike": {
          "cognito-identity.amazonaws.com:amr": "unauthenticated"
        }
      }
    }
  ]
}
```

#### 4-9-3. Create an IAM role and attach policies

```bash
aws iam create-role \
--role-name guest-access-role \
--assume-role-policy-document file://workload-identity-trust-policy.json

for policy in \
arn:aws:iam::aws:policy/AmazonLexRunBotsOnly \
arn:aws:iam::aws:policy/AmazonPollyReadOnlyAccess
do
    aws iam attach-role-policy \
    --role-name guest-access-role \
    --policy $policy
done
```

#### 4-9-4. Attach the role to workload identity

```bash
aws cognito-identity set-identity-pool-roles \
  --identity-pool-id <your-identity-pool-id> \
  --roles '{"unauthenticated":"arn:aws:iam::<your-account-id>:role/guest-access-role"}'
```
