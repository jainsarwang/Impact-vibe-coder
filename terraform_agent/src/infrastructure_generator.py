import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from .terraform_agent import TerraformAgent

class InfrastructureGenerator:
    def __init__(self, report_path: str, output_dir: Optional[str] = None):
        """
        Initialize infrastructure generator with report path
        
        Args:
            report_path: Path to the report.json file
            output_dir: Optional output directory for Terraform files
        """
        self.report_path = Path(report_path)
        self.output_dir = Path(output_dir) if output_dir else Path("terraform_output")
        self.terraform_agent = TerraformAgent()
        
    def _read_report(self) -> Dict:
        """Read and parse the report.json file"""
        if not self.report_path.exists():
            raise FileNotFoundError(f"Report file not found: {self.report_path}")
            
        with open(self.report_path, 'r') as f:
            return json.load(f)
            
    def _convert_report_to_requirements(self, report: Dict) -> Dict:
        """Convert report data to Terraform requirements format"""
        # Extract project information from report
        project_info = report.get('project_info', {})
        requirements = report.get('requirements', {})
        
        # Create base requirements structure
        terraform_requirements = {
            "cloud_provider": requirements.get('cloud_provider', 'aws'),
            "region": requirements.get('region', 'ap-south-1'),
            "application_type": requirements.get('application_type', 'web-app'),
            "environments": requirements.get('environments', ['dev']),
            "compute": self._process_compute_requirements(requirements.get('compute', {})),
            "storage": self._process_storage_requirements(requirements.get('storage', {})),
            "networking": self._process_networking_requirements(requirements.get('networking', {})),
            "security": self._process_security_requirements(requirements.get('security', {})),
            "tags": {
                "Project": project_info.get('name', 'unknown'),
                "Environment": requirements.get('environment', 'dev'),
                "ManagedBy": "terraform"
            }
        }
        
        return terraform_requirements
    
    def _process_compute_requirements(self, compute: Dict) -> Dict:
        """Process compute requirements from report"""
        return {
            "instance_type": compute.get('instance_type', 't2.micro'),
            "scaling_requirements": {
                "min_instances": compute.get('min_instances', 1),
                "max_instances": compute.get('max_instances', 1)
            }
        }
    
    def _process_storage_requirements(self, storage: Dict) -> Dict:
        """Process storage requirements from report"""
        return {
            "type": storage.get('type', 'database'),
            "size": storage.get('size', '20GB')
        }
    
    def _process_networking_requirements(self, networking: Dict) -> Dict:
        """Process networking requirements from report"""
        return {
            "public_access": networking.get('public_access', True),
            "load_balancer": networking.get('load_balancer', False),
            "cdn_enabled": networking.get('cdn_enabled', False)
        }
    
    def _process_security_requirements(self, security: Dict) -> Dict:
        """Process security requirements from report"""
        return {
            "compliance_requirements": security.get('compliance_requirements', []),
            "encryption_required": security.get('encryption_required', True)
        }
    
    def _generate_custom_resources(self, requirements: Dict) -> str:
        """Generate custom resource configurations based on requirements"""
        resources = []
        
        # Add compute resources
        if requirements['compute']:
            resources.extend(self._generate_compute_resources(requirements))
            
        # Add storage resources
        if requirements['storage']:
            resources.extend(self._generate_storage_resources(requirements))
            
        # Add networking resources
        if requirements['networking']:
            resources.extend(self._generate_networking_resources(requirements))
            
        # Add security resources
        if requirements['security']:
            resources.extend(self._generate_security_resources(requirements))
            
        return "\n".join(resources)
    
    def _generate_compute_resources(self, requirements: Dict) -> List[str]:
        """Generate compute resource configurations"""
        resources = []
        compute = requirements['compute']
        
        # Generate EC2 instance if specified
        if compute.get('type') == 'ec2':
            resources.append(f"""
resource "aws_instance" "app_server" {{
  ami           = var.ami_id
  instance_type = var.instance_type
  
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name               = aws_key_pair.generated_key.key_name
  
  tags = {{
    Name = "${{var.project_name}}-instance"
    Project = var.project_name
    Environment = var.environment
  }}
}}""")
            
        # Generate ECS cluster if specified
        elif compute.get('type') == 'ecs':
            resources.append(f"""
resource "aws_ecs_cluster" "main" {{
  name = "${{var.project_name}}-cluster"
  
  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
  
  tags = {{
    Name = "${{var.project_name}}-cluster"
    Project = var.project_name
    Environment = var.environment
  }}
}}""")
            
        return resources
    
    def _generate_storage_resources(self, requirements: Dict) -> List[str]:
        """Generate storage resource configurations"""
        resources = []
        storage = requirements['storage']
        
        # Generate RDS instance if specified
        if storage.get('type') == 'database':
            resources.append(f"""
resource "aws_db_instance" "main" {{
  identifier        = "${{var.project_name}}-db"
  engine           = "mysql"
  engine_version   = "8.0"
  instance_class   = "db.t3.micro"
  allocated_storage = 20
  
  db_name  = "${{var.project_name}}_db"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  
  tags = {{
    Name = "${{var.project_name}}-db"
    Project = var.project_name
    Environment = var.environment
  }}}}""")
            
        # Generate S3 bucket if specified
        elif storage.get('type') == 'object-storage':
            resources.append(f"""
resource "aws_s3_bucket" "main" {{
  bucket = "${{var.project_name}}-storage"
  
  tags = {{
    Name = "${{var.project_name}}-storage"
    Project = var.project_name
    Environment = var.environment
  }}
}}""")
            
        return resources
    
    def _generate_networking_resources(self, requirements: Dict) -> List[str]:
        """Generate networking resource configurations"""
        resources = []
        networking = requirements['networking']
        
        # Generate VPC if specified
        if networking.get('vpc'):
            resources.append(f"""
resource "aws_vpc" "main" {{
  cidr_block = "10.0.0.0/16"
  
  tags = {{
    Name = "${{var.project_name}}-vpc"
    Project = var.project_name
    Environment = var.environment
  }}
}}""")
            
        # Generate load balancer if specified
        if networking.get('load_balancer'):
            resources.append(f"""
resource "aws_lb" "main" {{
  name               = "${{var.project_name}}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = aws_subnet.public[*].id
  
  tags = {{
    Name = "${{var.project_name}}-lb"
    Project = var.project_name
    Environment = var.environment
  }}
}}""")
            
        return resources
    
    def _generate_security_resources(self, requirements: Dict) -> List[str]:
        """Generate security resource configurations"""
        resources = []
        security = requirements['security']
        
        # Generate security groups
        resources.append(f"""
resource "aws_security_group" "app_sg" {{
  name_prefix = "${{var.project_name}}-"
  description = "Security group for ${{var.project_name}} application"
  
  # SSH
  ingress {{
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  # HTTP
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  # HTTPS
  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  # All outbound traffic
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-sg"
  }}
}}""")
            
        return resources
    
    def generate_infrastructure(self) -> Dict:
        """Generate infrastructure configuration from report"""
        # Read report
        report = self._read_report()
        
        # Convert report to requirements
        requirements = self._convert_report_to_requirements(report)
        
        # Generate base Terraform configuration
        result = self.terraform_agent.generate(requirements)
        
        # Generate custom resources based on requirements
        custom_resources = self._generate_custom_resources(requirements)
        
        # Update main.tf with custom resources
        main_tf_content = f"""terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.region
}}

{custom_resources}
"""
        
        # Update the result with our custom main.tf
        result["terraform_files"]["main.tf"] = main_tf_content
        
        return result

def generate_infrastructure_from_report(report_path: str, output_dir: Optional[str] = None) -> Dict:
    """
    Generate infrastructure configuration from a report file
    
    Args:
        report_path: Path to the report.json file
        output_dir: Optional output directory for Terraform files
        
    Returns:
        Dict containing the generated Terraform configuration
    """
    generator = InfrastructureGenerator(report_path, output_dir)
    return generator.generate_infrastructure() 