# import os
# import sys
# import argparse
# import json
# from pathlib import Path
# from typing import Dict

# from .terraform_planner import TerraformPlanner, TerraformPlan, EC2InstanceConfig
# from .terraform_generator import TerraformGenerator
# from ..utils.terraform_utils import load_project_report, validate_terraform_config

# def main():
#     parser = argparse.ArgumentParser(description='Generate Terraform configurations for VibeCoder projects')
#     parser.add_argument('--report', required=True, help='Path to the VibeCoder project report JSON file')
#     parser.add_argument('--output-dir', default='terraform_output', help='Directory where Terraform files will be generated')
#     parser.add_argument('--project-path', help='Path to the VibeCoder project directory')
#     args = parser.parse_args()

#     try:
#         # Load and validate project report
#         report = load_project_report(args.report)
        
#         # If project path is not provided, try to find it from the report
#         if not args.project_path and 'file_manifest' in report:
#             # Get the first file path from the manifest and extract the project directory
#             first_file = report['file_manifest'][0]['path']
#             project_path = os.path.dirname(first_file)
#             if os.path.exists(project_path):
#                 args.project_path = project_path
#                 print(f"Found project path: {project_path}")
        
#         # Create Terraform plan from the report
#         plan = TerraformPlan()
        
#         # Add EC2 instances from the report
#         for instance in report.get('instances', []):
#             ec2_config = EC2InstanceConfig(
#                 ami_id=instance.get('ami_id', 'ami-0c55b159cbfafe1f0'),  # Default Amazon Linux 2 AMI
#                 instance_type=instance.get('instance_type', 't2.micro'),
#                 tags=instance.get('tags', {'Name': 'VibeCoder-Instance'})
#             )
#             plan.add_ec2_instance(ec2_config)
        
#         # Generate Terraform configuration files
#         generator = TerraformGenerator(output_dir=args.output_dir, source_code_path=args.project_path)
#         generated_files = generator.generate_terraform_scripts(plan)
        
#         print("\nTerraform configuration generated successfully!")
#         print("\nGenerated files:")
#         for file_name, file_path in generated_files.items():
#             print(f"- {file_name}: {file_path}")
        
#         if args.project_path:
#             print(f"\nProject code will be deployed from: {args.project_path}")
#             print("The code will be uploaded to S3 and then deployed to EC2 instances")
        
#         print("\nTo apply the Terraform configuration:")
#         print(f"1. cd {args.output_dir}")
#         print("2. terraform init")
#         print("3. terraform plan")
#         print("4. terraform apply")
        
#         if args.project_path:
#             print("\nAfter applying the configuration:")
#             print("1. The source code will be uploaded to S3")
#             print("2. EC2 instances will be created")
#             print("3. The code will be automatically deployed to the instances")
#             print("4. The application will be started using PM2")
        
#     except Exception as e:
#         print(f"Error: {str(e)}", file=sys.stderr)
#         sys.exit(1)

# if __name__ == "__main__":
#     main() 

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict

from .terraform_planner import TerraformPlanner, TerraformPlan, EC2InstanceConfig
from .terraform_generator import TerraformGenerator
from ..utils.terraform_utils import load_project_report, validate_terraform_config

def main():
    parser = argparse.ArgumentParser(description='Generate Terraform configurations for VibeCoder projects')
    parser.add_argument('--report', required=True, help='Path to the VibeCoder project report JSON file')
    parser.add_argument('--project-path', required=True, help='Path to the VibeCoder project directory containing source code')
    parser.add_argument('--output-dir', default='terraform_output', help='Directory where Terraform files will be generated')
    parser.add_argument('--region', default='ap-south-1', help='AWS region to deploy to')
    parser.add_argument('--instance-type', default='t2.micro', help='EC2 instance type')
    args = parser.parse_args()

    try:
        # Validate project path exists
        if not os.path.exists(args.project_path):
            raise Exception(f"Project path does not exist: {args.project_path}")
        
        # Load and validate project report
        report = load_project_report(args.report)
        
        # Create Terraform plan from the report
        plan = TerraformPlan(ec2_instances=[])
        
        # Add EC2 instances from the report or create default
        if 'instances' in report and report['instances']:
            for instance in report['instances']:
                ec2_config = EC2InstanceConfig(
                    ami_id=instance.get('ami_id', 'ami-0af9569868786b23a'),  # Default Amazon Linux 2 AMI
                    instance_type=instance.get('instance_type', args.instance_type),
                    region=args.region,
                    tags=instance.get('tags', {'Name': f"{report.get('project_name', 'VibeCoder')}-Instance"}),
                    security_groups=instance.get('security_groups', [])
                )
                plan.ec2_instances.append(ec2_config)
        else:
            # Create default instance configuration
            ec2_config = EC2InstanceConfig(
                ami_id='ami-0af9569868786b23a',  # Amazon Linux 2 AMI
                instance_type=args.instance_type,
                region=args.region,
                tags={
                    'Name': f"{report.get('project_name', 'VibeCoder')}-Instance",
                    'Project': report.get('project_name', 'VibeCoder'),
                    'Environment': 'development'
                },
                security_groups=[]
            )
            plan.ec2_instances.append(ec2_config)
        
        # Generate Terraform configuration files
        generator = TerraformGenerator(output_dir=args.output_dir, source_code_path=args.project_path)
        generated_files = generator.generate_terraform_scripts(plan)
        
        print("=" * 60)
        print("🚀 Terraform configuration generated successfully!")
        print("=" * 60)
        
        print("\n📁 Generated files:")
        for file_name, file_path in generated_files.items():
            print(f"   ✓ {file_name}: {file_path}")
        
        print(f"\n📂 Source code will be deployed from: {args.project_path}")
        print(f"📦 Terraform files location: {args.output_dir}")
        
        # Detect project type and show relevant information
        project_type = _detect_project_type(args.project_path)
        print(f"🔍 Detected project type: {project_type.upper()}")
        
        print("\n" + "=" * 60)
        print("🛠️  DEPLOYMENT INSTRUCTIONS")
        print("=" * 60)
        
        print(f"\n1. Navigate to the Terraform directory:")
        print(f"   cd {args.output_dir}")
        
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