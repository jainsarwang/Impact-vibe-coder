from datetime import datetime
import logging
import json
import os
import json_repair
import logging
from copy import deepcopy
from typing import Literal
from langchain_core.messages import HumanMessage, BaseMessage

import json_repair
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.types import Command

from src.agents import  (
    research_agent, 
    directory_generator_agent, 
    coder_master_agent, 
    model_coder_agent,
    controller_coder_agent,
    route_coder_agent,
    service_coder_agent,
    utility_coder_agent,
    config_coder_agent,
    test_coder_agent,
    frontend_coder_agent,db_coder_agent,
    browser_agent
)
from src.llms.llm import get_llm_by_type
from src.config import TEAM_MEMBERS
from src.config.agents import AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template, apply_prompt_template_planner, get_prompt_template
from src.tools.search import tavily_tool
from src.utils.json_utils import repair_json_output
from .types import State, Router
import re
import json

def extract_and_save_json(response_text: str, output_file: str = 'project_requirements.json') -> bool:
    """
    Extracts JSON from response text and saves to file.
    Uses a non-recursive approach to handle nested structures.
    """
    try:
        # First try parsing the entire response as JSON
        try:
            json_data = json.loads(response_text)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            return True
        except json.JSONDecodeError:
            pass  # Continue to try partial extraction

        # Improved pattern without recursive extension
        json_pattern = r'(?s)(?:```json\s*)?(\{(?:[^{}]|(?0))*\})(?:\s*```)?'
        
        # Alternative simpler pattern that works with standard re
        simple_pattern = r'(?s)(?:```json\s*)?(\{.*?\})(?:\s*```)?'
        
        for pattern in [simple_pattern, json_pattern]:
            try:
                match = re.search(pattern, response_text)
                if match:
                    json_str = match.group(1)
                    json_data = json.loads(json_str)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    return True
            except (re.error, json.JSONDecodeError):
                continue

        raise ValueError("No valid JSON found after multiple extraction attempts")
    
    except Exception as e:
        raise ValueError(f"Could not extract valid JSON: {str(e)}")

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

def directory_generator_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the directory generator agent that generator directory structure."""
    logger.info("Directory Generator agent starting task")
    result = directory_generator_agent.invoke(state)
    logger.info("Directory Generator agent completed task")
    response_content = result["messages"][-1].content
    response_content = repair_json_output(response_content)
    
    logger.debug(f"Directory Generator agent response: {response_content}")
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="directory_generator",
                )
            ],
            "directory_structure": response_content
        },
        goto="supervisor",
    )

"""

Directory  ->  Image Generation  -> Dependencies Graph  ->  Coder Master  -> (
    Coder  -> Analyse code and all fucntion corresponds to Graph
)  ->  Move to next File generation by Coder

"""

CODER_AGENTS = [
    "model_coder",
    "controller_coder",
    "route_coder",
    "service_coder",
    "utility_coder",
    "test_coder",
    "config_coder",
    "frontend_coder",
    "db_coder",
]
def coder_master_node(state: State) -> Command[Literal[*CODER_AGENTS, "supervisor", "__end__"]]:
    """Coder Master node that decides which agent should act next."""
    
    logger.info("Coder master evaluating next action")

    directory_structure = state.get('directory_structure')
    if not directory_structure:
        logging.warning("No Directory Object in State, Going back to supervisor")
        return Command(goto='supervisor')
    
    generated_files = state.get('generated_files')
    if not generated_files:
        generated_files = []

    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template('coder_master'),
    ).format(CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"), **state)

    message = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"Directory Struture: {directory_structure}\n\nGenerated Files: {str(generated_files)}"
        }
    ]

    response = (
        get_llm_by_type(AGENT_LLM_MAP["coder_master"])
        # Remove .with_structured_output for streaming compatibility
        .invoke(message)
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
            raise ValueError("Unexpected response format from Coder master LLM")
        goto = parsed_response.get("next")

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing Coder master response: {e}, raw response: {response}")
        goto = "__end__"  # Default to end if parsing fails

    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Coder master raw response: {response.content}")
    logger.debug(f"Coder master parsed response: {goto=}")

    if goto == "FINISH":
        goto = "__end__"
        logger.info("Coder Master workflow completed")
    elif goto == "INSTALLATION":
        goto = "__end__"
        # TODO: Module installtion handling left
        logger.info("Module Installtion required")
    elif goto in CODER_AGENTS:
        logger.info(f"Coder Master delegating to: {goto}")
    else:
        logger.warning(f"Coder master returned invalid next step: {goto}. Ending workflow.")
        goto = "__end__"

    return Command(
        goto=goto, 
        update={
            "messages": [
                HumanMessage(
                    content=response.content,
                    name="coder_master",
                )
            ],
            "generated_files": generated_files, 
            "coder_instruction": parsed_response
        }
    )








def model_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Model Coder agent that generator directory structure."""
    logger.info("Model Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = model_coder_agent.invoke(state)
    logger.info("Model Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Model Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="model_coder",
                )
            ],
        },
        goto="coder_master",
    )

def controller_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Controller Coder agent that generator directory structure."""
    logger.info("Controller Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = controller_coder_agent.invoke(state)
    logger.info("Controller Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Controller Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="controller_coder",
                )
            ],
        },
        goto="coder_master",
    )

def route_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Router Coder agent that generator directory structure."""
    logger.info("Router Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = route_coder_agent.invoke(state)
    logger.info("Router Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Router Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="route_coder",
                )
            ],
        },
        goto="coder_master",
    )

def service_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Service Coder agent that generator directory structure."""
    logger.info("Service Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = service_coder_agent.invoke(state)
    logger.info("Service Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Service Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="service_coder",
                )
            ],
        },
        goto="coder_master",
    )

def utility_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Utility Coder agent that generator directory structure."""
    logger.info("Utility Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = utility_coder_agent.invoke(state)
    logger.info("Utility Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Utility Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="utility_coder",
                )
            ],
        },
        goto="coder_master",
    )

def config_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Config Coder agent that generator directory structure."""
    logger.info("Config Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = config_coder_agent.invoke(state)
    logger.info("Config Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Config Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="config_coder",
                )
            ],
        },
        goto="coder_master",
    )

def test_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Test Coder agent that generator directory structure."""
    logger.info("Test Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = test_coder_agent.invoke(state)
    logger.info("Test Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Test Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="test_coder",
                )
            ],
        },
        goto="coder_master",
    )

def frontend_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Frontend Coder agent that generator directory structure."""
    logger.info("Frontend Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = frontend_coder_agent.invoke(state)
    logger.info("Frontend Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Frontend Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="frontend_coder",
                )
            ],
        },
        goto="coder_master",
    )

def db_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the DB Coder agent that generator directory structure."""
    logger.info("DB Coder agent starting task")
    logging.warning(state.get('coder_instruction'))

    result = db_coder_agent.invoke(state)
    logger.info("DB Coder agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"DB Coder agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="db_coder",
                )
            ],
        },
        goto="coder_master",
    )


# def code_node(state: State) -> Command[Literal["supervisor"]]:
#     """Node for the coder agent that executes Python code."""
#     logger.info("Code agent starting task")
#     result = coder_agent.invoke(state)
#     logger.info("Code agent completed task")
#     response_content = result["messages"][-1].content
#     # 尝试修复可能的JSON输出
#     response_content = repair_json_output(response_content)
#     logger.debug(f"Code agent response: {response_content}")
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response_content,
#                     name="coder",
#                 )
#             ]
#         },
#         goto="supervisor",
#     )

# def frontend_code_node(state: State) -> Command[Literal["supervisor"]]:
#     """Node for the frontend coder agent that executes Python code."""
#     logger.info("Frontend Code agent starting task")
#     result = frontend_coder_agent.invoke(state)
#     logger.info("Frontend Code agent completed task")
#     response_content = result["messages"][-1].content
#     response_content = repair_json_output(response_content)
#     logger.debug(f"Frontend Code agent response: {response_content}")
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response_content,
#                     name="frontend_coder",
#                 )
#             ]
#         },
#         goto="supervisor",
#     )

# def backend_code_node(state: State) -> Command[Literal["supervisor"]]:
#     """Node for the frontend coder agent that executes Python code."""
#     logger.info("Backend Code agent starting task")
#     result = backend_coder_agent.invoke(state)
#     logger.info("Backend Code agent completed task")
#     response_content = result["messages"][-1].content
#     response_content = repair_json_output(response_content)
#     logger.debug(f"Backend Code agent response: {response_content}")
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response_content,
#                     name="backend_coder",
#                 )
#             ]
#         },
#         goto="supervisor",
#     )

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
    messages = apply_prompt_template_planner("planner", state)
    # whether to enable deep thinking mode
    llm = get_llm_by_type("basic")
    if state.get("deep_thinking_mode"):
        llm = get_llm_by_type("reasoning")
    if state.get("search_before_planning"):
        searched_content = tavily_tool.invoke({"query": state["messages"][-1].content})
        messages = deepcopy(messages)
        messages[-1].content += f"\n\n# Relative Search Results\n\n{json.dumps([{'title': elem['title'], 'content': elem['content']} for elem in searched_content], ensure_ascii=False)}"
    response = llm.invoke(messages)
    full_response = response.content
    # extract_and_save_json(full_response)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")

    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    goto = "supervisor"
    try:
        repaired_response = json_repair.loads(full_response)
        full_response = json.dumps(repaired_response)
        with open("project_requirements.json", "w", encoding="utf-8") as f:
            json.dump(repaired_response, f, indent=2, ensure_ascii=False)
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
    """Coordinator node that communicates with customers, showing only non-JSON context."""
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    
    # Keep original response
    response_content_raw = response.content
    
    # Process JSON for internal use
    response_content = repair_json_output(response_content_raw)
    logger.debug(f"Coordinator full response: {response_content}")
    
    # Extract non-JSON context to show user
    user_display_content = extract_user_content(response_content_raw)
    
    # Set the user-visible content
    response.content = user_display_content
    
    # Handle planner handoff
    goto = "__end__"
    if "handoff_to_planner()" in response_content_raw:
        extract_and_save_json(response_content)
        goto = "planner"
    
    return Command(goto=goto)

def extract_user_content(full_content: str) -> str:
    """Extracts non-JSON parts of the response for user display."""
    # Remove JSON blocks (both ```json``` and raw {})
    no_json = re.sub(r'```json.*?```', '', full_content, flags=re.DOTALL)
    no_json = re.sub(r'\{.*?\}', '', no_json, flags=re.DOTALL)
    
    # Remove technical markers like handoff_to_planner()
    no_json = no_json.replace("handoff_to_planner()", "")
    
    # Clean up resulting whitespace
    return "\n".join(line.strip() for line in no_json.splitlines() if line.strip())

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