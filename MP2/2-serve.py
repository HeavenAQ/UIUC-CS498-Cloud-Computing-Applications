from fastapi import FastAPI
import subprocess
import socket

app = FastAPI()


@app.post("/")
def stress_cpu():
    sub = subprocess.Popen(["python3", "./stress_cpu.py"])
    return {"status": "success"}


@app.get("/")
def get_private_ip():
    return socket.gethostname()
