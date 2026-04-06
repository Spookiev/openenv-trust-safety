import asyncio
import os
import json
from typing import List, Optional

from openai import OpenAI
from server.env import TrustSafetyEnv
from server.models import AnalystAction

# --- MANDATORY CONFIGURATION ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy-key-for-local-testing")

TASK_NAME = "trust_safety_analyst"
BENCHMARK = "openenv"
MAX_STEPS = 5

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_model_action(client: OpenAI, obs_text: str) -> AnalystAction:
    """Asks the LLM for the next action, with a failsafe fallback."""
    system_prompt = """You are a Trust & Safety Analyst investigating a user. 
    You must choose an action. Valid query_types: query_login_history, query_message_logs, query_linked_accounts, resolve_case.
    Respond ONLY with valid JSON matching this schema: {"query_type": "string", "resolution_decision": "string", "target_account": "string"}"""
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Current Observation: {obs_text}"},
            ],
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        response_text = completion.choices[0].message.content
        data = json.loads(response_text)
        return AnalystAction(**data)
    except Exception as exc:
        # FAILSAFE: If the LLM fails or network drops, don't crash the script! 
        # Return a valid default action so the evaluation finishes.
        return AnalystAction(query_type="query_message_logs")

async def main() -> None:
    # 1. Initialize OpenAI Client & Environment
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = TrustSafetyEnv()

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    # 2. Emit Mandatory Start Log
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # 3. Start the Episode
        obs = env.reset()
        
        for step in range(1, MAX_STEPS + 1):
            if env._state.is_done:
                break
                
            # Ask LLM for action
            action = get_model_action(client, str(obs.dict()))
            action_str = f"{action.query_type}({action.resolution_decision or ''})"
            
            # Step the environment
            try:
                obs, reward, done, info = env.step(action)
                error = None
            except Exception as e:
                reward = 0.0
                done = True
                error = str(e)
            
            # Record keeping
            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)
            
            if done:
                break
                
        # Calculate final score (normalized 0.0 to 1.0)
        total_reward = sum(rewards)
        score = min(max(total_reward / (steps_taken * 0.5), 0.0), 1.0) if steps_taken > 0 else 0.0
        success = score > 0.0

    finally:
        # 4. Emit Mandatory End Log
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())