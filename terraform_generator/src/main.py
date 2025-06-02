import os
import sys
import argparse
from pathlib import Path
from typing import Dict

from .terraform_planner import TerraformPlanner
from .terraform_generator import TerraformGenerator
from ..utils.terraform_utils import load_project_report, validate_terraform_config

def main():
    parser = argparse.ArgumentParser(description='Generate Terraform configuration from VibeCoder project report')
    parser.add_argument('--report', required=True, help='Path to the project report JSON file')
    parser.add_argument('--output-dir', default='terraform_output', help='Directory to output Terraform files')
    args = parser.parse_args()

    try:
        # Load and validate project report
        report = load_project_report(args.report)
        
        # Create Terraform planner and generate plan
        planner = TerraformPlanner()
        plan = planner.analyze_project_report(args.report)
        
        # Generate Terraform configuration files
        generator = TerraformGenerator(output_dir=args.output_dir)
        generated_files = generator.generate_terraform_scripts(plan)
        
        print("\nTerraform configuration generated successfully!")
        print("\nGenerated files:")
        for file_name, file_path in generated_files.items():
            print(f"- {file_name}: {file_path}")
        
        print("\nTo apply the Terraform configuration:")
        print(f"1. cd {args.output_dir}")
        print("2. terraform init")
        print("3. terraform plan")
        print("4. terraform apply")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 