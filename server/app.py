from fastapi import FastAPI
from openenv.core.env_server import create_fastapi_app
from .env import TrustSafetyEnv

# This magically wraps your env into a FastAPI app with /reset, /step, /state
app = create_fastapi_app(TrustSafetyEnv)

# Mandatory Hackathon Endpoints
@app.get("/baseline")
async def get_baseline():
    return {"score": 0.0, "message": "Baseline inference will be executed via inference.py"}

@app.get("/grader")
async def get_grader():
    return {"score": 0.0, "message": "Grader logic pending teammate implementation"}

@app.get("/tasks")
async def get_tasks():
    return {"tasks": ["easy_phishing", "med_dispute", "hard_fraud_ring"]}