import uvicorn
from fastapi import FastAPI
from openenv.core.env_server import create_fastapi_app
from .env import TrustSafetyEnv
from .models import AnalystAction, CaseObservation

app = create_fastapi_app(TrustSafetyEnv, AnalystAction, CaseObservation)

@app.get("/baseline")
async def get_baseline():
    return {"score": 0.0, "message": "Baseline inference will be executed via inference.py"}

@app.get("/grader")
async def get_grader():
    return {"score": 0.0, "message": "Grader logic pending teammate implementation"}

@app.get("/tasks")
async def get_tasks():
    return {"tasks": ["easy_phishing", "med_dispute", "hard_fraud_ring"]}

# --- ADDED FOR DEPLOYMENT REQUIREMENTS ---
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == '__main__':
    main()