from typing import Any, Literal
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage

from src.config import TEAM_MEMBERS

# Define routing options
OPTIONS = TEAM_MEMBERS + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*OPTIONS]


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""

    # Constants
    TEAM_MEMBERS: list[str]

    # Runtime Variables
    next: str
    full_plan: str
    deep_thinking_mode: bool
    search_before_planning: bool
    researched_content: str
    directory_structure: str
    generated_files: list[str]
    coder_instruction: Any
    code_plan: str