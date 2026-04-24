from botocore import validate
from pydantic import BaseModel
from flask_pydantic import validate
from flask import Flask
from kafka import KafkaProducer
from kafka.sasl.oauth import AbstractTokenProvider
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from typing import Any
import json
import socket

# Configuration
# Copy your Kafka broker client below
REGION = "us-east-1"
TOPIC_NAME = "social_engagement"

# TODO: Provide your Kafka broker private endpoint here
KAFKA_BROKERS = [
    "b-1.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098",
    "b-2.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098",
]


# =======================
# TODO: Implement IAM Authentication
# =======================
class MSKTokenProvider(AbstractTokenProvider):
    def token(self) -> str:
        token, _ = MSKAuthTokenProvider.generate_auth_token("us-east-1")
        return token


# =======================
# TODO: Initialize Kafka Producer
# =======================
tp = MSKTokenProvider()
producer = KafkaProducer(
    bootstrap_servers="b-2.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098,b-1.mp6mskcluster.73tosl.c21.kafka.us-east-1.amazonaws.com:9098",
    security_protocol="SASL_SSL",
    sasl_mechanism="OAUTHBEARER",
    sasl_oauth_token_provider=tp,
    client_id=socket.gethostname(),
)

# Flask App
app = Flask(__name__)


# =======================
# TODO: Flask Route to Produce Message
# =======================
class ProduceBody(BaseModel):
    topic: str
    message: Any


@app.route("/produce", methods=["POST"])
@validate()
def produce(body: ProduceBody):
    """
    The jSON payload has the format {"topic": <TOPIC-NAME>, "message": <MESSAGE>}
    """
    try:
        message = json.dumps(body.message)
        producer.send(body.topic, message.encode())
        producer.flush()
        app.logger.info("Message has been sent!")
        return {
            "status": "success",
            "message": body.message,
            "topic": body.topic,
        }, 200
    except Exception as e:
        app.logger.warning(f"Failed to send a message: {e}")
        return {
            "status": "failed",
            "message": body.message,
            "topic": body.topic,
        }, 500


# =======================
# TODO: Health Route to check health
# =======================
@app.route("/health", methods=["GET"])
def health_check():
    # code here
    return {"isStableTraffic": True, "producer_ip": socket.gethostname()}, 200


# =======================
# Flask App Runner
# =======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
