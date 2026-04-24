import json
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor


http = urllib3.PoolManager()
CONSUMER_URL = "http://184.72.132.199:5000/consume"
HEALTH_URL = "http://184.72.132.199:5000/health"


STAGES = [
    {"rate": 50, "duration": 10},
    {"rate": 100, "duration": 10},
    {"rate": 200, "duration": 10},
]


def send_request(counter):
    try:
        response = http.request(
            "POST",
            CONSUMER_URL,
            body=json.dumps({"message": f"load-{counter}"}),
            headers={"Content-Type": "application/json"},
            timeout=2.0,
        )
        print(f"[{counter}] Status: {response.status}")
    except Exception as e:
        print(f"[{counter}] ERROR: {str(e)}")


def is_consumer_healthy():
    try:
        r = http.request("GET", HEALTH_URL, timeout=2.0)
        return r.status == 200
    except Exception as e:
        print(f"[HEALTH CHECK FAILED] {str(e)}")
        return False


def lambda_handler(event, context):
    counter = 0
    for idx, stage in enumerate(STAGES):
        total_requests = int(stage["rate"] * stage["duration"])
        interval = 1.0 / stage["rate"]

        print(
            f"--- Starting Stage {idx + 1}: {stage['rate']} req/sec for {stage['duration']}s ---"
        )
        with ThreadPoolExecutor(max_workers=stage["rate"]) as executor:
            start = time.time()
            for i in range(total_requests):
                executor.submit(send_request, counter)
                counter += 1
                time.sleep(interval)
            end = time.time()
            print(f"Stage {idx + 1} done in {end - start:.2f} seconds")

        # Check consumer health
        if not is_consumer_healthy():
            print("Consumer is down. Stopping load test early.")
            return {
                "status": "consumer_unhealthy",
                "stopped_stage": idx + 1,
                "sent_messages": counter,
            }

    return {"status": "done", "sent_messages": counter}
