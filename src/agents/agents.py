from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from src.prompts import apply_prompt_template, apply_prompt_template_planner, apply_prompt_template_for_coder
from src.tools import (
    bash_tool,
    browser_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
    project_zip_tool
)

from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from ..graph.types import State

# Create agents using configured LLM types
research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),
    tools=[tavily_tool, crawl_tool],
    prompt=lambda state: apply_prompt_template("researcher", state),
)

directory_generator_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['directory_generator']),
    tools=[browser_tool],
    prompt=lambda state: apply_prompt_template("directory_generator", state),
)

def coder_wrapper(react_agent):
    def intermediate(state: State):
        agent = react_agent(state)
        return agent.invoke(state)
    return intermediate

coder_master_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['coder_master']),
    tools=[browser_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template("coder_master", state),
)
model_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['model_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("model_coder", app_state),
))
controller_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['controller_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("controller_coder", app_state),
))
route_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['route_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("route_coder", app_state),
))
service_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['service_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("service_coder", app_state),
))
utility_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['utility_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("utility_coder", app_state),
))
config_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['config_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("config_coder", app_state),
))
test_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['test_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("test_coder", app_state),
))
frontend_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['frontend_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("frontend_coder", app_state),
))
db_coder_agent = coder_wrapper(lambda app_state: create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['db_coder']),
    tools=[bash_tool,python_repl_tool],
    prompt=lambda state: apply_prompt_template_for_coder("db_coder", app_state),
))

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
    prompt=lambda state: apply_prompt_template("browser", state),
)

version_agent =  create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["version_resolver"]),
    tools=[bash_tool], 
    prompt=lambda state: apply_prompt_template("version_resolver", state),
)