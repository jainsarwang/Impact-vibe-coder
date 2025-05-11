from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from src.prompts import apply_prompt_template, apply_prompt_template_planner
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

coder_master_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['coder_master']),
    tools=[browser_tool],
    prompt=lambda state: apply_prompt_template("coder_master", state),
)
model_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['model_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("model_coder", state),
)
controller_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['controller_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("controller_coder", state),
)
route_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['route_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("route_coder", state),
)
service_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['service_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("service_coder", state),
)
utility_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['utility_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("utility_coder", state),
)
config_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['config_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("config_coder", state),
)
test_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['test_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("test_coder", state),
)
frontend_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['frontend_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("frontend_coder", state),
)
db_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP['db_coder']),
    tools=[bash_tool],
    prompt=lambda state: apply_prompt_template("db_coder", state),
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
    prompt=lambda state: apply_prompt_template("browser", state),
)
