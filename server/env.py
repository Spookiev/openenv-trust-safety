import uuid
from typing import Tuple
from openenv.core.env_server import Environment
from .models import AnalystAction, CaseObservation, TrustState

# --- THE MOCK DATABASE ---
# This simulates the backend data the AI will uncover when it queries logs.
CASES = [
    {
        "id": "case_001",
        "level": "easy",
        "complaint": "User 'CryptoKing99' sent me a link that asked for my password.",
        "target": "CryptoKing99",
        "logs": {
            "query_message_logs": "[08:01] CryptoKing99: Hey! Claim your free Bitcoin here: http://fake-login-verify.com/stolen-creds",
            "query_login_history": "IP: 192.168.1.1 (Standard residential)",
            "query_linked_accounts": "No linked accounts found."
        },
        "correct_resolution": "ban_user" # Blatant phishing
    },
    {
        "id": "case_002",
        "level": "medium",
        "complaint": "User 'GamerGurl' called me a noob and told me I suck at the game.",
        "target": "GamerGurl",
        "logs": {
            "query_message_logs": "[14:22] GamerGurl: Wow you are literal trash at this game. Go back to the tutorial.",
            "query_login_history": "IP: 10.0.0.5 (Standard residential)",
            "query_linked_accounts": "Account linked to verified Twitch streamer."
        },
        "correct_resolution": "issue_warning" # Rude, but not a bannable offense on the first strike
    },
    {
        "id": "case_003",
        "level": "hard",
        "complaint": "Five different accounts bought my art but the credit cards all charged back.",
        "target": "ArtBuyer_Alpha",
        "logs": {
            "query_message_logs": "[09:00] ArtBuyer_Alpha: I would like to buy your most expensive piece.",
            "query_login_history": "IP: 45.33.22.11 (Known VPN/Proxy node used for fraud)",
            "query_linked_accounts": "Linked via device fingerprint to: ArtBuyer_Beta, ArtBuyer_Gamma, ArtBuyer_Delta."
        },
        "correct_resolution": "escalate_to_human" # Complex fraud ring requires human legal review
    }
]

class TrustSafetyEnv(Environment):
    def __init__(self):
        super().__init__()
        self.current_case_idx = 0
        self.last_query_result = "No queries made yet. Use 'query_type' to investigate the logs."
        self._state = TrustState(current_task_level=CASES[0]["level"])
        
    def reset(self) -> CaseObservation:
        self.current_case_idx = 0
        self.last_query_result = "No queries made yet. Use 'query_type' to investigate the logs."
        self._state = TrustState(
            current_task_level=CASES[self.current_case_idx]["level"], 
            cases_reviewed=0, 
            accumulated_reward=0.0, 
            is_done=False
        )
        return self._generate_observation()

    def step(self, action: AnalystAction) -> Tuple[CaseObservation, float, bool, dict]:
        if self._state.is_done:
            raise ValueError("Episode is already finished. Call reset().")
            
        current_case = CASES[self.current_case_idx]
        reward = 0.0
        
        # 1. Handle Active Investigation Queries (The AI is digging for clues)
        if action.query_type in ["query_message_logs", "query_login_history", "query_linked_accounts"]:
            self.last_query_result = current_case["logs"][action.query_type]
            
        # 2. Handle Case Resolution (The AI is making its final decision)
        elif action.query_type == "resolve_case":
            if action.resolution_decision == current_case["correct_resolution"]:
                reward = 1.0  # Perfect decision!
                self.last_query_result = f"Correct! Action '{action.resolution_decision}' was appropriate."
            else:
                reward = -1.0 # Wrong decision!
                self.last_query_result = f"Incorrect. '{action.resolution_decision}' was the wrong call for this scenario."
            
            # Update scores and move to the next case
            self._state.accumulated_reward += reward
            self._state.cases_reviewed += 1
            self.current_case_idx += 1
            
            # Check if the game is over
            if self.current_case_idx >= len(CASES):
                self._state.is_done = True
            else:
                self._state.current_task_level = CASES[self.current_case_idx]["level"]
                self.last_query_result += " Moving to the next case..."
                
        return self._generate_observation(), reward, self._state.is_done, {"total_score": self._state.accumulated_reward}

    def state(self) -> TrustState:
        return self._state

    def _generate_observation(self) -> CaseObservation:
        # If the game is done, return a final summary observation
        if self._state.is_done:
             return CaseObservation(
                case_id="DONE",
                task_level="none",
                initial_complaint="All cases reviewed.",
                query_results=f"Investigation Complete. Final Score: {self._state.accumulated_reward}"
            )
            
        # Otherwise, return the current case details
        current_case = CASES[self.current_case_idx]
        return CaseObservation(
            case_id=current_case["id"],
            task_level=current_case["level"],
            initial_complaint=current_case["complaint"],
            query_results=self.last_query_result
        )