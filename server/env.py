import uuid
from typing import Tuple
from openenv.core.env_server import Environment
from .models import AnalystAction, CaseObservation, TrustState

class TrustSafetyEnv(Environment):
    def __init__(self):
        super().__init__()
        self._state = TrustState(current_task_level="easy")
        
    def reset(self) -> CaseObservation:
        """Called at the start of a new episode or when the HF ping tests it."""
        self._state = TrustState(current_task_level="easy")
        return self._generate_observation()

    def step(self, action: AnalystAction) -> Tuple[CaseObservation, float, bool, dict]:
        """Processes the agent's action. (Dummy logic for validation)"""
        if self._state.is_done:
            raise ValueError("Episode is already finished. Call reset().")
            
        # Dummy progression so the bot sees the environment moving
        self._state.cases_reviewed += 1
        reward = 0.5 # Dummy reward
        
        if self._state.cases_reviewed >= 3:
            self._state.is_done = True
            
        return self._generate_observation(), reward, self._state.is_done, {}

    def state(self) -> TrustState:
        return self._state

    def _generate_observation(self) -> CaseObservation:
        return CaseObservation(
            case_id=str(uuid.uuid4())[:8],
            task_level=self._state.current_task_level,
            initial_complaint="User reported for suspicious activity.",
            query_results="No queries made yet. Use query_type to investigate."
        )