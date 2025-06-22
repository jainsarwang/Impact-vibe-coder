from .env import (
    # AZURE Config
    AZURE_API_BASE,
    AZURE_API_KEY,
    AZURE_API_VERSION,
    # Reasoning LLM
    REASONING_MODEL,
    REASONING_BASE_URL,
    REASONING_API_KEY,
    REASONING_AZURE_DEPLOYMENT,
    # Basic LLM
    BASIC_MODEL,
    BASIC_BASE_URL,
    BASIC_API_KEY,
    BASIC_AZURE_DEPLOYMENT,
    # Vision-language LLM
    VL_MODEL,
    VL_BASE_URL,
    VL_API_KEY,
    VL_AZURE_DEPLOYMENT,
    # Other configurations
    CHROME_INSTANCE_PATH,
    CHROME_HEADLESS,
    CHROME_PROXY_SERVER,
    CHROME_PROXY_USERNAME,
    CHROME_PROXY_PASSWORD,
)
from .tools import TAVILY_MAX_RESULTS, BROWSER_HISTORY_DIR
from .agents import AGENT_LLM_MAP

# Team configuration
TEAM_MEMBERS = [
    "researcher",
    "browser",
    "reporter",
    "directory_generator",
    "import-export",
    "code_planner",
    "coder_master",
    "version_resolver",
    "diagram",
    "terraform_generator"
]

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
    "figma_coder",
]

__all__ = [
    # Reasoning LLM
    "REASONING_MODEL",
    "REASONING_BASE_URL",
    "REASONING_API_KEY",
    # Basic LLM
    "BASIC_MODEL",
    "BASIC_BASE_URL",
    "BASIC_API_KEY",
    # Vision-language LLM
    "VL_MODEL",
    "VL_BASE_URL",
    "VL_API_KEY",
    # Other configurations
    "TEAM_MEMBERS",
    "TAVILY_MAX_RESULTS",
    "CHROME_INSTANCE_PATH",
    "CHROME_HEADLESS",
    "CHROME_PROXY_SERVER",
    "CHROME_PROXY_USERNAME",
    "CHROME_PROXY_PASSWORD",
    "BROWSER_HISTORY_DIR",
    "CODER_AGENTS",
    "AGENT_LLM_MAP",
]
