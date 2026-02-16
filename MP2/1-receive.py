from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import boto3

app = FastAPI()

DATA_ACCESS_SERVICE_GET_URL = "http://172.31.47.161:5000"
DATA_ACCESS_SERVICE_POST_URL = "http://172.31.47.161:8080/"
NACL_ID = "acl-069d00e3d86bb8bd1"
AWS_REGION = "ap-northeast-1"

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
