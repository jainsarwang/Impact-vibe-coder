# Complete Response Schemas for All Coders

from google import genai

# Existing schemas (provided as reference)
planner_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["thought", "project_name", "title", "steps"],
    properties = {
        "thought": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "project_name": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "title": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "steps": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.OBJECT,
                required = ["agent_name", "title", "description"],
                properties = {
                    "agent_name": genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                    "title": genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                    "description": genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                    "note": genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                },
            ),
        ),
    },
)

supervisor_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["next"],
    properties = {
        "next": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

diagram_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["diagram"],
    properties = {
        "diagram": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Directory Generator Response Schema
directory_generator_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["project_overview", "directory_structure", "file_documentation", "api_endpoints", "data_models", "dependencies"],
    properties = {
        "project_overview": genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["name", "description", "stack"],
            properties = {
                "name": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "description": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "stack": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        ),
        "directory_structure": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "file_documentation": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "api_endpoints": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "data_models": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "dependencies": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
    },
)

# Import Export Response Schema
import_export_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["project_overview", "directory_structure", "file_documentation", "api_endpoints", "data_models", "dependencies"],
    properties = {
        "project_overview": genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["name", "description", "stack"],
            properties = {
                "name": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "description": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "stack": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        ),
        "directory_structure": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "file_documentation": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "api_endpoints": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "data_models": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "dependencies": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
    },
)

# Version Resolver Response Schema
version_resolver_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["project_overview", "directory_structure", "file_documentation", "api_endpoints", "data_models", "dependencies"],
    properties = {
        "project_overview": genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["name", "description", "stack"],
            properties = {
                "name": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "description": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "stack": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        ),
        "directory_structure": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "file_documentation": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "api_endpoints": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "data_models": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "dependencies": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
    },
)

# Code Planner Response Schema
code_planner_response = genai.types.Schema(
    type = genai.types.Type.ARRAY,
    items = genai.types.Schema(
        type = genai.types.Type.OBJECT,
        required = ["coder", "file", "next_coder_instruction", "functions", "variables", "imports", "exports", "api_endpoints", "data_models", "dependencies"],
        properties = {
            "coder": genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
            "file": genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
            "next_coder_instruction": genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
            "note": genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
            "functions": genai.types.Schema(
                type = genai.types.Type.OBJECT,
            ),
            "variables": genai.types.Schema(
                type = genai.types.Type.OBJECT,
            ),
            "imports": genai.types.Schema(
                type = genai.types.Type.OBJECT,
            ),
            "exports": genai.types.Schema(
                type = genai.types.Type.ARRAY,
                items = genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
            ),
            "api_endpoints": genai.types.Schema(
                type = genai.types.Type.OBJECT,
            ),
            "data_models": genai.types.Schema(
                type = genai.types.Type.OBJECT,
            ),
            "dependencies": genai.types.Schema(
                type = genai.types.Type.OBJECT,
            ),
        },
    ),
)

# Model Coder Response Schema
model_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Controller Coder Response Schema
controller_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Route Coder Response Schema
route_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Service Coder Response Schema
service_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Utility Coder Response Schema
utility_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# DB Coder Response Schema
db_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Config Coder Response Schema
config_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Frontend Coder Response Schema
frontend_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Test Coder Response Schema
test_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Backend Coder Response Schema
backend_coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# General Coder Response Schema
coder_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["FILE", "programming_language", "code"],
    properties = {
        "FILE": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "programming_language": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
        "code": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# Version Resolver Response Schema 
version_resolver_response = genai.types.Schema(
    type = genai.types.Type.OBJECT,
    required = ["dependencies"],
    properties = {
        "dependencies": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "corrected_dependencies": genai.types.Schema(
            type = genai.types.Type.OBJECT,
        ),
        "issues_found": genai.types.Schema(
            type = genai.types.Type.ARRAY,
            items = genai.types.Schema(
                type = genai.types.Type.STRING,
            ),
        ),
        "resolution_summary": genai.types.Schema(
            type = genai.types.Type.STRING,
        ),
    },
)

# terraform planner Response Schema
# TODO: Needs to be defined properly
# terraform_planner_response = genai.types.Schema(
#     type = genai.types.Type.OBJECT,
#     required = ["agent", ''],
#     properties = {
#         "agent": genai.types.response_schema(
#             type = genai.types.Type.STRING
#         )
#     }
# )

# Complete Response Schema Dictionary
response_schema = {
    "planner": planner_response,
    "supervisor": supervisor_response,
    "diagram": diagram_response,
    "directory_generator": directory_generator_response,
    "import_export": import_export_response,
    "version_resolver": version_resolver_response,
    "code_planner": code_planner_response,
    "model_coder": model_coder_response,
    "controller_coder": controller_coder_response,
    "route_coder": route_coder_response,
    "service_coder": service_coder_response,
    "utility_coder": utility_coder_response,
    "db_coder": db_coder_response,
    "config_coder": config_coder_response,
    "frontend_coder": frontend_coder_response,
    "test_coder": test_coder_response,
    "coder": coder_response,
}



def get_response_schema(agent_name: str):
    if agent_name not in response_schema:
        return None

    return response_schema[agent_name]

__all__ = [
    "get_response_schema",
]