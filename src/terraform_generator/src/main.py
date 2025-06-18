
import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict

from .terraform_planner import TerraformPlanner, TerraformPlan, EC2InstanceConfig
from .terraform_generator import TerraformGenerator
from ..utils.terraform_utils import load_project_report, validate_terraform_config

def main(project_path: str = None, report: dict = None, output_dir: str = 'terraform_output', region: str = 'ap-south-1', instance_type: str = 't2.micro'):

    try:
        # Validate project path exists
        if not os.path.exists(project_path):
            raise Exception(f"Project path does not exist: {project_path}")
        
        # Load and validate project report
        # report = load_project_report(report)
        
        # Create Terraform plan from the report
        plan = TerraformPlan(ec2_instances=[])
        
        # Add EC2 instances from the report or create default
        if 'instances' in report and report['instances']:
            for instance in report['instances']:
                ec2_config = EC2InstanceConfig(
                    ami_id=instance.get('ami_id', 'ami-0af9569868786b23a'),  # Default Amazon Linux 2 AMI
                    instance_type=instance.get('instance_type', instance_type),
                    region=region,
                    tags=instance.get('tags', {'Name': f"{report.get('project_name', 'VibeCoder')}-Instance"}),
                    security_groups=instance.get('security_groups', [])
                )
                plan.ec2_instances.append(ec2_config)
        else:
            # Create default instance configuration
            ec2_config = EC2InstanceConfig(
                ami_id='ami-0af9569868786b23a',  # Amazon Linux 2 AMI
                instance_type=instance_type,
                region=region,
                tags={
                    'Name': f"{report.get('project_name', 'VibeCoder')}-Instance",
                    'Project': report.get('project_name', 'VibeCoder'),
                    'Environment': 'development'
                },
                security_groups=[]
            )
            plan.ec2_instances.append(ec2_config)
        
        # Generate Terraform configuration files
        generator = TerraformGenerator(output_dir=output_dir, source_code_path=project_path)
        generated_files = generator.generate_terraform_scripts(plan)
        
        print("=" * 60)
        print("🚀 Terraform configuration generated successfully!")
        print("=" * 60)
        
        print("\n📁 Generated files:")
        for file_name, file_path in generated_files.items():
            print(f"   ✓ {file_name}: {file_path}")
        
        print(f"\n📂 Source code will be deployed from: {project_path}")
        print(f"📦 Terraform files location: {output_dir}")
        
        # Detect project type and show relevant information
        project_type = _detect_project_type(project_path)
        print(f"🔍 Detected project type: {project_type.upper()}")
        
        print("\n" + "=" * 60)
        print("🛠️  DEPLOYMENT INSTRUCTIONS")
        print("=" * 60)
        
        print(f"\n1. Navigate to the Terraform directory:")
        print(f"   cd {output_dir}")
        
        print(f"\n2. Configure AWS credentials (if not already done):")
        print(f"   aws configure")
        print(f"   # OR export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        
        print(f"\n3. Run the deployment script:")
        print(f"   ./deploy.sh")
        
        print(f"\n   OR manually execute:")
        print(f"   terraform init")
        print(f"   terraform plan")
        print(f"   terraform apply")
        
        print(f"\n4. After deployment completes:")
        print(f"   • Your application will be automatically deployed")
        print(f"   • Check the output for application URLs")
        print(f"   • It may take 2-5 minutes for the application to be fully available")
        
        # Show project-specific deployment info
        if project_type == "nodejs":
            print(f"\n📋 Node.js Deployment Details:")
            print(f"   • Dependencies will be installed automatically")
            print(f"   • Application will run using PM2 process manager")
            print(f"   • Default port: 3000 (configurable in your app)")
            
        elif project_type == "python":
            print(f"\n📋 Python Deployment Details:")
            print(f"   • Dependencies from requirements.txt will be installed")
            print(f"   • Application will run using Gunicorn")
            print(f"   • Default port: 8000 (configurable)")
            
        elif project_type == "php":
            print(f"\n📋 PHP Deployment Details:")
            print(f"   • Apache web server will be configured")
            print(f"   • Files will be served from /var/www/html")
            print(f"   • Default port: 80")
            
        else:
            print(f"\n📋 Static Site Deployment Details:")
            print(f"   • Files will be served using Apache")
            print(f"   • Default port: 80")
        
        print(f"\n5. To destroy the infrastructure later:")
        print(f"   terraform destroy")
        
        print("\n" + "=" * 60)
        print("✅ Ready for deployment!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def _detect_project_type(project_path):
    """Detects the type of project based on files in the project path"""
    if not os.path.exists(project_path):
        return "unknown"
    
    files = os.listdir(project_path)
    
    if 'package.json' in files:
        return "nodejs"
    elif 'requirements.txt' in files or 'setup.py' in files:
        return "python"
    elif 'composer.json' in files:
        return "php"
    elif 'pom.xml' in files:
        return "java"
    elif 'go.mod' in files:
        return "go"
    else:
        return "static"

if __name__ == "__main__":
    main()