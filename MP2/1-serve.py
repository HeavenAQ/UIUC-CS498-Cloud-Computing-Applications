import os
from fastapi import FastAPI
from typing import Literal
from pydantic import BaseModel
import asyncio

app_read = FastAPI()
app_update = FastAPI()
seed_lock = asyncio.Lock()
seed_file = "seed.txt"


class UpdateSeedReq(BaseModel):
    num: int


class UpdateSeedRes(BaseModel):
    num: int
    status: Literal["ok", "error"]


@app_update.post("/")
async def set_seed(body: UpdateSeedReq):
    global seed
    async with seed_lock:
        with open(seed_file, "w") as f:
            _ = f.write(f"{body.num}")
        return UpdateSeedRes(num=body.num, status="ok")


@app_read.get("/")
async def get_seed():
    async with seed_lock:
        if not os.path.exists(seed_file):
            return 0
        else:
            with open(seed_file, "r") as f:
                return f.read()
