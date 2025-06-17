from typing import Dict

def get_response_schema(agent_type: str) -> Dict:
    """Get the response schema for a specific agent type."""
    schemas = {
        "terraform_coder": {
            "type": "object",
            "properties": {
                "configuration": {
                    "type": "object",
                    "properties": {
                        "cloud_provider": {"type": "string"},
                        "region": {"type": "string"},
                        "application_type": {"type": "string"},
                        "environments": {"type": "array", "items": {"type": "string"}},
                        "compute": {"type": "object"},
                        "storage": {"type": "object"},
                        "networking": {"type": "object"},
                        "security": {"type": "object"},
                        "tags": {"type": "object"}
                    },
                    "required": ["cloud_provider", "region", "application_type"]
                },
                "terraform_files": {
                    "type": "object",
                    "properties": {
                        "main.tf": {"type": "string"},
                        "variables.tf": {"type": "string"},
                        "outputs.tf": {"type": "string"},
                        "versions.tf": {"type": "string"},
                        "terraform.tfvars.example": {"type": "string"},
                        "README.md": {"type": "string"}
                    },
                    "required": ["main.tf", "variables.tf", "outputs.tf", "versions.tf"]
                },
                "deployment_instructions": {"type": "string"}
            },
            "required": ["configuration", "terraform_files", "deployment_instructions"]
        }
    }
    
    return schemas.get(agent_type, {}) 