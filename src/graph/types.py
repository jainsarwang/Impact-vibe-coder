from typing import Any, Literal
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage

from src.config import TEAM_MEMBERS
from src.utils.ChecklistManager import ChecklistManager

# Define routing options
OPTIONS = TEAM_MEMBERS + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*OPTIONS]


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""

    # Constants
    TEAM_MEMBERS: list[str]
    checklist_manager: ChecklistManager

    # Runtime Variables
    requirements: dict # requirements of the application
    next: str # Information about the next agent
    full_plan: str # Full plan of the current application
    deep_thinking_mode: bool #Deep thinking mode enabled
    search_before_planning: bool #searching mode enabled
    researched_content: str # full research content from all researchers
    directory_structure: str # full directory structure of the application
    generated_files: list[str] # Files that are already generated
    coder_instruction: Any # next coder instruction from the coder master
    component_diagram: str # component diagram of the application
    code_plan: str # code generation plan of the application
    previous_file_path: str # previously generated file path
    previous_file_content: str # previously generated file content
    session_id: str # session id of the current session
    tokens: int # tokens used in a session

    report: str # report of the current application
    is_terraform_generated: bool # if terraform is generated or not