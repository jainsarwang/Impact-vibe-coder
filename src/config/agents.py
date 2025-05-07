from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",  # 协调默认使用basic llm
    "planner": "reasoning",  # 计划默认使用basic llm
    "supervisor": "reasoning",  # 决策使用basic llm
    "researcher": "reasoning",  # 简单搜索任务使用basic llm
    "directory_generator" : "basic",
    "coder": "basic",
    "frontend_coder":"basic",
    "backend_coder":"basic",
    "browser": "vision",  # 浏览器操作使用vision llm
    "reporter": "reasoning",  # 编写报告使用basic llm
}
