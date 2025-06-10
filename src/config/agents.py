from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision", "version_llm", "image_gen"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",  # 协调默认使用basic llm
    "planner": "reasoning",  # 计划默认使用basic llm
    "supervisor": "reasoning",  # 决策使用basic llm
    "researcher": "reasoning",  # 简单搜索任务使用basic llm
    "directory_generator" : "basic",
    "import-export": "basic",
    "code_planner": "basic",
    "coder_master": "basic",
    "model_coder": "basic",
    "controller_coder": "basic",
    "route_coder": "basic",
    "service_coder": "basic",
    "utility_coder": "basic",
    "config_coder": "basic",
    "test_coder": "basic",
    "frontend_coder": "basic",
    "db_coder": "basic",
    "figma_coder": "image_gen",
    "coder": "basic",
    "frontend_coder":"basic",
    "backend_coder":"basic",
    "browser": "vision",  # 浏览器操作使用vision llm
    "reporter": "reasoning",  # 编写报告使用basic llm
    "version_resolver": "version_llm",
    "terraform_planner": "basic",
    "validator":"basic"
}
