import os
import json
from typing import Dict, Any
from pathlib import Path

def load_project_report(report_path: str) -> Dict[str, Any]:
    """
    Loads and validates the project report JSON file
    """
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Project report not found at: {report_path}")
    
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
        return report
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in project report: {report_path}")

def validate_terraform_config(config: Dict[str, Any]) -> bool:
    """
    Validates the Terraform configuration
    """
    required_fields = ['ec2_instances']
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    return True

def get_aws_region_name(region_code: str) -> str:
    """
    Converts AWS region code to full name
    """
    region_map = {
        'us-east-1': 'US East (N. Virginia)',
        'us-east-2': 'US East (Ohio)',
        'us-west-1': 'US West (N. California)',
        'us-west-2': 'US West (Oregon)',
        'eu-west-1': 'EU (Ireland)',
        'eu-central-1': 'EU (Frankfurt)',
        'ap-southeast-1': 'Asia Pacific (Singapore)',
        'ap-southeast-2': 'Asia Pacific (Sydney)',
        'ap-northeast-1': 'Asia Pacific (Tokyo)'
    }
    return region_map.get(region_code, region_code)

def sanitize_resource_name(name: str) -> str:
    """
    Sanitizes a string to be used as a Terraform resource name
    """
    # Replace spaces and special characters with hyphens
    sanitized = ''.join(c if c.isalnum() else '-' for c in name.lower())
    # Remove consecutive hyphens
    sanitized = '-'.join(filter(None, sanitized.split('-')))
    return sanitized 