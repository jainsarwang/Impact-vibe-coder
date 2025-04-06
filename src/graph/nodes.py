import logging
import json
import json_repair
import logging
from copy import deepcopy
from typing import Literal
from langchain_core.messages import HumanMessage, BaseMessage

import json_repair
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.agents import research_agent, coder_agent, browser_agent
from src.llms.llm import get_llm_by_type
from src.config import TEAM_MEMBERS
from src.config.agents import AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template
from src.tools.search import tavily_tool
from src.utils.json_utils import repair_json_output
from .types import State, Router

logger = logging.getLogger(__name__)

RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"


def research_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the researcher agent that performs research tasks."""
    logger.info("Research agent starting task")
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    response_content = result["messages"][-1].content

    response_content = repair_json_output(response_content)
    logger.debug(f"Research agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="researcher",
                )
            ]
        },
        goto="supervisor",
    )


def code_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the coder agent that executes Python code."""
    logger.info("Code agent starting task")
    result = coder_agent.invoke(state)
    logger.info("Code agent completed task")
    response_content = result["messages"][-1].content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"Code agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="coder",
                )
            ]
        },
        goto="supervisor",
    )


def browser_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the browser agent that performs web browsing tasks."""
    logger.info("Browser agent starting task")
    result = browser_agent.invoke(state)
    logger.info("Browser agent completed task")
    response_content = result["messages"][-1].content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"Browser agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="browser",
                )
            ]
        },
        goto="supervisor",
    )


def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """Supervisor node that decides which agent should act next."""
    logger.info("Supervisor evaluating next action")
    messages = apply_prompt_template("supervisor", state)
    # preprocess messages to make supervisor execute better.
    messages = deepcopy(messages)
    for message in messages:
        if isinstance(message, BaseMessage) and message.name in TEAM_MEMBERS:
            message.content = RESPONSE_FORMAT.format(message.name, message.content)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["supervisor"])
        # Remove .with_structured_output for streaming compatibility
        .invoke(messages)
    )
    # Parse the JSON manually if the LLM doesn't directly output structured data
    try:
        if isinstance(response, str):
            # Handle Markdown JSON formatting if present
            if response.startswith('```json') and response.endswith('```'):
                response = response[7:-3].strip()  # Remove ```json and ```
            parsed_response = json.loads(response)
        elif hasattr(response, 'content'):
            content = response.content
            # Handle Markdown JSON formatting if present
            if content.startswith('```json') and content.endswith('```'):
                content = content[7:-3].strip()  # Remove ```json and ```
            parsed_response = json.loads(content)
        else:
            raise ValueError("Unexpected response format from supervisor LLM")
        goto = parsed_response.get("next")
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing supervisor response: {e}, raw response: {response}")
        goto = "__end__"  # Default to end if parsing fails

    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Supervisor raw response: {response.content}")
    logger.debug(f"Supervisor parsed response: {goto=}")

    if goto == "FINISH":
        goto = "__end__"
        logger.info("Workflow completed")
    elif goto in TEAM_MEMBERS:
        logger.info(f"Supervisor delegating to: {goto}")
    else:
        logger.warning(f"Supervisor returned invalid next step: {goto}. Ending workflow.")
        goto = "__end__"

    return Command(goto=goto, update={"next": goto})


def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan")
    messages = apply_prompt_template("planner", state)
    # whether to enable deep thinking mode
    llm = get_llm_by_type("basic")
    if state.get("deep_thinking_mode"):
        llm = get_llm_by_type("reasoning")
    if state.get("search_before_planning"):
        searched_content = tavily_tool.invoke({"query": state["messages"][-1].content})
        messages = deepcopy(messages)
        messages[
            -1
        ].content += f"\n\n# Relative Search Results\n\n{json.dumps([{'title': elem['title'], 'content': elem['content']} for elem in searched_content], ensure_ascii=False)}"
    response = llm.invoke(messages)
    full_response = response.content
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Planner response: {full_response}")

    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    goto = "supervisor"
    try:
        repaired_response = json_repair.loads(full_response)
        full_response = json.dumps(repaired_response)
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        goto = "__end__"

    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="planner")],
            "full_plan": full_response,
        },
        goto=goto,
    )


def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    response_content = response.content
    response_content = repair_json_output(response_content)
    logger.debug(f"Coordinator response: {response_content}")

    goto = "__end__"
    if "handoff_to_planner" in response_content.lower():
        goto = "planner"

    response.content = response_content

    return Command(
        goto=goto,
    )



def reporter_node(state: State) -> Command[Literal["supervisor"]]:
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    messages = apply_prompt_template("reporter", state)
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    response_content = response.content
    # 尝试修复可能的JSON输出
    response_content = repair_json_output(response_content)
    logger.debug(f"reporter response: {response_content}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="reporter",
                )
            ]
        },
        goto="supervisor",
    )