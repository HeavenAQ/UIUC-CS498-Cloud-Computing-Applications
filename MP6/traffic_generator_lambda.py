import json
import time
import socket
import requests
import csv
from io import StringIO
from datetime import datetime
import boto3
import requests

# Constants
REGION = 'us-east-1'
TOPIC_NAME = "social_engagement"
BUCKET_NAME = "<your-bucket-name"
CSV_KEY = "<your-csv-file-name>"

def load_csv_from_s3(bucket, key):
    """Reads CSV data from S3 and returns list of dictionaries."""
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))
        return list(csv_reader)
    except Exception as e:
        raise Exception(f"Failed to load CSV from S3: {e}")

def lambda_handler(event, context):
    producer_ip = event.get("producer_ip")
    if not producer_ip:
        raise Exception("Missing 'producer_ip' in event input")

    PRODUCER_URL = f"http://{producer_ip}/produce"

    is_stable = event.get("isStableTraffic", True)  # Default: True

    # Determine message count and sleep interval based on traffic type
    if is_stable:
        message_count = 120
        sleep_interval = 1
        phase_label = "Stable"
    else:
        message_count = 500
        sleep_interval = 0.5
        phase_label = "Spiked"

    try:
        # Load CSV data
        engagement_data = load_csv_from_s3(BUCKET_NAME, CSV_KEY)
        total_messages = len(engagement_data)
        print(f"Loaded {total_messages} messages from s3://{BUCKET_NAME}/{CSV_KEY}")

        # Send traffic
        print(f"\n[Step] Sending {phase_label} Traffic ({message_count} messages)...\n")

        for index, row in enumerate(engagement_data[:message_count]):
            payload = {
                "topic": TOPIC_NAME,
                "message": row
            }
            try:
                response = requests.post(PRODUCER_URL, json=payload)
                print(f"[{index + 1}] Sent: {row} | Status: {response.status_code}")
            except Exception as e:
                raise Exception(f"[Error] Failed to send message #{index + 1}: {e}")

            time.sleep(sleep_interval)

        print(f"\nAll {message_count} messages sent successfully.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "traffic_type": phase_label,
                "messages_sent": min(message_count, total_messages)
            })
        }

    except Exception as e:
        print(f"Fatal error: {e}")
        raise Exception(f"Producer encountered an error: {e}")
