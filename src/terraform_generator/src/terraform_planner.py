from typing import Dict, List, Optional
import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class EC2InstanceConfig:
    """Configuration for an EC2 instance"""
    ami_id: str
    instance_type: str
    region: str
    tags: Dict[str, str]
    security_groups: List[str] = field(default_factory=list)
    key_name: Optional[str] = None

@dataclass
class TerraformPlan:
    """Represents a complete Terraform deployment plan"""
    ec2_instances: List[EC2InstanceConfig] = field(default_factory=list)
    vpc_config: Optional[Dict] = None
    subnet_config: Optional[Dict] = None
    
    def add_ec2_instance(self, config: EC2InstanceConfig):
        """Add an EC2 instance configuration to the plan"""
        self.ec2_instances.append(config)

class TerraformPlanner:
    """Plans and generates Terraform configurations based on project requirements"""
    
    def __init__(self):
        self.default_region = "ap-south-1"
        self.default_instance_type = "t2.micro"
        self.default_ami = "ami-0af9569868786b23a"  # Amazon Linux 2

    def analyze_project_report(self, report_path: str) -> TerraformPlan:
        """
        Analyzes the project report and generates a Terraform plan
        
        Args:
            report_path: Path to the project report JSON file
            
        Returns:
            TerraformPlan object containing the deployment configuration
        """
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            # Extract project requirements and dependencies
            requirements = report.get('requirements', {})
            dependencies = report.get('dependencies', [])
            
            # Create EC2 instance configuration
            ec2_config = EC2InstanceConfig(
                instance_type=self._determine_instance_type(requirements),
                ami_id=self._determine_ami(requirements),
                region=self.default_region,
                tags={
                    "Name": f"{report.get('project_name', 'vibecoder-project')}-instance",
                    "Project": report.get('project_name', 'vibecoder-project'),
                    "Environment": "development"
                },
                security_groups=[]
            )
            
            plan = TerraformPlan()
            plan.add_ec2_instance(ec2_config)
            
            return plan
            
        except Exception as e:
            raise Exception(f"Error analyzing project report: {str(e)}")

    def create_plan_from_config(self, project_name: str, instance_configs: List[Dict] = None) -> TerraformPlan:
        """
        Creates a Terraform plan from basic configuration
        
        Args:
            project_name: Name of the project
            instance_configs: List of instance configurations (optional)
            
        Returns:
            TerraformPlan object containing the deployment configuration
        """
        plan = TerraformPlan()
        
        if not instance_configs:
            # Create default configuration
            instance_configs = [{
                'instance_type': self.default_instance_type,
                'ami_id': self.default_ami,
                'tags': {
                    'Name': f"{project_name}-instance",
                    'Project': project_name,
                    'Environment': 'development'
                }
            }]
        
        for config in instance_configs:
            ec2_config = EC2InstanceConfig(
                instance_type=config.get('instance_type', self.default_instance_type),
                ami_id=config.get('ami_id', self.default_ami),
                region=config.get('region', self.default_region),
                tags=config.get('tags', {'Name': f"{project_name}-instance"}),
                security_groups=config.get('security_groups', []),
                key_name=config.get('key_name')
            )
            plan.add_ec2_instance(ec2_config)
        
        return plan

    def _determine_instance_type(self, requirements: Dict) -> str:
        """
        Determines appropriate EC2 instance type based on project requirements
        
        Args:
            requirements: Dictionary containing project requirements
            
        Returns:
            Recommended EC2 instance type
        """
        # Basic logic to determine instance type based on requirements
        if requirements.get('memory_intensive', False):
            return 't3.medium'
        elif requirements.get('cpu_intensive', False):
            return 't3.small'
        else:
            return self.default_instance_type

    def _determine_ami(self, requirements: Dict) -> str:
        """
        Determines appropriate AMI based on project requirements
        
        Args:
            requirements: Dictionary containing project requirements
            
        Returns:
            Recommended AMI ID
        """
        # # Basic logic to determine AMI based on requirements
        # os_type = requirements.get('os', 'linux')
        
        # if os_type.lower() == 'ubuntu':
        #     return 'ami-0c7217cdde317cfec'  # Ubuntu 22.04 LTS
        # elif os_type.lower() == 'centos':
        #     return 'ami-0c9978668f8d55984'  # CentOS 7
        # else:
        #     return self.default_ami  # Amazon Linux 2

    # def get_supported_regions(self) -> List[str]:
    #     """Returns list of supported AWS regions"""
    #     return [
    #         'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
    #         'eu-west-1', 'eu-west-2', 'eu-central-1',
    #         'ap-south-1', 'ap-southeast-1', 'ap-southeast-2'
    #     ]

    def get_recommended_instance_types(self, project_type: str = 'web') -> List[str]:
        """
        Returns recommended instance types based on project type
        
        Args:
            project_type: Type of project (web, api, ml, database, static)
            
        Returns:
            List of recommended EC2 instance types
        """
        recommendations = {
            'web': ['t2.micro', 't3.micro', 't3.small'],
            'api': ['t3.small', 't3.medium', 't3.large'],
            'ml': ['t3.medium', 't3.large', 'm5.large'],
            'database': ['t3.medium', 't3.large', 'r5.large'],
            'static': ['t2.nano', 't2.micro', 't3.micro']
        }
        
        return recommendations.get(project_type, recommendations['web'])