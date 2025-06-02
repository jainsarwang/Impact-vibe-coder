from typing import Dict, List, Optional
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EC2InstanceConfig:
    instance_type: str
    ami_id: str
    region: str
    tags: Dict[str, str]
    security_groups: List[str]
    key_name: Optional[str] = None

@dataclass
class TerraformPlan:
    ec2_instances: List[EC2InstanceConfig]
    vpc_config: Optional[Dict] = None
    subnet_config: Optional[Dict] = None

class TerraformPlanner:
    def __init__(self):
        self.default_region = "us-east-1"
        self.default_instance_type = "t2.micro"
        self.default_ami = "ami-0af9569868786b23a"

    def analyze_project_report(self, report_path: str) -> TerraformPlan:
        """
        Analyzes the project report and generates a Terraform plan
        """
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            # Extract project requirements and dependencies
            requirements = report.get('requirements', {})
            dependencies = report.get('dependencies', [])
            
            # Create EC2 instance configuration
            ec2_config = EC2InstanceConfig(
                instance_type=self.default_instance_type,
                ami_id=self.default_ami,
                region=self.default_region,
                tags={
                    "Name": f"{report.get('project_name', 'vibecoder-project')}-instance",
                    "Project": report.get('project_name', 'vibecoder-project'),
                    "Environment": "development"
                },
                security_groups=["default"]
            )
            
            return TerraformPlan(
                ec2_instances=[ec2_config]
            )
            
        except Exception as e:
            raise Exception(f"Error analyzing project report: {str(e)}")

    def _determine_instance_type(self, requirements: Dict) -> str:
        """
        Determines appropriate EC2 instance type based on project requirements
        """
        # Add logic to determine instance type based on requirements
        return self.default_instance_type

    def _determine_ami(self, requirements: Dict) -> str:
        """
        Determines appropriate AMI based on project requirements
        """
        # Add logic to determine AMI based on requirements
        return self.default_ami 