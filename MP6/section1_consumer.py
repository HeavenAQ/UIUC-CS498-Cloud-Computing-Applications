# consumer_template.py

"""
Flask Consumer Server Template
------------------------------
This template simulates a backend consumer service that receives POST requests
and processes them with simulated CPU, memory, and time load.

Your job: Fill in the TODOs to complete the consumer.
"""

from flask import Flask, request
import time
from pydantic import BaseModel
from flask_pydantic import validate

app = Flask(__name__)

# Global list to simulate memory usage
load_list = []


# Define the /consume route
class ConsumeBody(BaseModel):
    message: str


@app.route("/consume", methods=["POST"])
@validate()
def consume(body: ConsumeBody):
    """
    This endpoint simulates a message consumer:
    - Accepts POST requests with JSON payload.
      The JSON payload is of the format {"message": "load-i"}, where i is the message counter.
      You may use this for logging purposes only.
    - Simulates CPU usage (e.g., looping or math operations).
    - Optionally simulates memory usage by appending to a global list.
    - Sleeps for a short time to simulate delay.
    """

    # TODO
    # Parse the incoming JSON data
    message = body.message
    app.logger.info(message)

    # Simulate CPU work
    # Try computing squares in a loop (e.g., [x**2 for x in range(100000)])
    data = [str(x**2) for x in range(100000)]

    # Simulate memory pressure
    # Append a large string to the global list to simulate memory load
    load_list.append("".join(data))

    # Simulate a 100ms  delay in processing
    time.sleep(0.1)

    # Return a 200 OK response with a status message
    return {"status": "success"}, 200


# Define the /health route
@app.route("/health", methods=["GET"])
def health():
    """
    Simple health check endpoint to confirm the service is alive.
    """
    # TODO
    # Return a 200 OK with JSON status
    return {"status": "ok"}, 200


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
