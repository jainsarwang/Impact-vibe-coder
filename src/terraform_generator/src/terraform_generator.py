from typing import Dict, List
import os
import json
import shutil
import base64
import zipfile
from pathlib import Path
from .terraform_planner import TerraformPlan, EC2InstanceConfig

class TerraformGenerator:
    def __init__(self, output_dir: str = "terraform_output", source_code_path: str = None):
        self.output_dir = output_dir
        self.source_code_path = source_code_path
        self.source_code_zip_path = None
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Creates the output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_terraform_scripts(self, plan: TerraformPlan) -> Dict[str, str]:
        """
        Generates Terraform configuration files based on the provided plan
        Returns a dictionary of generated file paths
        """
        generated_files = {}
        print("generate terraform scripts called")
        
        # Create source code zip FIRST (before generating main.tf)
        if self.source_code_path and os.path.exists(self.source_code_path):
            zip_path = self._create_source_zip()
            self.source_code_zip_path = zip_path
            generated_files['source_code.zip'] = zip_path

        # Generate user data script directly (not as template)
        user_data_script = self._generate_user_data_script()
        user_data_script_path = os.path.join(self.output_dir, "user_data.sh")
        with open(user_data_script_path, 'w') as f:
            f.write(user_data_script)
        os.chmod(user_data_script_path, 0o755)  # Make executable
        generated_files['user_data.sh'] = user_data_script_path

        # Generate main.tf (now that script exists)
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

        # Generate terraform.tfvars
        tfvars = self._generate_tfvars()
        tfvars_path = os.path.join(self.output_dir, "terraform.tfvars")
        with open(tfvars_path, 'w') as f:
            f.write(tfvars)
        generated_files['terraform.tfvars'] = tfvars_path

        # Generate deployment script
        deploy_script = self._generate_deploy_script()
        deploy_script_path = os.path.join(self.output_dir, "deploy.sh")
        with open(deploy_script_path, 'w') as f:
            f.write(deploy_script)
        os.chmod(deploy_script_path, 0o755)  # Make executable
        generated_files['deploy.sh'] = deploy_script_path

        return generated_files

    def _create_source_zip(self) -> str:
        """Creates a zip file of the source code"""
        print("Creating source code zip...")
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        zip_path = os.path.join(self.output_dir, "source_code.zip")
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.source_code_path):
                    # Skip unnecessary directories
                    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.terraform']]
                    
                    for file in files:
                        # Skip unnecessary files
                        if file.startswith('.') and file not in ['.env.example', '.gitignore']:
                            continue
                        if file.endswith(('.pyc', '.pyo', '.log')):
                            continue
                            
                        file_path = os.path.join(root, file)
                        try:
                            arcname = os.path.relpath(file_path, self.source_code_path)
                            zipf.write(file_path, arcname)
                        except Exception as e:
                            print(f"Warning: Could not add {file_path} to zip: {str(e)}")
                            continue
            
            return zip_path
        except Exception as e:
            raise Exception(f"Error creating source code zip: {str(e)}")

    def _detect_project_type(self):
        """Detects the type of project based on files in the source code path"""
        if not self.source_code_path or not os.path.exists(self.source_code_path):
            return "unknown"
        
        files = os.listdir(self.source_code_path)
        
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

    def _generate_user_data_script(self) -> str:
        """Generates a minimal user data script that sets up the environment"""
        return """#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

# Update system and install basic dependencies
yum update -y
yum install -y python3 python3-pip wget curl unzip git

# Create app directory
mkdir -p /home/ec2-user/app
cd /home/ec2-user/app

# Set up basic environment
echo "export PATH=$PATH:/usr/local/bin" >> /home/ec2-user/.bashrc
echo "export PYTHONPATH=/home/ec2-user/app" >> /home/ec2-user/.bashrc

# Fix permissions
chown -R ec2-user:ec2-user /home/ec2-user/app

echo "Initial setup completed successfully"
"""

    def _generate_main_tf(self, plan: TerraformPlan) -> str:
        """Generates the main Terraform configuration file"""
        
        main_tf = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
  access_key = "AKIA4SDNVNFYSRLW4G7G"
  secret_key = "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"
}

# Generate SSH key pair
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "vibecoder-key"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

# Save private key to file
resource "local_file" "private_key" {
  content  = tls_private_key.ssh_key.private_key_pem
  filename = "${path.module}/vibecoder-key.pem"
  file_permission = "777"
}

# Security group for EC2 instances
resource "aws_security_group" "app_sg" {
  name_prefix = "vibecoder-app-"
  description = "Security group for VibeCoder application"

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Custom application ports
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "vibecoder-app-sg"
  }
}

"""
        
        # Add EC2 instance configurations
        for i, instance in enumerate(plan.ec2_instances):
            main_tf += f"""
# EC2 Instance {i + 1}
resource "aws_instance" "app_server_{i}" {{
  ami           = "{instance.ami_id}"
  instance_type = "{instance.instance_type}"
  
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name               = aws_key_pair.generated_key.key_name
  
  user_data = base64encode(file("${{path.module}}/user_data.sh"))
  
  tags = {{
"""
            for key, value in instance.tags.items():
                main_tf += f'    {key} = "{value}"\n'
            main_tf += """  }
  
  timeouts {
    create = "10m"
  }
}

"""

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

variable "key_name" {
  description = "AWS Key Pair name for SSH access"
  type        = string
  default     = ""
}
"""

    def _generate_outputs_tf(self, plan: TerraformPlan) -> str:
        """Generates the outputs Terraform configuration file"""
        outputs = ""
        
        for i, instance in enumerate(plan.ec2_instances):
            outputs += f"""
output "instance_{i + 1}_public_ip" {{
  description = "Public IP address of EC2 instance {i + 1}"
  value       = aws_instance.app_server_{i}.public_ip
}}

output "instance_{i + 1}_public_dns" {{
  description = "Public DNS name of EC2 instance {i + 1}"
  value       = aws_instance.app_server_{i}.public_dns
}}

output "instance_{i + 1}_ssh_command" {{
  description = "SSH command to connect to EC2 instance {i + 1}"
  value       = "ssh -i vibecoder-key.pem ec2-user@${{aws_instance.app_server_{i}.public_ip}}"
}}
"""

        outputs += """
output "application_urls" {
  description = "URLs to access the deployed application"
  value = [
"""
        for i, instance in enumerate(plan.ec2_instances):
            outputs += f'    "http://${{aws_instance.app_server_{i}.public_ip}}",\n'
        
        outputs += """  ]
}

output "private_key_path" {
  description = "Path to the generated private key file"
  value       = local_file.private_key.filename
}
"""
        return outputs

    def _generate_tfvars(self) -> str:
        """Generates the terraform.tfvars file"""
        return """# AWS Configuration
aws_region = "ap-south-1"
instance_type = "t2.micro"

# Uncomment and set your key pair name for SSH access
# key_name = "your-key-pair-name"
"""
    def _generate_deploy_script(self) -> str:
        """Generates a deployment script that handles SSH deployment"""
        return """#!/bin/bash

echo "Starting Terraform deployment..."

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
read -p "Do you want to apply this plan? (y/N): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo "Applying Terraform configuration..."
    terraform apply tfplan
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "Deployment completed successfully!"
        echo ""
        
        # Get instance details
        INSTANCE_IP=$(terraform output -raw instance_1_public_ip)
        KEY_PATH="vibecoder-key.pem"
        
        echo "Waiting for instance to be ready..."
        sleep 30  # Give instance time to initialize
        
        echo "Deploying source code..."
        # Create app directory on EC2
        ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$INSTANCE_IP "mkdir -p /home/ec2-user/app"
        
        # Copy source code zip to EC2
        scp -i $KEY_PATH -o StrictHostKeyChecking=no source_code.zip ec2-user@$INSTANCE_IP:/home/ec2-user/app/
        
        # SSH into instance and set up the project
        ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$INSTANCE_IP << 'EOF'
            cd /home/ec2-user/app
            
            # Unzip the source code
            echo "Unzipping source code..."
            unzip -o source_code.zip
            
            # Detect project type and set up accordingly
            if [ -f "package.json" ]; then
                echo "Setting up Node.js project..."
                npm install
                npm install -g pm2
                pm2 start npm --name "app" -- start
            elif [ -f "requirements.txt" ]; then
                echo "Setting up Python project..."
                python3 -m pip install -r requirements.txt
                # Start the application (adjust command based on your app)
                nohup python3 app.py > app.log 2>&1 &
            elif [ -f "composer.json" ]; then
                echo "Setting up PHP project..."
                composer install
                # Configure Apache if needed
                sudo cp -r * /var/www/html/
            else
                echo "Static project detected..."
                # For static sites, just ensure files are in the right place
                sudo cp -r * /var/www/html/
            fi
            
            # Clean up
            rm source_code.zip
            
            echo "Project setup completed!"
EOF
        
        echo ""
        echo "Application URLs:"
        terraform output application_urls
        echo ""
        echo "SSH Access:"
        echo "ssh -i $KEY_PATH ec2-user@$INSTANCE_IP"
        echo ""
        echo "Note: It may take 2-5 minutes for the application to be fully available"
    else
        echo "Deployment failed!"
        exit 1
    fi
else
    echo "Deployment cancelled."
    rm -f tfplan
fi
"""
