from typing import Dict, List
import os
from pathlib import Path
from .terraform_planner import TerraformPlan, EC2InstanceConfig

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

class TerraformGenerator:
    def __init__(self, output_dir: str = "terraform_output"):
        self.output_dir = output_dir
        self._ensure_output_dir()
        self._setup_aws_credentials()

    def _ensure_output_dir(self):
        """Creates the output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def _setup_aws_credentials(self):
        """Sets up AWS credentials in the output directory"""
        aws_dir = os.path.join(self.output_dir, ".aws")
        os.makedirs(aws_dir, exist_ok=True)

        credentials_content = f"""[default]
aws_access_key_id = {AWS_ACCESS_KEY}
aws_secret_access_key = {AWS_SECRET_KEY}
region = {AWS_REGION}
# This is a placeholder for AWS credentials. Replace with your actual credentials.
"""
        credentials_path = os.path.join(aws_dir, "credentials")
        with open(credentials_path, 'w') as f:
            f.write(credentials_content)

    def generate_terraform_scripts(self, plan: TerraformPlan) -> Dict[str, str]:
        """
        Generates Terraform configuration files based on the provided plan
        Returns a dictionary of generated file paths
        """
        generated_files = {}
        
        # Generate main.tf
        main_tf = self._generate_main_tf(plan)
        main_tf_path = os.path.join(self.output_dir, "main.tf")
        with open(main_tf_path, 'w') as f:
            f.write(main_tf)
        generated_files['main.tf'] = main_tf_path

        # Generate variables.tf
        variables_tf = self._generate_variables_tf(plan)
        variables_tf_path = os.path.join(self.output_dir, "variables.tf")
        with open(variables_tf_path, 'w') as f:
            f.write(variables_tf)
        generated_files['variables.tf'] = variables_tf_path

        # Generate outputs.tf
        outputs_tf = self._generate_outputs_tf(plan)
        outputs_tf_path = os.path.join(self.output_dir, "outputs.tf")
        with open(outputs_tf_path, 'w') as f:
            f.write(outputs_tf)
        generated_files['outputs.tf'] = outputs_tf_path

        return generated_files

    def _generate_main_tf(self, plan: TerraformPlan) -> str:
        """Generates the main Terraform configuration file"""
        main_tf = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  shared_credentials_files    = [".aws/credentials"]
  profile                     = "default"
}

"""
        # Add EC2 instance configurations
        for i, instance in enumerate(plan.ec2_instances):
            main_tf += f"""
resource "aws_instance" "app_server_{i}" {{
  ami           = "{instance.ami_id}"
  instance_type = "{instance.instance_type}"
  
  tags = {{
"""
            for key, value in instance.tags.items():
                main_tf += f'    {key} = "{value}"\n'
            main_tf += "  }\n}\n"

        return main_tf

    def _generate_variables_tf(self, plan: TerraformPlan) -> str:
        """Generates the variables Terraform configuration file"""
        return """variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}
"""

    def _generate_outputs_tf(self, plan: TerraformPlan) -> str:
        """Generates the outputs Terraform configuration file"""
        outputs = ""
        for i, instance in enumerate(plan.ec2_instances):
            outputs += f"""
output "instance_{i}_public_ip" {{
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app_server_{i}.public_ip
}}

output "instance_{i}_private_ip" {{
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.app_server_{i}.private_ip
}}
"""
        return outputs 