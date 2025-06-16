import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ComputeConfig(BaseModel):
    instance_type: str
    scaling_requirements: Dict[str, int]

class StorageConfig(BaseModel):
    type: str
    size: str

class NetworkingConfig(BaseModel):
    public_access: bool
    load_balancer: bool
    cdn_enabled: bool

class SecurityConfig(BaseModel):
    compliance_requirements: List[str]
    encryption_required: bool

class ProjectRequirements(BaseModel):
    cloud_provider: str = Field(..., pattern="^(aws|azure|gcp)$")
    region: str
    application_type: str = Field(..., pattern="^(web-app|microservices|data-pipeline|ml-platform)$")
    environments: List[str]
    compute: ComputeConfig
    storage: StorageConfig
    networking: NetworkingConfig
    security: SecurityConfig

class TerraformAgent:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Terraform agent with Gemini API."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass it to the constructor.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Load templates
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.output_dir = Path(__file__).parent.parent / "output"

    def _generate_terraform_config(self, requirements: ProjectRequirements) -> Dict:
        """Generate Terraform configuration using Gemini."""
        prompt = self._create_prompt(requirements)
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text)

    def _create_prompt(self, requirements: ProjectRequirements) -> str:
        """Create a prompt for the LLM to generate Terraform configuration."""
        return f"""Generate a complete Terraform configuration for the following requirements:
{requirements.json(indent=2)}

Follow these guidelines:
1. Use consistent snake_case naming
2. Include comprehensive variable descriptions
3. Add appropriate resource tags
4. Implement validation rules
5. Generate meaningful outputs

Generate the following files:
1. main.tf - Main infrastructure configuration
2. variables.tf - Variable definitions
3. outputs.tf - Output definitions
4. versions.tf - Provider and version constraints
5. terraform.tfvars.example - Example variable values

Format the response as a JSON object with the following structure:
{{
    "main.tf": "content",
    "variables.tf": "content",
    "outputs.tf": "content",
    "versions.tf": "content",
    "terraform.tfvars.example": "content"
}}"""

    def _parse_response(self, response: str) -> Dict:
        """Parse the LLM response into a dictionary of Terraform files."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")

    def generate(self, requirements: Dict) -> Dict:
        """Generate Terraform configuration from requirements."""
        # Validate requirements
        validated_requirements = ProjectRequirements(**requirements)
        
        # Generate configuration
        terraform_files = self._generate_terraform_config(validated_requirements)
        
        # Save files
        self._save_files(terraform_files)
        
        return {
            "configuration": validated_requirements.dict(),
            "terraform_files": terraform_files
        }

    def _save_files(self, files: Dict[str, str]):
        """Save generated Terraform files to the output directory."""
        self.output_dir.mkdir(exist_ok=True)
        
        for filename, content in files.items():
            file_path = self.output_dir / filename
            with open(file_path, "w") as f:
                f.write(content) 