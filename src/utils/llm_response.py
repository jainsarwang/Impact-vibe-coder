# Complete Response Schemas for All Coders

from typing import List, Dict, Optional
from pydantic import BaseModel, RootModel

# Planner Response Schema
class Step(BaseModel):
    agent_name: str
    title: str 
    description: str
    note: Optional[str] = None

class PlannerResponse(BaseModel):
    thought: str
    project_name: str
    title: str
    steps: List[Step]

# Supervisor Response Schema
class SupervisorResponse(BaseModel):
    next: str

# Diagram Response Schema  
class DiagramResponse(BaseModel):
    diagram: str

# Directory Generator Response Schema
class ProjectOverview(BaseModel):
    name: str
    description: str
    stack: List[str]

class DirectoryGeneratorResponse(BaseModel):
    project_overview: ProjectOverview
    directory_structure: Dict
    file_documentation: Dict
    api_endpoints: Dict
    data_models: Dict
    dependencies: Dict

# Import Export Response Schema
class ImportExportResponse(BaseModel):
    project_overview: ProjectOverview
    directory_structure: Dict
    file_documentation: Dict
    api_endpoints: Dict
    data_models: Dict
    dependencies: Dict

# Code Planner Response Schema
class CodePlannerItem(BaseModel):
    coder: str
    file: str
    next_coder_instruction: str
    note: Optional[str] = None
    functions: Dict
    variables: Dict
    imports: Dict
    exports: List[str]
    api_endpoints: Dict
    data_models: Dict
    dependencies: Dict
class CodePlannerResponse(RootModel):
    root: List[CodePlannerItem]

# Base Coder Response Schema
class CoderResponse(BaseModel):
    FILE: str
    programming_language: str
    code: str
    description: str

class HydeCoderResponse(BaseModel):
    detailed_prompt: str

# Version Resolver Response Schema
class VersionResolverResponse(BaseModel):
    dependencies: Dict
    corrected_dependencies: Optional[Dict] = None
    issues_found: Optional[List[str]] = None
    resolution_summary: Optional[str] = None

# Complete Response Schema Dictionary
response_schema = {
    "planner": PlannerResponse,
    "supervisor": SupervisorResponse,
    "diagram": DiagramResponse,
    "directory_generator": DirectoryGeneratorResponse,
    "import_export": ImportExportResponse,
    "version_resolver": VersionResolverResponse,
    "code_planner": CodePlannerResponse,
    "model_coder": CoderResponse,
    "controller_coder": CoderResponse,
    "route_coder": CoderResponse,
    "service_coder": CoderResponse,
    "utility_coder": CoderResponse,
    "db_coder": CoderResponse,
    "config_coder": CoderResponse,
    "frontend_coder": CoderResponse,
    "test_coder": CoderResponse,
    "backend_coder": CoderResponse,
    "coder": CoderResponse,
    "hyde_coder": HydeCoderResponse
}

def get_response_schema(agent_name: str):
    if agent_name not in response_schema:
        return None
    return response_schema[agent_name]

__all__ = [
    "get_response_schema",
]