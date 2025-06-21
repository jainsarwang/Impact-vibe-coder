from datetime import datetime
import logging
import json
import os
import json_repair
import logging
from copy import deepcopy
from io import BytesIO
from PIL import Image
from typing import Dict, List, Literal
from pymongo import MongoClient
from bson import SON


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
    browser_agent,
    import_export_agent,
    version_agent,
    figma_coder_agent
)
from src.llms.llm import get_llm_by_type
from src.config import TEAM_MEMBERS, CODER_AGENTS, AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template, apply_prompt_template_for_coder, apply_prompt_template_planner, get_prompt_template
from src.tools import tavily_tool, bash_tool
from src.utils import ReadmeExecutor, repair_json_output, ensure_directory_exists, ChecklistManager, token_count, get_response_schema
from src.utils.save_chat_history import save_chat_history
from .types import State
from ..terraform_generator.src import terraform_generator_main
import re
import json


logger = logging.getLogger(__name__)

report = {
    "project_name": "VibeCoder",
    "instances": [
        {
            "ami_id": "ami-0af9569868786b23a",  # Default Amazon Linux 2 AMI
            "instance_type": "t2.micro",
            "tags": {"Name": "VibeCoder-Instance"},
            "security_groups": []
        }
    ]
}

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

RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"

def research_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the researcher agent that performs research tasks."""
    logger.info("Research agent starting task")
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    token_count.set_token_count(token_count.token_count(result["messages"][-1].content))
    logger.info("Token count after research agent: %s", token_count.get_token_count())
    response_content = result["messages"][-1].content

    logger.debug(f"Research agent response: {response_content}")
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="researcher",
                )
            ],
            "researched_content" : response_content,
            "tokens": token_count.get_token_count()
        },
        goto="supervisor",
    )


def directory_generator_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the directory generator agent that generator directory structure."""
    logger.info("Directory Generator agent starting task")
    logger.debug(f"Request sent to directory generator: {state}")
    result = directory_generator_agent.invoke(state)
    logger.debug(f"Result response from directory generator: {result}")
    checklist_manager = ChecklistManager(state)  # Reset checklist manager for new task
    
    logger.info("Directory Generator agent completed task")
    token_count.set_token_count(token_count.token_count(result["messages"][-1].content))

    checklist_manager.update_tokens(token_count.get_token_count())
    logger.info("Token count after directory generator: %s", token_count.get_token_count())
    response_content = result["messages"][-1].content
    response_content = repair_json_output(response_content)
    # extract_and_save_json(response_content, "directory_structure.json")

    # Initialize checklist from directory structure
    checklist_manager.initialize_from_directory(response_content)
    
    
    # checklist_manager.save_chat_history(state, "directory_generator")
    
    
    logger.debug(f"Directory Generator agent response: {response_content}")
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="directory_generator",
                )
            ],
            "directory_structure": response_content,
            "checklist_manager": checklist_manager,
            "tokens": token_count.get_token_count()
        },
        goto="supervisor",
    )

"""
Directory  ->  Image Generation  -> Dependencies Graph  ->  Coder Master  -> (
    Coder  -> Analyse code and all fucntion corresponds to Graph
)  ->  Move to next File generation by Coder
"""
    
def code_planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Code Planner node that generate the full plan for coder master."""
    logger.info("Code Planner generating full plan")

    directory_structure = state.get('directory_structure')
    if not directory_structure:
        logging.warning("No Directory Object in State, Going back to supervisor")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update={"tokens": token_count.get_token_count()})

    # Prepare all variables for the prompt
    prompt_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        "CODER_AGENTS": ", ".join(CODER_AGENTS),  # Convert list to string
        "directory_structure": directory_structure,
        **state  # Include other state variables
    }

    template = get_prompt_template('code_planner')
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME", "CODER_AGENTS","directory_structure"],
        template=template,
    ).format(**prompt_vars)

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": "Create a Code plan"
        }
    ]
    messages = apply_prompt_template_planner("code_planner", state)
    # whether to enable deep thinking mode
    llm = get_llm_by_type("basic", schema=get_response_schema("code_planner"))
    response = llm.invoke(messages)
    token_count.set_token_count(token_count.token_count(response.content))
    state.get("checklist_manager").update_tokens(token_count.get_token_count())
    logger.info("Token count after code planner: %s", token_count.get_token_count())
    full_response = response.content
    # extract_and_save_json(full_response)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Code Planner response: {full_response}")

    # extract_and_save_json(full_response, "code_planner.json")

    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    goto = "supervisor"

    try:
        repaired_response = json_repair.loads(full_response)
        full_response = json.dumps(repaired_response)

        # Update checklist from the plan
        state.get("checklist_manager").update_from_plan(repaired_response)
    except json.JSONDecodeError:
        logger.warning("Code Planner response is not a valid JSON")
        goto = "__end__"
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="code_planner")],
            "code_plan": full_response,
            "tokens": token_count.get_token_count()
        },
        goto=goto,
    )


def version_resolver_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Node for version resolver agent that verifies versions and corrects them to latest stable versions."""
    logger.info("Version Resolver Agent starting task")

    # Safely get directory_structure from state
    directory_structure = state.get('directory_structure')
    if not directory_structure:
        logger.warning("No Directory Object in State, Going back to supervisor")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update={"tokens": token_count.get_token_count()})

    # Parse directory_structure if it's a string
    if isinstance(directory_structure, str):
        try:
            directory_structure = json.loads(directory_structure)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse directory_structure: {e}")
            logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
            return Command(goto='supervisor', update={"tokens": token_count.get_token_count()})

    # Initialize dependencies_values safely
    dependencies_values = {}
    try:
        dependencies_values = directory_structure.get("dependencies", {})
        if isinstance(dependencies_values, str):
            dependencies_values = json.loads(dependencies_values)
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Failed to parse dependencies: {e}")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update={"token": token_count.get_token_count()})

    # Prepare prompt variables
    prompt_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state
    }

    # Get and format the prompt template
    template = get_prompt_template('version_resolver')
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=template,
    ).format(**prompt_vars)

    # Prepare messages for LLM
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": json.dumps(dependencies_values)  # Better than List() for JSON data
        }
    ]

    # Get LLM response
    llm = get_llm_by_type("basic", schema=get_response_schema("version_resolver"))
    try:
        response = llm.invoke(messages)
        full_response = response.content
        token_count.set_token_count(token_count.token_count(response.content))      
        state.get("checklist_manager").update_tokens(token_count.get_token_count())
        logger.info("Token count after version resolver: %s", token_count.get_token_count())    
        json_response = repair_json_output(full_response)
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update = {"token": token_count.get_token_count()})

    logger.debug(f"Current state messages: {state.get('messages', [])}")
    logger.info(f"Version Resolver response: {json_response}")

    # Process the response
    try:
        if isinstance(json_response, str):
            parsed_response = json.loads(json_response)
        else:
            parsed_response = json_response  # Assuming it's already a dict/list

        # Validate the response structure
        if not isinstance(parsed_response, (dict, list)):
            raise ValueError("Response must be a dictionary or list")

        directory_structure['dependencies'] = parsed_response
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.error(f"Failed to process LLM response: {e}")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update = {"tokens": token_count.get_token_count()})

    logger.info("Version Resolver work done")
    logger.debug(f"Updated dependencies: {directory_structure['dependencies']}")
    logger.info(directory_structure)
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=str(parsed_response),
                    name="version_resolver",
                )
            ],
            "directory_structure": str(directory_structure),
            "tokens": token_count.get_token_count()
        },
        
        goto="supervisor",
    )
    
def coder_master_node(state: State) -> Command[Literal[*CODER_AGENTS, "supervisor", "__end__"]]:
    """
    Coder Master node that decides which agent should act next based on the checklist.
    It reads the checklist, finds the next pending file, delegates to the assigned
    coder agent statically, and transitions back to supervisor when all planned
    files are marked as created.
    """
    logger.info("Coder master evaluating next action based on checklist")

    directory_structure = state.get('directory_structure')
    code_plan_str = state.get('code_plan')
    generated_files = state.get('generated_files', [])

    if not directory_structure or not code_plan_str:
        logging.warning("No Directory Structure or code plan in State. Going back to supervisor.")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update={
            "messages": state["messages"] + [
                HumanMessage(
                    content="Coder master cannot proceed: Missing directory structure or code plan.",
                    name="coder_master",
                ),
            ],
            "tokens": token_count.get_token_count()
        })

    # Load the code plan from the JSON string
    try:
        code_plan = json.loads(code_plan_str)
        if not isinstance(code_plan, list):
            code_plan = code_plan.get("plan", [])
            if not isinstance(code_plan, list):
                logger.error("Code plan loaded but is not a list and has no 'plan' key list.")
                raise ValueError("Invalid code plan format")

        # Update checklist with the plan
        state.get("checklist_manager").update_from_plan(code_plan)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse or process code_plan JSON string: {e}")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='__end__', update={
            "messages": state["messages"] + [
                HumanMessage(content=f"Error parsing code plan: {e}", name="coder_master")
            ],
            "tokens": token_count.get_token_count()
        })

    # Get the next file to process from the checklist
    next_file_info = state.get("checklist_manager").get_next_file_to_process()

    if next_file_info:
        file_path_to_process = next_file_info['file_path']
        assigned_coder_name = next_file_info.get('coder')

        logger.info(f"Next file from checklist: {file_path_to_process}")
        logger.debug(f"Assigned coder: {assigned_coder_name}")

        if assigned_coder_name not in CODER_AGENTS:
            logger.error(f"Checklist assigned an invalid coder '{assigned_coder_name}' for file '{file_path_to_process}'.")
            logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
            return Command(goto='supervisor', update={
                "messages": state["messages"] + [
                    HumanMessage(
                        content=f"Checklist error: Invalid coder '{assigned_coder_name}' for file '{file_path_to_process}'.",
                        name="coder_master",
                    )
                ],
                "tokens": token_count.get_token_count()
            })

        # Find the specific instruction for this file in the code plan
        instruction_content = ""
        found_plan_item = None
        
        for item in code_plan:
            if "file" in item and state.get("checklist_manager")._normalize_path(item["file"]) == state.get("checklist_manager")._normalize_path(file_path_to_process):
                instruction_content = json.dumps(item, indent=2)
                found_plan_item = item
                break

        if not found_plan_item:
            logger.warning(f"Could not find specific plan item for file '{file_path_to_process}' in the code_plan.")
            instruction_content = json.dumps({
                "file": file_path_to_process,
                "coder": assigned_coder_name,
                "description": f"Generate the content for the file '{file_path_to_process}'."
            }, indent=2)

        logger.info(f"Delegating to agent: {assigned_coder_name} for file: {file_path_to_process}")

        coder_master_message = f"Delegating file `{file_path_to_process}` to `{assigned_coder_name}` agent."
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(
            goto=assigned_coder_name,
            update={
                "messages": state["messages"] + [HumanMessage(content=coder_master_message, name="coder_master")],
                "coder_instruction": instruction_content,
                "current_file_processing": file_path_to_process,
                "generated_files": generated_files,
                "tokens": token_count.get_token_count()
            }
        )

    else:
        logger.info("Checklist indicates no more planned files need processing.")

        unplanned_created = state.get("checklist_manager").get_unplanned_files()
        completion_message = "Coding phase completed. All planned files have been processed."
        if unplanned_created:
            completion_message += f"\nNote: {len(unplanned_created)} files were created but were not in the original plan."

        updated_state = deepcopy(state)
        updated_state["coder_instruction"] = None
        updated_state["current_file_processing"] = None
        updated_state["messages"].append(HumanMessage(content=completion_message, name="coder_master"))
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(
            goto='supervisor',            
        )

def coder(state: State, prompt_name: str, agent) -> Command[Literal["coder_master"]]:
    """
    Generic coder node that invokes a specified agent, parses its JSON response
    to extract file paths and content, and writes those files to disk.
    """
    logger.info(f"Coder node '{prompt_name}' starting task.")
    logger.debug(f"Instruction for {prompt_name} from coder_master: {state.get('coder_instruction')}")

    try:
        result = agent(state)
    except Exception as e:
        logger.error(f"Error invoking agent '{prompt_name}': {str(e)}", exc_info=True)
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error during agent '{prompt_name}' execution: {str(e)}",
                        name=prompt_name,
                    )
                ],
                "tokens": token_count.get_token_count()
            },
            goto="coder_master",
        )

    logger.info(f"Coder agent '{prompt_name}' completed invocation.")

    response_content_raw = result["messages"][-1].content
    token_count.set_token_count(token_count.token_count(response_content_raw))
    state.get("checklist_manager").update_tokens(token_count.get_token_count())
    logger.info("Token count after coder agent '%s': %s", prompt_name, token_count.get_token_count())
    response_content_repaired = repair_json_output(response_content_raw)

    try:
        parsed_response = json.loads(response_content_repaired)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from '{prompt_name}': {e}")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error parsing JSON response from '{prompt_name}': {str(e)}",
                        name=prompt_name,
                    )
                ],
                "tokens": token_count.get_token_count()
            },
            goto="coder_master",
        )

    current_generated_files = state.get('generated_files', [])
    newly_generated_this_run: List[str] = []
    processed_file_specs: List[Dict[str, str]] = []
    if isinstance(parsed_response, list):
        parsed_response = dict(parsed_response[0])
    elif isinstance(parsed_response, str):
        parsed_response = dict(parsed_response)
    else:
        if not isinstance(parsed_response, dict):
            parsed_response = dict(parsed_response)
    logger.info(f"Parsed response from '{prompt_name}': {parsed_response}")
    files_spec_from_llm = parsed_response.get("FILE")
    if isinstance(files_spec_from_llm, str):
        path = files_spec_from_llm
        content = parsed_response.get("code", "")
        description = parsed_response.get("description", "")
        processed_file_specs.append({"path": path, "content": content})
    elif isinstance(files_spec_from_llm, list):
        for item in files_spec_from_llm:
            if isinstance(item, str):
                processed_file_specs.append({"path": item, "content": parsed_response.get("code", "")})
            elif isinstance(item, dict):
                path = item.get("path")
                content = item.get("content", parsed_response.get("code", ""))
                logger.info(f"Content : {content}")
                if path:
                    processed_file_specs.append({"path": path, "content": content if content is not None else ""})
    elif files_spec_from_llm is None:
        top_level_path = parsed_response.get("path")
        if top_level_path:
            processed_file_specs.append({"path": top_level_path, "content": parsed_response.get("code", "")})

    for file_spec in processed_file_specs:
        file_path = file_spec.get("path")
        file_content = file_spec.get("content", "")
        description = parsed_response.get("description", "")

        if not file_path:
            continue

        try:
            file_path = os.path.normpath(file_path)
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            newly_generated_this_run.append(file_path)
            
            # Update checklist
            state.get("checklist_manager").mark_file_created(file_path)
            if description:
                state.get("checklist_manager").update_file_description(file_path, description)
                logger.info(f"Updated description for file '{file_path}': {description}")

        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}", exc_info=True)

    updated_generated_files = list(set(current_generated_files + newly_generated_this_run))
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content_repaired,
                    name=prompt_name,
                )
            ],
            "generated_files": updated_generated_files,
            "tokens": token_count.get_token_count()
        },
        goto="coder_master",
    )


def import_export_node(state: State) -> Command[Literal["supervisor"]]:
    """
    Node for the import-export agent that verifies import and export statements of directory structure 
    and verifies the path of import and export statements. 
    Rewrite it in Directory if issues found
    """
    logger.info("import-export agent starting task")

    # if directory not foun in state, return to supervisor
    directory_structure = state.get('directory_structure')
    if not directory_structure:
        logging.warning("No Directory Object in State, Going back to supervisor")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(goto='supervisor', update={"tokens": token_count.get_token_count()})

    prompt_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        "directory_structure": directory_structure,
        **state  # Include other state variables
    }

    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template('import-export'),
    ).format(**prompt_vars)

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": directory_structure
        }
    ]

    goto= 'supervisor'

    try:
        llm = get_llm_by_type("basic", schema=get_response_schema("import_export"))
        response = llm.invoke(messages)
        full_response = response.content
        token_count.set_token_count(token_count.token_count(response.content))
        state.get("checklist_manager").update_tokens(token_count.get_token_count())
        logger.info("token count after import-export agent: %s", token_count.get_token_count())
        logger.debug(f"Current state messages: {state['messages']}")
        logger.info(f"Import Export Response: {full_response}")
        if full_response.startswith("```json"):
            full_response = full_response.removeprefix("```json")

        if full_response.endswith("```"):
            full_response = full_response.removesuffix("```")

    #     with open("directory_structure.json", "w", encoding="utf-8") as f:
    #         json.dump(repaired_response, f, indent=2, ensure_ascii=False)

    except json.JSONDecodeError:
        logger.warning("Import Export response is not a valid JSON")
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=(full_response),
                    name="import-export",
                )
            ],
            "directory_structure": (full_response),
            "tokens": token_count.get_token_count()
        },
        goto=goto,
    )   

# def import_export_node(state: State) -> Command[Literal["supervisor"]]:
#     """
#     Node for the import-export agent that verifies import and export statements of directory structure 
#     and verifies the path of import and export statements. 
#     Rewrite it in Directory if issues found
#     """
#     logger.info("import-export agent starting task")
#     result = import_export_agent.invoke(state)
#     logger.info("import-export agent completed task")
#     response_content = result["messages"][-1].content
#     response_content = repair_json_output(response_content)
#     extract_and_save_json(response_content, "import-export.json")

#     # Initialize checklist from directory structure
#     checklist_manager.initialize_from_directory(response_content)

#     logger.debug(f"Import-Export agent response: {response_content}")
    
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=response_content,
#                     name="import-export",
#                 )
#             ],
#             "directory_structure": response_content
#         },
#         goto="supervisor",
#     )

# """

# Directory  ->  Image Generation  -> Dependencies Graph  ->  Coder Master  -> (
#     Coder  -> Analyse code and all fucntion corresponds to Graph
# )  ->  Move to next File generation by Coder

# """


def model_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Model Coder agent that generator directory structure."""
    return coder(state, 'model_coder', model_coder_agent)

def controller_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Controller Coder agent that generator directory structure."""
    return coder(state, 'controller_coder', controller_coder_agent)

def route_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Router Coder agent that generator directory structure."""
    return coder(state, 'route_coder', route_coder_agent)

def service_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Service Coder agent that generator directory structure."""
    return coder(state, 'service_coder', service_coder_agent)

def utility_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Utility Coder agent that generator directory structure."""
    return coder(state, 'utility_coder', utility_coder_agent)

def config_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Config Coder agent that generator directory structure."""
    return coder(state, 'config_coder', config_coder_agent)

def test_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Test Coder agent that generator directory structure."""
    return coder(state, 'test_coder', test_coder_agent)

def frontend_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Frontend Coder agent that generator directory structure."""
    return coder(state, 'frontend_coder', frontend_coder_agent)

def db_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the DB Coder agent that generator directory structure."""
    return coder(state, 'db_coder', db_coder_agent)

def figma_coder_node(state: State) -> Command[Literal["coder_master"]]:
    """Node for the Figma Coder agent that generator directory structure."""

    logger.info(f"Coder node figma_coder starting task.")
    logger.debug(f"Instruction for 'figma_coder' from coder_master: {state.get('coder_instruction')}")

    try:
        parsed_instruction = json.loads(state.get('coder_instruction', '{}'))
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing 'coder_instruction' for 'figma_coder': {str(e)}", exc_info=True)
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error parsing 'coder_instruction' for 'figma_coder': {str(e)}",
                        name='figma_coder',
                    )
                ],
                "tokens": token_count.get_token_count()
            },
            goto="coder_master",
        )

    try:
        response_parts = figma_coder_agent(state)
    except Exception as e:
        logger.error(f"Error invoking agent 'figma_coder': {str(e)}", exc_info=True)
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error during agent 'figma_coder' execution: {str(e)}",
                        name='figma_coder',
                    )
                ],
                "tokens": token_count.get_token_count()
            },
            goto="coder_master",
        )

    logger.info(f"Coder agent 'figma_coder' completed invocation.")

    for part in response_parts:
        if part.inline_data is not None:
            file_name = parsed_instruction.get("file")
            if(not file_name):
                logger.warning("No file name provided in instruction for 'figma_coder'. Skipping image save.")
                continue

            image = Image.open(BytesIO(part.inline_data.data))
            ensure_directory_exists(file_name)
            image.save(file_name)
            logger.info(f"Image saved successfully as {file_name}")
        
    current_generated_files = state.get('generated_files', [])
    state['generated_files'] = current_generated_files + [parsed_instruction.get("file", "")]
    state.get('checklist_manager').mark_file_created(parsed_instruction.get("file", ""))
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="Image generated Successfully",
                    name='figma_coder',
                )
            ],
            "tokens": token_count.get_token_count()
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
    token_count.set_token_count(token_count.token_count(response_content))
    state.get("checklist_manager").update_tokens(token_count.get_token_count())
    logger.info("Token count after browser agent: %d", token_count.get_token_count())
    logger.debug(f"Browser agent response: {response_content}")
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="browser",
                )
            ],
            "tokens": token_count.get_token_count()
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
        get_llm_by_type(AGENT_LLM_MAP["supervisor"], get_response_schema("supervisor"))
        # Remove .with_structured_output for streaming compatibility
        .invoke(messages)
    )
    # Parse the JSON manually if the LLM doesn't directly output structured data
    save_chat_history(state)
    try:
        if isinstance(response, str):
            # Handle Markdown JSON formatting if present
            parsed_response = repair_json_output(response)
        elif hasattr(response, 'content'):
            content = response.content
            # Handle Markdown JSON formatting if present
            parsed_response = repair_json_output(content)
        else:
            raise ValueError("Unexpected response format from supervisor LLM")

        parsed_response = json.loads(parsed_response)
        goto = parsed_response.get("next")
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing supervisor response: {e}, raw response: {response}")
        goto = "__end__"  # Default to end if parsing fails

    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Supervisor raw response: {response.content}")
    logger.debug(f"Supervisor parsed response: {goto=}")

    if goto == "FINISH":
        save_chat_history(state)
        logger.info(f"Save chat history executed")
        state.get("checklist_manager").update_tokens(token_count.get_token_count())
        print(token_count.get_token_count())
        token_count.set_token_count(0)
        print(f"After making tokens to '0', count is: {token_count.get_token_count()}")
        
        project_requirement = state.get("full_plan")
        project_requirement = json.loads(project_requirement) if isinstance(project_requirement, str) else project_requirement
        goto = "__end__"
        if project_requirement:
            project_name = project_requirement.get('project_name', f"ivc-project-{state.get('session_id')}")
            # check if `projects/{project_name} exits`
            if not os.path.exists(f"projects/{project_name}"):
                logger.error(f"Project directory not found: projects/{project_name}")
            elif state.get('report') and not state.get("is_terraform_generated"):
                # if report is generated and terraform is not generated, then execute the executor
                logging.debug("**Executor Started")
                executor = ReadmeExecutor(project_path=f"projects/{project_name}")
                executor.extract_commands_with_gemini()
                executor.execute_commands()
                logging.debug("**Executor Ended")

                # then go to terraform generator
                goto = 'terraform_generator'
            else:
                logger.info("Workflow completed")
    elif goto in TEAM_MEMBERS:
        save_chat_history(state)
        logger.info(f"Save chat history executed")
        logger.info(f"Supervisor delegating to: {goto}")
    else:
        save_chat_history(state)
        logger.info(f"Save chat history executed")
        logger.warning(f"Supervisor returned invalid next step: {goto}. Ending workflow.")
        goto = "__end__"
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(goto=goto, update={"next": goto, "tokens": token_count.get_token_count()})

def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan")
    messages = apply_prompt_template_planner("planner", state)
    # whether to enable deep thinking mode
    logger.info(f"Current state messages at planner starting: {state['messages']}")
    llm = get_llm_by_type("basic", schema=get_response_schema("planner"))
    if state.get("deep_thinking_mode"):
        llm = get_llm_by_type("reasoning", schema=get_response_schema("planner"))
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
        token_count.set_token_count(token_count.token_count(full_response))
        # state.get("checklist_manager").update_tokens(token_count.get_token_count())
        logger.info("Token count after planner: %d", token_count.get_token_count())
        
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        goto = "__end__"
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="planner")],
            "full_plan": full_response,
            "tokens": token_count.get_token_count()
        },
        goto=goto,
    )

logger = logging.getLogger(__name__) # Ensure logger is configured

def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """Coordinator node that communicates with customers, showing only non-JSON context."""
    logger.info("Coordinator talking.")  
    #Hyde Coder Part
    #--------------------------------------------------------
    logger.info(f"Corrdinator Starting State Messages: {state["messages"][0].content}")
    hyde_detailed_prompt = ""
    prompt_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state
    }
    # Get and format the prompt template
    template = get_prompt_template('hyde_coder')
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=template,
    ).format(**prompt_vars)

    # Prepare messages for LLM
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": str(state["messages"][0].content)
        }
    ]
    # Get LLM response
    llm = get_llm_by_type("basic", schema=get_response_schema("hyde_coder"))
    try:
        response = llm.invoke(messages)
        hyde_detailed_prompt = response.content
        try:
            # Extract only the JSON part from hyde_detailed_prompt
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', hyde_detailed_prompt, re.DOTALL)
            if json_match:
                hyde_detailed_prompt = json_match.group(1)
            else:
                # Fallback: try to extract the first {...} block
                brace_match = re.search(r'(\{.*?\})', hyde_detailed_prompt, re.DOTALL)
                if brace_match:
                    hyde_detailed_prompt = brace_match.group(1)
            data = json.loads(hyde_detailed_prompt)
            hyde_detailed_prompt = data["detailed_prompt"]
        except json.JSONDecodeError:
            data = dict(hyde_detailed_prompt)
            hyde_detailed_prompt = data.get("detailed_prompt")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        token_count.set_token_count(token_count.token_count(response.content))      
        logger.info("Token count after Hyde Coder: %s", token_count.get_token_count())
        logger.info(f"Hyde Code Response: {hyde_detailed_prompt}")
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
        goto = "__end__" 
    logger.info(f"User Prompt: {state['messages'][0].content}")
    logger.info(f"Hyde Coder Response: {hyde_detailed_prompt}")
        
    #Core existing Logic
    logger.info(f"State Messgaes After Hyde Coder response: {state["messages"][0].content}")
    logger.info(f"Hyde Response: {hyde_detailed_prompt}")
    messages = apply_prompt_template("coordinator", state)
    messages.append(hyde_detailed_prompt)
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"], schema=get_response_schema('coordinator'), temperature=0.6).invoke(messages)
    
    logger.debug(f"Current state messages: {state['messages']}")
    # Keep original response
    response_content_raw = response.content
    token_count.set_token_count(token_count.token_count(response_content_raw))
    # state.get("checklist_manager").update_tokens(token_count.get_token_count())

    logger.info("token count after coordinator: %d", token_count.get_token_count())
    # Process JSON for internal use
    response_content_repaired = repair_json_output(response_content_raw)
    logger.debug(f"Coordinator full response: {response_content_raw}")
    # Extract non-JSON context to show user
    user_display_content = extract_user_content(response_content_raw)
    
    # Set the user-visible content
    response.content = user_display_content
    
    #--------------------------------------------------------
    # Handle planner handoff
    goto = "__end__"
    additional_update = {}

    if "handoff_to_planner()" in response_content_raw or "handofftoplanner()" in response_content_raw or "handoff_to_planner()" in response.content:
        # extract_and_save_json(response_content_raw)
        try:
            requirements = json.loads(response_content_repaired)
            additional_update["requirements"] = requirements
            goto = "planner"
        except json.JSONDecodeError:
            logger.error(f"Error parsing requirements: {response_content_raw}")
            goto = "__end__"

    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        goto=goto,
        update={
            "messages": [
                HumanMessage(
                    content=response_content_raw,
                    name="coordinator",
                )
            ],
            "tokens": token_count.get_token_count(),
            **additional_update
        }
    )

def extract_user_content(full_content: str) -> str:
    """Extracts non-JSON parts of the response for user display."""
    # Remove JSON blocks (both ```json``` and raw {})
    no_json = re.sub(r'```json.*?```', '', full_content, flags=re.DOTALL)
    no_json = re.sub(r'\{.*?\}', '', no_json, flags=re.DOTALL)
    
    # Remove technical markers like handoff_to_planner()
    # no_json = no_json.replace("handoff_to_planner()", "")
    # no_json = no_json.replace("handoff_to_planner()", "")
    
    # Clean up resulting whitespace
    return "\n".join(line.strip() for line in no_json.splitlines() if line.strip())

def reporter_node(state: State) -> Command[Literal["supervisor"]]:
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    messages = apply_prompt_template("reporter", state)
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"], schema=get_response_schema('reporter'), temperature=0.6).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    response_content = str(response.content)
    token_count.set_token_count(token_count.token_count(response_content))
    state.get("checklist_manager").update_tokens(token_count.get_token_count())
    logger.info("Token count after reporter: %d", token_count.get_token_count())
    response_content = repair_json_output(response_content)

    # Todo: Add report to state

    logger.debug(f"reporter response: {response_content}")
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="reporter",
                )
            ],
            "tokens": token_count.get_token_count(),
            "report": response_content
        },
        goto="supervisor",
    )

def diagram_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the diagram agent that generates diagrams."""
    logger.info("Diagram agent starting task")
    template = get_prompt_template('diagram_generator')
    directory_structure = state.get('directory_structure',"")
    prompt_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        "directory_structure": directory_structure,
        **state  # Include other state variables
    }
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME","directory_structure"],
        template=template,
    ).format(**prompt_vars)

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": state["messages"][-1].content if state["messages"] else ""
        }
    ]

    llm = get_llm_by_type("basic", schema=get_response_schema("diagram_generator"), temperature=0.8)
    response = llm.invoke(messages)
    token_count.set_token_count(token_count.token_count(str(response.content)))
    # state.get("checklist_manager").update_tokens(token_count.get_token_count())
    logger.info("Token count after diagram generation: %d", token_count.get_token_count())
    logger.debug(f"Diagram agent response: {response}")
    logger.info("Diagram agent completed task")
    logger.info(f"Tokens in  state till now: {state.get("tokens")} for the session: {state.get("session_id")}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response.content,  # Corrected: Passing the content string
                    name="diagram",
                )
            ],
            "component_diagram": response.content,
            "tokens": token_count.get_token_count()
        },
        goto="supervisor",
    )

"""
##### Terraform Generation

terraform Solution architect (image generation and requiement analsis)
terraform planner
terraform directory
terraform engineer
terraform script executor
    terraform init
    terraform validate
    terraform plan
    terraform apply

depployer
    ssh setup
    scp code push
    ssh code setup
    server begins

"""

def terraform_generator_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the Terraform Generator that creates infrastructure configurations."""
    logger.info("Terraform Generator starting task")

    try:
        # Get directory structure and code plan from state
        directory_structure = state.get('full_plan')
        if not directory_structure:
            logger.warning("No directory structure found in state")
            return Command(goto="supervisor")

        # Parse directory_structure if it's a string
        if isinstance(directory_structure, str):
            try:
                directory_structure = json.loads(directory_structure)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse directory_structure JSON: {e}")
                return Command(goto="supervisor")

        # Ensure directory_structure is a dictionary
        if not isinstance(directory_structure, dict):
            logger.error(f"Invalid directory_structure type: {type(directory_structure)}")
            return Command(goto="supervisor")

        # Update report with project name
        global report
        report["project_name"] = directory_structure.get("project_name", "sample_project")
        project_path = f"projects/{report['project_name']}"

        # Generate Terraform files
        terraform_generator_main(project_path=project_path, report=report)

        # Initialize and apply Terraform
        logger.info("Initializing and applying Terraform configuration")
        terraform_cmds = [
            "terraform init",
            "terraform plan",
            "terraform apply -auto-approve"
        ]
        for cmd in terraform_cmds:
            output = bash_tool.invoke(f"cd terraform_output && {cmd}")
            logger.debug(f"Terraform command '{cmd}' output: {output}")

        # Get instance public IP
        logger.info("Retrieving instance public IP")
        output = bash_tool.invoke("cd terraform_output && terraform output -raw instance_1_public_ip")
        instance_ip = output.strip()
        if not instance_ip:
            raise ValueError("Failed to retrieve instance IP from Terraform output")

        logger.info(f"Instance IP: {instance_ip}")

        report["instance_ip"] = instance_ip

        # Get deployment commands
        # get the readme.md file content from 'f"projects/{project_name}/README.md"'
        with open(f"projects/{report['project_name']}/README.md", "r") as f:
            readme_content = f.read()

        prompt_vars = {
            "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
            **state
        }
        # Get and format the prompt template
        template = get_prompt_template('terraform_deployer')
        system_prompt = PromptTemplate(
            input_variables=["CURRENT_TIME"],
            template=template,
        ).format(**prompt_vars)

        # Prepare messages for LLM
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {"role": "user", "content": readme_content}
        ]
        deployment_commands = get_llm_by_type("basic", schema=get_response_schema("terraform_deployer")).invoke(messages)
        deployment_commands = str(deployment_commands.content)
        deployment_commands = repair_json_output(deployment_commands)
        deployment_commands = json.loads(deployment_commands)
        deployment_cmds = " && ".join(deployment_commands.get("commands", []))

        logging.info(f"Deployment commands: {deployment_commands}")

        # Prepare deployment commands
        key_path = "vibecoder-key.pem"
        deployment_cmds = [
            # Set key permissions
            f"icacls {key_path} /inheritance:r",
            f'icacls {key_path} /grant:r "%USERNAME%":"(R,W)"',
            f'icacls {key_path} /remove "NT AUTHORITY\\Authenticated Users"',

            # Wait for instance to be ready
            "timeout /t 30",

            # Prepare remote directory
            f'ssh -i {key_path} -o StrictHostKeyChecking=no ec2-user@{instance_ip} "mkdir -p /home/ec2-user/app"',

            # Copy source code
            f'scp -i {key_path} -o StrictHostKeyChecking=no source_code.zip ec2-user@{instance_ip}:/home/ec2-user/app/',

            # Extract and deploy
            f'ssh -i {key_path} -o StrictHostKeyChecking=no ec2-user@{instance_ip} "cd /home/ec2-user/app && unzip -o source_code.zip"',

            # Execute deployment commands
            f'ssh -i {key_path} -o StrictHostKeyChecking=no ec2-user@{instance_ip} "{deployment_cmds}"',

            # Print access information
            f"echo http://{instance_ip}"
        ]

        # Execute deployment commands
        logger.info("Starting deployment to instance")
        for cmd in deployment_cmds:
            output = bash_tool.invoke(f"cd terraform_output && {cmd}")
            logger.debug(f"Deployment command output: {output}")

        logger.info("Terraform Generator completed task successfully")

        return Command(
            goto="supervisor", 
            update={
                "is_terraform_generated": True,
            }
        )

    except Exception as e:
        logger.error(f"Error in terraform_generator_node: {str(e)}", exc_info=True)
        report["error"] = str(e)
        return Command(
            goto="supervisor", 
            update={
                "is_terraform_generated": True,
                "error": str(e)
            }
        )