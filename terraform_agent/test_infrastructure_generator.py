import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terraform_agent.src.infrastructure_generator import generate_infrastructure_from_report

def test_infrastructure_generator():
    # Path to your report.json file
    report_path = r"D:\Impact-vibe-coder\report.json"

    # Create a sample report.json if it doesn't exist
    if not os.path.exists(report_path):
        sample_report = {
            "project_info": {
                "name": "test-project",
                "description": "Test project for infrastructure generation",
                "version": "1.0.0"
            },
            "requirements": {
                "cloud_provider": "aws",
                "region": "ap-south-1",
                "application_type": "web-app",
                "environment": "dev",
                "compute": {
                    "type": "ec2",
                    "instance_type": "t2.micro",
                    "min_instances": 1,
                    "max_instances": 2
                },
                "storage": {
                    "type": "database",
                    "size": "20GB"
                },
                "networking": {
                    "public_access": True,
                    "load_balancer": True,
                    "vpc": True,
                    "cdn_enabled": False
                },
                "security": {
                    "compliance_requirements": ["SOC2"],
                    "encryption_required": True
                }
            }
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        # Write sample report
        with open(report_path, 'w') as f:
            import json
            json.dump(sample_report, f, indent=2)
    
    try:
        # Generate infrastructure configuration
        print(f"Reading report from: {report_path}")
        result = generate_infrastructure_from_report(report_path)
        
        print("\nGeneration completed successfully!")
        print("\nGenerated files:")
        for filename in result["terraform_files"].keys():
            print(f"- {filename}")
            
        # Print instructions for applying the configuration
        print("\nTo apply the configuration:")
        print("1. cd terraform_output")
        print("2. terraform init")
        print("3. terraform plan")
        print("4. terraform apply")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    test_infrastructure_generator() 