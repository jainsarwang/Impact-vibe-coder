import logging
import os
import re
import json
from datetime import datetime
from typing import List, Union

from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt.chat_agent_executor import AgentState
from ..graph.types import State


def get_prompt_template(prompt_name: str) -> str:
    """Loads and formats prompt template from markdown file."""
    template = open(os.path.join(os.path.dirname(__file__), f"{prompt_name}.md")).read()
    # Escape curly braces using backslash
    template = template.replace("{", "{{").replace("}", "}}")
    # Replace `<<VAR>>` with `{VAR}`
    template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
    return template


def apply_prompt_template(prompt_name: str, state: AgentState) -> List[dict]:
    """Base prompt template application."""
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"), **state)
    return [{"role": "system", "content": system_prompt}] + state["messages"]


def apply_prompt_template_for_coder(prompt_name: str, state: State) -> List[dict]:
    """Specialized prompt template for coding agents."""
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME", "ADDITIONAL_RULES"],
        template=get_prompt_template(prompt_name),
    ).format(
        CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        ADDITIONAL_RULES=get_prompt_template('common_coder'),
        **state
    )
    
    return [
            {"role": "system", "content": system_prompt}
        ] + [
            {
                "role": "user", 
                "content": state["coder_instruction"] + "And this is the required research content to generate the files." +state.get("researched_content"," ") +"Carefully and mandatorily follow this component diagram" +state.get("component_diagram","")
            }
        ]


def apply_prompt_template_for_version_resolver(state: State) -> List[dict]:
    """Prompt template for version resolution agent."""
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME", "error_log", "dependencies", "python_version", "node_version"],
        template=get_prompt_template("version_resolver"),
    ).format(
        CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        error_log=state.get("error_log", "No error log provided"),
        dependencies=state.get("dependencies", "No dependency info"),
        python_version=state.get("python_version", "Unknown"),
        node_version=state.get("node_version", "Unknown")
    )
    return [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": state["version_issue"]}]


def apply_prompt_template_planner(prompt_name: str, state: AgentState) -> List[dict]:
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
            project_requirements=json.dumps(project_requirements, indent=2),
            **state
        )
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    
    except FileNotFoundError:
        raise ValueError("project_requirements.json file not found")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in project_requirements.json")
    except Exception as e:
        raise ValueError(f"Error applying prompt template: {str(e)}")


__all__ = [
    "get_prompt_template",
    "apply_prompt_template",
    "apply_prompt_template_for_coder",
    "apply_prompt_template_for_version_resolver",
    "apply_prompt_template_planner"
]