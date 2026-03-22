# Full-stack Development with AWS

## 1. Create Frontend S3 Bucket

### 1.1. Create a bucket

```bash
aws s3 mb "s3://my-frontend-asset"
make_bucket: my-cca-bucket

```

### 1.2. Create a bucket policy to allow public access

- This is saved as `bucket-policy.json`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-frontend-asset/*"
    }
  ]
}
```

### 1.3. Update s3 bucket's public access policy

```bash
# Turn off public access block first
aws s3api put-public-access-block \
  --bucket my-frontend-asset \
  --public-access-block-configuration \
BlockPublicAcls=false,\
IgnorePublicAcls=false,\
BlockPublicPolicy=false,\
RestrictPublicBuckets=false

# Add new policy to the s3 bucket
aws s3api put-bucket-policy \
  --bucket my-frontend-asset \
  --policy file://bucket-policy.json
```

