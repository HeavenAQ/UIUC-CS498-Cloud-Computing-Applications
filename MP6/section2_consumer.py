from typing import Any
from kafka import KafkaConsumer
import json
import happybase  # HBase Client
import time
import socket
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from kafka.sasl.oauth import AbstractTokenProvider
from flask import Flask, jsonify
import threading

# Flask app for health check
app = Flask(__name__)
is_ready = False  # will become True when consumer is fully initialized


@app.route("/health", methods=["GET"])
def health_check():
    if is_ready:
        return jsonify({"status": "UP"}), 200
    return jsonify({"status": "INITIALIZING"}), 503


def start_flask():
    app.run(host="0.0.0.0", port=5000)


# Start Flask in a background thread
threading.Thread(target=start_flask, daemon=True).start()


# =======================
# TODO: Implement IAM Authentication
# =======================
class MSKTokenProvider(AbstractTokenProvider):
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token("us-east-1")
        return token


tp = MSKTokenProvider()

# TODO: Provide your Kafka broker private endpoint here
KAFKA_BROKERS = [
    "b-1.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098",
    "b-2.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098",
]
TOPIC = "social_engagement"

# TODO: HBase Configuration
HBASE_HOST = "172.31.22.189"
HBASE_PORT = 9090
TABLE_NAME = "post_engagement"

# Connect to HBase
hbase_conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT)


def get_hbase_table():
    global hbase_conn
    try:
        if not hbase_conn.transport.isOpen():
            hbase_conn.transport.open()
    except Exception:
        print("Reconnecting to HBase...")
        hbase_conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT)
    return hbase_conn.table(TABLE_NAME)


# =======================
# TODO: Store messages in HBase
# =======================
def store_in_hbase(data: dict[Any, Any]):
    try:
        # TODO:
        # Extract 'post_id', 'user_id', 'likes', 'comments', and 'timestamp' from the incoming message.
        # Validate that 'post_id' and 'user_id' are present; skip message if invalid.
        # Construct a unique row key using 'post_id' and 'timestamp' to store the data in HBase.
        # Connect to HBase table and insert the extracted data into appropriate columns.
        # Add logging to confirm successful storage or identify errors clearly if storing fails.

        # code here
        if data.get("post_id") is None or data.get("user_id") is None:
            return None

        table = get_hbase_table()
        table.put(
            f"{data['user_id']}_{data['timestamp']}".encode(),
            {
                b"engagement:post_id": f"{data['post_id']}".encode(),
                b"engagement:user_id": f"{data['user_id']}".encode(),
                b"engagement:likes": f"{data['likes']}".encode(),
                b"engagement:comments": f"{data['comments']}".encode(),
                b"engagement:timestamp": f"{data['timestamp']}".encode(),
            },
        )

        print("Successfully stored the message")
    except Exception as e:
        print(f"Error storing engagement in HBase: {e}")


# =======================
# TODO: Kafka Consumer setup, group_id should be engagement_analytics_group, auto_offset_reset should be set to latest
# =======================
try:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKERS,
        security_protocol="SASL_SSL",
        sasl_mechanism="OAUTHBEARER",
        sasl_oauth_token_provider=tp,
        client_id=socket.gethostname(),
        auto_offset_reset="latest",
        group_id="engagement_analytics_group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )
    print(f"Listening for engagement events on topic: {TOPIC}...")
    is_ready = True  # Set consumer readiness to True after successful setup
except Exception as e:
    print(f"Failed to connect to Kafka: {e}")


# Consume messages and store in HBase
if is_ready:
    for message in consumer:
        try:
            print(f"Received: {message.value}")
            store_in_hbase(message.value)
            time.sleep(1)
        except json.JSONDecodeError:
            print("Error decoding JSON message. Skipping...")
        except Exception as e:
            print(f"Unexpected error: {e}")
