from src.terraform_agent import TerraformAgent

def test_terraform_agent():
    # Sample project requirements
    project_requirements = {
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

    try:
        # Initialize the agent
        print("Initializing Terraform agent...")
        agent = TerraformAgent()
        
        # Generate Terraform configuration
        print("Generating Terraform configuration...")
        result = agent.generate(project_requirements)
        
        print("\nGeneration completed successfully!")
        print("\nGenerated files:")
        for filename in result["terraform_files"].keys():
            print(f"- {filename}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    test_terraform_agent() 