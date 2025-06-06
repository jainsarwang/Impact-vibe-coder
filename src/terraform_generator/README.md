# Terraform Generator for VibeCoder

A powerful tool that automatically generates Terraform configurations for deploying VibeCoder projects to AWS infrastructure.

## Features

- 🚀 Automatic Terraform configuration generation
- 🔧 Support for multiple project types (Node.js, Python, PHP, Java, Go, Static)
- 🖥️ EC2 instance provisioning with optimized configurations
- 🔒 Security group management
- 📦 Direct source code deployment to EC2
- 🔄 Support for multiple AWS regions
- 🏷️ Customizable instance tags and naming
- 📝 Detailed deployment instructions

## Project Structure

```
terraform_generator/
├── src/
│   ├── main.py              # Main entry point
│   ├── terraform_planner.py # Infrastructure planning logic
│   ├── terraform_generator.py # Terraform file generation
│   └── utils/
│       └── terraform_utils.py # Utility functions
└── README.md
```

## Prerequisites

- Python 3.7+
- AWS CLI configured with appropriate credentials
- Terraform installed (version >= 1.0)
- OpenSSH client (for Windows users)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/terraform-generator.git
cd terraform-generator
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
# Windows PowerShell
mkdir terraform_output\.aws
@"
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = ap-south-1
"@ | Out-File -FilePath "terraform_output\.aws\credentials" -Encoding utf8

# Linux/Mac
mkdir -p terraform_output/.aws
cat > terraform_output/.aws/credentials << EOL
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = ap-south-1
EOL
```

## Deployment Commands

### Windows Deployment

1. **Setup Environment**
```cmd
:: Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

:: Install dependencies
pip install -r requirements.txt

:: Create AWS credentials directory
mkdir terraform_output\.aws

:: Set AWS credentials
echo [default] > terraform_output\.aws\credentials
echo aws_access_key_id = YOUR_ACCESS_KEY >> terraform_output\.aws\credentials
echo aws_secret_access_key = YOUR_SECRET_KEY >> terraform_output\.aws\credentials
echo region = ap-south-1 >> terraform_output\.aws\credentials
```

2. **Generate Terraform Configuration**
```cmd
:: Generate configuration
python -m terraform_generator --report D:\path\to\report.json --project-path D:\path\to\project

:: Navigate to output directory
cd terraform_output
```

3. **Initialize and Apply Terraform**
```cmd
:: Initialize Terraform
terraform init

:: Plan deployment
terraform plan

:: Apply configuration
terraform apply
```

4. **Deploy Application**
```cmd
:: Get instance IP (CMD)
for /f "tokens=*" %i in ('terraform output -raw instance_1_public_ip') do set INSTANCE_IP=%i

:: Set key path
set KEY_PATH=vibecoder-key.pem

:: Set proper permissions for the key file (Windows CMD)
icacls %KEY_PATH% /inheritance:r
icacls %KEY_PATH% /grant:r "%USERNAME%":"(R,W)"
icacls %KEY_PATH% /remove "NT AUTHORITY\Authenticated Users"

:: Wait for instance to be ready (30 seconds)
timeout /t 30

:: Deploy source code
ssh -i %KEY_PATH% -o StrictHostKeyChecking=no ec2-user@%INSTANCE_IP% "mkdir -p /home/ec2-user/app"
scp -i %KEY_PATH% -o StrictHostKeyChecking=no source_code.zip ec2-user@%INSTANCE_IP%:/home/ec2-user/app/
ssh -i %KEY_PATH% -o StrictHostKeyChecking=no ec2-user@%INSTANCE_IP% "cd /home/ec2-user/app && unzip -o source_code.zip"

:: Verify deployment
echo http://%INSTANCE_IP%
ssh -i %KEY_PATH% ec2-user@%INSTANCE_IP%
```

### Linux/Mac Deployment

1. **Setup Environment**
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create AWS credentials directory
mkdir -p terraform_output/.aws

# Set AWS credentials
cat > terraform_output/.aws/credentials << EOL
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = ap-south-1
EOL
```

2. **Generate Terraform Configuration**
```bash
# Generate configuration
python -m terraform_generator --report /path/to/report.json --project-path /path/to/project

# Navigate to output directory
cd terraform_output
```

3. **Initialize and Apply Terraform**
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

4. **Deploy Application**
```bash
# Get instance IP
INSTANCE_IP=$(terraform output -raw instance_1_public_ip)

# Set key path
KEY_PATH="vibecoder-key.pem"

# Set correct permissions for key
chmod 600 $KEY_PATH

# Wait for instance to be ready
timeout /t 30

# Deploy source code
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$INSTANCE_IP "mkdir -p /home/ec2-user/app"
scp -i $KEY_PATH -o StrictHostKeyChecking=no source_code.zip ec2-user@$INSTANCE_IP:/home/ec2-user/app/

# SSH and setup application
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$INSTANCE_IP << 'EOF'
    cd /home/ec2-user/app
    unzip -o source_code.zip
    # Application setup will be handled automatically based on project type
EOF

# Verify deployment
echo http://%INSTANCE_IP%
ssh -i %KEY_PATH% ec2-user@%INSTANCE_IP%
```

### Verification Commands

1. **Check Instance Status**
```bash
# Windows
terraform output

# Linux/Mac
terraform output
```

2. **Access Application**
```bash
# Get application URL
echo "http://$(terraform output -raw instance_1_public_ip)"

# SSH into instance
ssh -i vibecoder-key.pem ec2-user@$(terraform output -raw instance_1_public_ip)
```

3. **Check Application Logs**
```bash
# SSH into instance
ssh -i vibecoder-key.pem ec2-user@$(terraform output -raw instance_1_public_ip)

# Check user data script logs
cat /var/log/user-data.log

# Check application logs based on project type
# Node.js
pm2 logs

# Python
cat app.log

# Apache
tail -f /var/log/httpd/error_log
```

### Cleanup Commands

```bash
# Destroy infrastructure
terraform destroy

# Clean up local files
rm -rf .terraform
rm -f terraform.tfstate*
rm -f vibecoder-key.pem
```

## Project Types and Configuration

### Node.js Projects
- Detected by `package.json`
- Uses PM2 for process management
- Default port: 3000
- Environment variables in `.env` file

### Python Projects
- Detected by `requirements.txt` or `setup.py`
- Uses Gunicorn for production
- Default port: 8000
- Virtual environment created automatically

### PHP Projects
- Detected by `composer.json`
- Apache web server configuration
- Default port: 80
- Composer dependencies installed

### Static Projects
- Served via Apache
- Default port: 80
- Optimized for static file serving

## Security Best Practices

1. **AWS Credentials**
   - Never commit credentials to version control
   - Use IAM roles when possible
   - Rotate credentials regularly

2. **Security Groups**
   - Only open necessary ports
   - Use specific IP ranges for SSH
   - Enable HTTPS

3. **Application Security**
   - Use environment variables for secrets
   - Enable HTTPS
   - Regular security updates

## Maintenance

### Updating Infrastructure
```bash
# Make changes to Terraform files
terraform plan
terraform apply
```

### Scaling
- Modify instance type in `terraform.tfvars`
- Update security groups as needed
- Adjust application configuration

### Cleanup
```bash
# Destroy all resources
terraform destroy
```

## Support

For issues and support:
1. Check the troubleshooting guide
2. Review application logs
3. Open a GitHub issue
4. Contact maintainers

## License

This project is licensed under the MIT License - see the LICENSE file for details. 