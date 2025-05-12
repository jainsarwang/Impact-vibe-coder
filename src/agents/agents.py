from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from src.prompts import apply_prompt_template, apply_prompt_template_planner
from src.tools import (
    bash_tool,
    browser_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
    project_zip_tool,
    manage_project_lifecycle
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

coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["coder"]),
    tools=[python_repl_tool, bash_tool,project_zip_tool],
    prompt=lambda state: apply_prompt_template("coder", state),
)

frontend_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["frontend_coder"]),
    tools=[python_repl_tool, bash_tool, project_zip_tool],
    prompt=lambda state: apply_prompt_template("frontend_coder", state),
)

backend_coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["backend_coder"]),
    tools=[python_repl_tool, bash_tool, project_zip_tool],
    prompt=lambda state: apply_prompt_template("backend_coder", state),
)

browser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["browser"]),
    tools=[browser_tool],
    prompt=lambda state: apply_prompt_template("browser", state),
)

