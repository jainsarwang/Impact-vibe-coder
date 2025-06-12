import logging
import os
import re
import json
from datetime import datetime

from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt.chat_agent_executor import AgentState
from ..graph.types import State
from ..utils import token_count


def get_prompt_template(prompt_name: str) -> str:
    template = open(os.path.join(os.path.dirname(__file__), f"{prompt_name}.md")).read()
    # Escape curly braces using backslash
    template = template.replace("{", "{{").replace("}", "}}")
    # Replace `<<VAR>>` with `{VAR}`
    template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
    return template

def apply_prompt_template(prompt_name: str, state: AgentState) -> list:
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"), **state)
    token_count.set_token_count(token_count.token_count(system_prompt))
    logging.info("token_count_value: %d for prompt_name: %s", token_count.get_token_count(), prompt_name)
    return [{"role": "system", "content": system_prompt}] + state["messages"]

def apply_prompt_template_for_validator(prompt_name: str, state: State)->list:
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(CURRENT_TIME = datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),**state)
    validation_instruction = state.get("validation_instruction")
    return [{"role": "system", "content": system_prompt + validation_instruction}]

def apply_prompt_template_for_coder(prompt_name: str, state: State) -> list:
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(
        CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        ADDITIONAL_RULES = get_prompt_template('common_coder'),
        **state
    )
    token_count.set_token_count(token_count.token_count(system_prompt))
    logging.info("token_count_value: %d for prompt_name: %s", token_count.get_token_count(), prompt_name)
    logging.info("component_diagram: %s", state.get("component_diagram", ""))
    return [
            {"role": "system", "content": system_prompt}
        ] + [
            {
                "role": "user", 
                "content": state["coder_instruction"] + "And this is the required research content to generate the files." +state.get("researched_content"," ") +"Carefully and mandatorily follow this component diagram" +state.get("component_diagram","")+"Also find the content and path of a already existing file that you can use to generate the new file. " + state.get("previous_file_content", "") + "The path of the previous file is: " + state.get("previous_file_path", "")  
            }
        ]

def apply_prompt_template_planner(prompt_name: str, state: AgentState) -> list:
    """Applies prompt template for planner with proper JSON handling."""
    try:
        # Load project requirements from JSON file
        with open("project_requirements.json", "r", encoding="utf-8") as f:
            project_requirements = json.load(f)
        
        system_prompt = PromptTemplate(
            input_variables=["CURRENT_TIME", "project_requirements"],
            template=get_prompt_template(prompt_name),
        ).format(
            CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
            project_requirements=json.dumps(project_requirements, indent=2),  # Convert dict to formatted JSON string
            **state
        )
        token_count.set_token_count(token_count.token_count(system_prompt))
        logging.info("token_count_value: %d for prompt_name: %s", token_count.get_token_count(), prompt_name)
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    
    except FileNotFoundError:
        raise ValueError("project_requirements.json file not found")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in project_requirements.json")
    except Exception as e:
        raise ValueError(f"Error applying prompt template: {str(e)}")