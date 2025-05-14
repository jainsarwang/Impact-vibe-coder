from langgraph.graph import StateGraph, START

from .types import State
from .nodes import (
    supervisor_node,
    research_node,
    directory_generator_node,
    code_planner_node,
    coder_master_node,
    model_coder_node,
    controller_coder_node,
    route_coder_node,
    service_coder_node,
    utility_coder_node,
    config_coder_node,
    test_coder_node,
    frontend_coder_node,
    db_coder_node,
    # frontend_code_node,
    # code_node,
    # backend_code_node,
    coordinator_node,
    browser_node,
    reporter_node,
    planner_node,
)


def build_graph():
    """Build and return the agent workflow graph."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("planner", planner_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("directory_generator", directory_generator_node)
    builder.add_node("code_planner", code_planner_node)
    builder.add_node("coder_master", coder_master_node)
    builder.add_node("model_coder", model_coder_node)
    builder.add_node("controller_coder", controller_coder_node)
    builder.add_node("route_coder", route_coder_node)
    builder.add_node("service_coder", service_coder_node)
    builder.add_node("utility_coder", utility_coder_node)
    builder.add_node("config_coder", config_coder_node)
    builder.add_node("test_coder", test_coder_node)
    builder.add_node("frontend_coder", frontend_coder_node)
    builder.add_node("db_coder", db_coder_node)
    # builder.add_node("coder", code_node)
    # builder.add_node("frontend_coder", frontend_code_node)
    # builder.add_node("backend_coder", backend_code_node)
    builder.add_node("browser", browser_node)
    builder.add_node("reporter", reporter_node)
    return builder.compile()
