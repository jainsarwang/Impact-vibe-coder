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
from src.utils import executor,  repair_json_output
from .types import State
from ..utils import ChecklistManager
import re
import json

logger = logging.getLogger(__name__)

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
checklist_manager = ChecklistManager.ChecklistManager()

def research_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the researcher agent that performs research tasks."""
    logger.info("Research agent starting task")
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    response_content = result["messages"][-1].content

    logger.debug(f"Research agent response: {response_content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name="researcher",
                )
            ],
            "researched_content" : response_content
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
    extract_and_save_json(response_content, "directory_structure.json")

    # Initialize checklist from directory structure
    checklist_manager.initialize_from_directory(response_content)

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
    
def code_planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Code Planner node that generate the full plan for coder master."""
    logger.info("Code Planner generating full plan")

    directory_structure = state.get('directory_structure')
    if not directory_structure:
        logging.warning("No Directory Object in State, Going back to supervisor")
        return Command(goto='supervisor')

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
    llm = get_llm_by_type("basic")
    response = llm.invoke(messages)
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

        with open("code_planner.json", "w", encoding="utf-8") as f:
            json.dump(repaired_response, f, indent=2, ensure_ascii=False)

        # Update checklist from the plan
        checklist_manager.update_from_plan(repaired_response)
    except json.JSONDecodeError:
        logger.warning("Code Planner response is not a valid JSON")
        goto = "__end__"

    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="code_planner")],
            "code_plan": full_response,
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
        return Command(goto='supervisor')

    # Parse directory_structure if it's a string
    if isinstance(directory_structure, str):
        try:
            directory_structure = json.loads(directory_structure)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse directory_structure: {e}")
            return Command(goto='supervisor')

    # Initialize dependencies_values safely
    dependencies_values = {}
    try:
        dependencies_values = directory_structure.get("dependencies", {})
        if isinstance(dependencies_values, str):
            dependencies_values = json.loads(dependencies_values)
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Failed to parse dependencies: {e}")
        return Command(goto='supervisor')

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
    llm = get_llm_by_type("basic")
    try:
        response = llm.invoke(messages)
        full_response = response.content
        json_response = repair_json_output(full_response)
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        return Command(goto='supervisor')

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
        return Command(goto='supervisor')

    logger.info("Version Resolver work done")
    logger.debug(f"Updated dependencies: {directory_structure['dependencies']}")
    logger.info(directory_structure)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=str(parsed_response),
                    name="version_resolver",
                )
            ],
            "directory_structure": str(directory_structure)
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
    # Get the code plan string from state
    code_plan_str = state.get('code_plan')
    generated_files = state.get('generated_files', [])

    if not directory_structure or not code_plan_str:
        logging.warning("No Directory Structure or code plan in State. Going back to supervisor.")
        # Add a message indicating why we're going back
        return Command(goto='supervisor', update={
            "messages": state["messages"] + [
                HumanMessage(
                    content="Coder master cannot proceed: Missing directory structure or code plan.",
                    name="coder_master",
                )
            ]
        })

    # Load the code plan from the JSON string
    try:
        code_plan = json.loads(code_plan_str)
        # Ensure code_plan is a list, handle potential wrapper dict
        if not isinstance(code_plan, list):
            code_plan = code_plan.get("plan", [])
            if not isinstance(code_plan, list):
                logger.error("Code plan loaded but is not a list and has no 'plan' key list.")
                raise ValueError("Invalid code plan format")

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse or process code_plan JSON string: {e}")
        return Command(goto='__end__', update={
            "messages": state["messages"] + [
                HumanMessage(content=f"Error parsing code plan: {e}", name="coder_master")
            ]
        })

    # The individual coder nodes are responsible for marking the file as created
    # in the checklist *before* they return to the coder_master.
    # So, we just need to read the checklist's current state.

    # Get the next file to process from the checklist
    next_file_info = checklist_manager.get_next_file_to_process()

    if next_file_info:
        # Found a file that is planned but not yet created
        file_path_to_process = next_file_info['file_path']
        assigned_coder_name = next_file_info.get('coder')

        logger.info(f"Next file from checklist: {file_path_to_process}")
        logger.debug(f"Assigned coder: {assigned_coder_name}")

        # Validate the assigned coder name
        if assigned_coder_name not in CODER_AGENTS:
            logger.error(f"Checklist assigned an invalid coder '{assigned_coder_name}' for file '{file_path_to_process}'. Cannot delegate.")
            # Mark this file as problematic? Or return to supervisor for intervention?
            # For now, go to supervisor and log the error. The file remains uncreated.
            return Command(goto='supervisor', update={
                "messages": state["messages"] + [
                    HumanMessage(
                        content=f"Checklist error: Invalid coder '{assigned_coder_name}' for file '{file_path_to_process}'. Needs manual intervention or plan update.",
                        name="coder_master",
                    )
                ]
            })

        # Find the specific instruction for this file in the code plan
        # We need the original plan item JSON object to pass to the coder agent
        instruction_content = ""
        found_plan_item = None
        
        # Normalize paths for comparison when searching the plan
        normalized_file_path_to_process = checklist_manager._normalize_path(file_path_to_process)

        for item in code_plan:
            item_file_path = item.get("file")
            if item_file_path and checklist_manager._normalize_path(item_file_path) == normalized_file_path_to_process:
                # Pass the entire plan item for this file as instruction
                instruction_content = json.dumps(item, indent=2)
                logger.info(f"instruction_content: {instruction_content}")
                found_plan_item = item
                break

        if not found_plan_item:
            logger.warning(f"Could not find specific plan item for file '{file_path_to_process}' in the code_plan. Using a generic instruction.")
            # Create a basic instruction if not found in the plan details
            instruction_content = json.dumps({
                "file": file_path_to_process,
                "coder": assigned_coder_name,
                "description": f"Generate the content for the file '{file_path_to_process}' based on the overall project requirements provided previously."
            }, indent=2)


        # Prepare the update and goto command
        goto_agent = assigned_coder_name # Statically go to the assigned agent node

        logger.info(f"Delegating to agent: {goto_agent} for file: {file_path_to_process}")

        # Ensure the assigned agent name is in the list of possible transitions
        if goto_agent not in CODER_AGENTS:
            logger.error(f"Attempted to delegate to non-coder agent: {goto_agent}. Error in checklist or plan.")
            return Command(goto='supervisor', update={
                "messages": state["messages"] + [
                    HumanMessage(
                        content=f"Internal error: Checklist assigned non-coder agent '{goto_agent}' for file '{file_path_to_process}'.",
                        name="coder_master",
                    )
                ]
            })


        # Append a message from the coder_master indicating the delegation
        coder_master_message = f"Delegating file `{file_path_to_process}` to `{goto_agent}` agent based on the development checklist and plan."

        return Command(
            goto=goto_agent, # Directly go to the specific coder agent node
            update={
                # Append the master's decision message to the history
                "messages": state["messages"] + [HumanMessage(content=coder_master_message, name="coder_master")],
                # Pass the specific instruction for the coder
                "coder_instruction": instruction_content,
                # Keep track of the file currently being processed by the delegated agent
                "current_file_processing": file_path_to_process,
                # Keep the current list of generated files (updated by the previous coder node)
                "generated_files": generated_files
            }
        )

    else:
        # checklist_manager.get_next_file_to_process() returned None
        # This means all files marked with plan_created=True now also have file_created=True
        logger.info("Checklist indicates no more planned files need processing.")

        # Optional: Check for unplanned files that were created (could indicate issues)
        unplanned_created = checklist_manager.get_unplanned_files()
        completion_message = "Coding phase completed. All planned files have been processed."
        if unplanned_created:
            completion_message += f"\nNote: {len(unplanned_created)} files were created but were not in the original plan/checklist. Please review these files manually."
            logger.warning(f"Unplanned files created: {unplanned_created}")

        logger.info("Returning to supervisor.")

        # Clear state specific to the coding phase
        updated_state = deepcopy(state)
        updated_state["coder_instruction"] = None # Clear instruction
        updated_state["current_file_processing"] = None # Clear current file processing status
        # Keep generated_files as a record

        # Add a final message from the coder_master indicating completion
        updated_state["messages"].append(HumanMessage(content=completion_message, name="coder_master"))


        return Command(
            goto='supervisor', # Go back to supervisor to decide next phase (e.g., testing, wrap-up)
            update=updated_state
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
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error during agent '{prompt_name}' execution: {str(e)}",
                        name=prompt_name,
                    )
                ]
            },
            goto="coder_master",
        )

    logger.info(f"Coder agent '{prompt_name}' completed invocation.")

    response_content_raw = result["messages"][-1].content
    response_content_repaired = repair_json_output(response_content_raw)

    try:
        parsed_response = json.loads(response_content_repaired)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from '{prompt_name}': {e}. "
                        f"Raw response: '{response_content_raw[:500]}...', "
                        f"Repaired: '{response_content_repaired[:500]}...'")
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error parsing JSON response from '{prompt_name}': {str(e)}. "
                                f"Repaired content (start): {response_content_repaired[:200]}...",
                        name=prompt_name,
                    )
                ]
            },
            goto="coder_master",
        )

    current_generated_files = state.get('generated_files', [])
    newly_generated_this_run: List[str] = []
    processed_file_specs: List[Dict[str, str]] = []

    files_spec_from_llm = parsed_response.get("FILE")

    if isinstance(files_spec_from_llm, str):
        path = files_spec_from_llm
        content = parsed_response.get("code", "")
        processed_file_specs.append({"path": path, "content": content})
    elif isinstance(files_spec_from_llm, list):
        for item in files_spec_from_llm:
            path, content = None, None
            if isinstance(item, str):
                path = item
                content = parsed_response.get("code", "")
            elif isinstance(item, dict):
                path = item.get("path")
                content = item.get("content", parsed_response.get("code", ""))

            if path:
                processed_file_specs.append({"path": path, "content": content if content is not None else ""})
            else:
                logger.warning(f"'{prompt_name}' provided an item in 'FILE' list without a path: {item}")
    elif files_spec_from_llm is None:
        top_level_path = parsed_response.get("path")
        if top_level_path:
            top_level_content = parsed_response.get("code", "")
            processed_file_specs.append({"path": top_level_path, "content": top_level_content})
        else:
            logger.warning(f"'{prompt_name}' response had no 'FILE' key and no top-level 'path'. Response: {parsed_response}")
    else:
        logger.warning(f"'{prompt_name}' returned 'FILE' with unexpected type: {type(files_spec_from_llm)}. Value: {files_spec_from_llm}")

    for file_spec in processed_file_specs:
        file_path = file_spec.get("path")
        file_content = file_spec.get("content", "")

        if not file_path:
            logger.warning(f"'{prompt_name}' produced a file spec with no path. Spec: {file_spec}. Skipping.")
            continue

        try:
            # Normalize the file path
            file_path = os.path.normpath(file_path)

            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                logger.debug(f"Ensured directory exists: {dir_path} (for file {file_path})")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            newly_generated_this_run.append(file_path)
            logger.info(f"Successfully wrote file by '{prompt_name}': {file_path}")

            # Update checklist to mark file as created
            checklist_manager.mark_file_created(file_path)
            logger.debug(f"Checklist updated for file: {file_path}")

        except Exception as e:
            logger.error(f"Error writing file {file_path} by '{prompt_name}': {str(e)}", exc_info=True)

    updated_generated_files = list(set(current_generated_files + newly_generated_this_run))

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content_repaired,
                    name=prompt_name,
                )
            ],
            "generated_files": updated_generated_files
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
        return Command(goto='supervisor')

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
        llm = get_llm_by_type("basic")
        response = llm.invoke(messages)
        full_response = response.content

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

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=(full_response),
                    name="import-export",
                )
            ],
            "directory_structure": (full_response)
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
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error parsing 'coder_instruction' for 'figma_coder': {str(e)}",
                        name='figma_coder',
                    )
                ]
            },
            goto="coder_master",
        )

    try:
        response_parts = figma_coder_agent(state)
    except Exception as e:
        logger.error(f"Error invoking agent 'figma_coder': {str(e)}", exc_info=True)
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Error during agent 'figma_coder' execution: {str(e)}",
                        name='figma_coder',
                    )
                ]
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
            image.save(file_name)
            logger.info(f"Image saved successfully as {file_name}")
        
    current_generated_files = state.get('generated_files', [])
    state['generated_files'] = current_generated_files + [parsed_instruction.get("file", "")]

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="Image generated Successfully",
                    name='figma_coder',
                )
            ]
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
        with open("project_requirements.json") as f:
            project_requirement = f.read()
        
        logging.debug("**Executor Started")
        executor.execute(state, project_requirement)
        logging.debug("**Executor Ended")
        
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

logger = logging.getLogger(__name__) # Ensure logger is configured

def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """Coordinator node that communicates with customers, showing only non-JSON context."""
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    
    # Keep original response
    response_content_raw = response.content
    
    # Process JSON for internal use
    response_content_repaired = repair_json_output(response_content_raw)
    logger.debug(f"Coordinator full response: {response_content_raw}")
    
    # Extract non-JSON context to show user
    user_display_content = extract_user_content(response_content_raw)
    
    # Set the user-visible content
    response.content = user_display_content
    
    # Handle planner handoff
    goto = "__end__"
    if "handoff_to_planner()" in response_content_raw:
        # extract_and_save_json(response_content_raw)
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

    llm = get_llm_by_type("basic")
    response = llm.invoke(messages)
    logger.debug(f"Diagram agent response: {response}")
    logger.info("Diagram agent completed task")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response.content,  # Corrected: Passing the content string
                    name="diagram",
                )
            ],
            "component_diagram": response.content, 
        },
        goto="supervisor",
    )