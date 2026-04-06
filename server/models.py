from pydantic import Field
from typing import Literal, Optional
from openenv.core.env_server import Action, Observation, State

# 1. WHAT THE AGENT CAN DO
class AnalystAction(Action):
    query_type: Literal[
        "query_login_history", 
        "query_message_logs", 
        "query_linked_accounts", 
        "resolve_case"
    ] = Field(
        ..., 
        description="Active investigation choice. Query the database to gather info, or select resolve_case to make a final decision."
    )
    
    resolution_decision: Optional[Literal[
        "ban_user", 
        "issue_warning", 
        "escalate_to_human", 
        "dismiss"
    ]] = Field(
        None, 
        description="ONLY required if query_type is 'resolve_case'. The final moderation action."
    )
    
    target_account: Optional[str] = Field(
        None, 
        description="The specific account ID you are querying or taking action against."
    )

# 2. WHAT THE AGENT SEES
class CaseObservation(Observation):
    case_id: str = Field(..., description="The ID of the current case being investigated.")
    task_level: str = Field(..., description="Difficulty level: easy, medium, or hard.")
    initial_complaint: str = Field(..., description="The user report that initiated the investigation.")
    query_results: str = Field(
        default="No queries made yet.", 
        description="The output from your last database query. Use this to inform your next action."
    )

# 3. THE INTERNAL STATE (Required by framework)
class TrustState(State):
    current_task_level: Literal["easy", "medium", "hard"]
    cases_reviewed: int = 0
    accumulated_reward: float = 0.0
    is_done: bool = False