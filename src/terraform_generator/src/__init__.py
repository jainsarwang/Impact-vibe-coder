"""
Terraform Generator package
"""

from .main import main as terraform_generator_main
from .terraform_generator import TerraformGenerator

__all__ = ['terraform_generator_main', 'TerraformGenerator'] 