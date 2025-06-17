# Terraform Generator Agent

A standalone agent that uses Google's Gemini LLM to generate Terraform configurations based on project requirements.

## Features

- Generates complete Terraform configurations using Gemini LLM
- Validates input requirements using Pydantic models
- Supports multiple cloud providers (AWS, Azure, GCP)
- Generates consistent, well-documented Terraform code
- Includes variable validation and meaningful outputs

## Prerequisites

- Python 3.8+
- Google API key for Gemini

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google API key:
```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Import and initialize the agent:
```python
from src.terraform_agent import TerraformAgent

agent = TerraformAgent()
```

2. Define your project requirements:
```python
requirements = {
    "cloud_provider": "aws",
    "region": "ap-south-1",
    "application_type": "web-app",
    "environments": ["dev", "staging", "prod"],
    "compute": {
        "instance_type": "t2.micro",
        "scaling_requirements": {
            "min_instances": 1,
            "max_instances": 3
        }
    },
    "storage": {
        "type": "database",
        "size": "20GB"
    },
    "networking": {
        "public_access": True,
        "load_balancer": True,
        "cdn_enabled": False
    },
    "security": {
        "compliance_requirements": ["SOC2"],
        "encryption_required": True
    }
}
```

3. Generate Terraform configuration:
```python
result = agent.generate(requirements)
```

4. The generated files will be saved in the `output` directory.

## Input Format

The agent expects a JSON object with the following structure:

```json
{
  "cloud_provider": "aws|azure|gcp",
  "region": "primary-region",
  "application_type": "web-app|microservices|data-pipeline|ml-platform",
  "environments": ["dev", "staging", "prod"],
  "compute": {
    "instance_type": "size-specification",
    "scaling_requirements": {
      "min_instances": number,
      "max_instances": number
    }
  },
  "storage": {
    "type": "database|object-storage|file-system",
    "size": "storage-requirements"
  },
  "networking": {
    "public_access": boolean,
    "load_balancer": boolean,
    "cdn_enabled": boolean
  },
  "security": {
    "compliance_requirements": ["SOC2", "HIPAA", "PCI"],
    "encryption_required": boolean
  }
}
```

## Output

The agent generates the following Terraform files:

- `main.tf` - Main infrastructure configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output definitions
- `versions.tf` - Provider and version constraints
- `terraform.tfvars.example` - Example variable values

## Testing

Run the test script to verify the agent's functionality:

```bash
python test_agent.py
```

## Integration with LangChain

This agent is designed to be easily integrated with LangChain. The `TerraformAgent` class can be used as a tool or agent within a LangChain workflow.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 