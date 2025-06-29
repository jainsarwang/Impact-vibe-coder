from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template, apply_prompt_template_planner, apply_prompt_template_for_coder
from src.tools import (
    bash_tool,
    browser_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
    project_zip_tool,
    read_file_tool
)

from src.llms.llm import generate_image_with_gemini, get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from ..graph.types import State
from ..utils import get_response_schema

# Create agents using configured LLM types

research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"], temperature=0.6),
    tools=[tavily_tool, crawl_tool],
    prompt=lambda state: apply_prompt_template("researcher", state)
)

directory_generator_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['directory_generator'], temperature=0.6),
    tools=[],
    prompt=lambda state: apply_prompt_template("directory_generator", state)
)

def coder_wrapper(react_agent):
    def intermediate(state: State):
        agent = react_agent(state)
        return agent.invoke(state)
    return intermediate

coder_master_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['coder_master']),
    tools=[browser_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template("coder_master", state)
)

import_export_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["import-export"]),
    tools=[browser_tool],
    prompt=lambda state: apply_prompt_template("import-export", state)
)

model_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['model_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("model_coder", app_state)
))
controller_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['controller_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("controller_coder", app_state)
))
route_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['route_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("route_coder", app_state)
))
service_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['service_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("service_coder", app_state)
))
utility_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['utility_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("utility_coder", app_state)
))
config_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['config_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("config_coder", app_state)
))
test_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['test_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("test_coder", app_state)
))
frontend_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['frontend_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("frontend_coder", app_state)
))

db_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['db_coder'], temperature=0.8),
    tools=[python_repl_tool, read_file_tool],
    prompt=lambda state: apply_prompt_template_for_coder("db_coder", app_state)
))
figma_coder_agent = lambda app_state: generate_image_with_gemini(
    prompt=app_state['coder_instruction'],
    temperature=0.8
)

# coder_agent = create_react_agent(
#     get_llm_by_type(AGENT_LLM_MAP["coder"]),
#     tools=[python_repl_tool, bash_tool,project_zip_tool],
#     prompt=lambda state: apply_prompt_template("coder", state),
# )

# frontend_coder_agent = create_react_agent(
#     get_llm_by_type(AGENT_LLM_MAP["frontend_coder"]),
#     tools=[python_repl_tool, bash_tool, project_zip_tool],
#     prompt=lambda state: apply_prompt_template("frontend_coder", state),
# )

# backend_coder_agent = create_react_agent(
#     get_llm_by_type(AGENT_LLM_MAP["backend_coder"]),
#     tools=[python_repl_tool, bash_tool, project_zip_tool],
#     prompt=lambda state: apply_prompt_template("backend_coder", state),
# )

browser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["browser"]),
    tools=[browser_tool],
    prompt=lambda state: apply_prompt_template("browser", state)
)

version_agent =  create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["version_resolver"], temperature=0.6),
    tools=[bash_tool], 
    prompt=lambda state: apply_prompt_template("version_resolver", state)
)

terraform_planner_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["terraform_planner"]),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template_planner("terraform_planner", state)
)