from setuptools import setup, find_packages

setup(
    name="terraform_agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "jinja2>=3.1.0",
        "typing-extensions>=4.5.0"
    ],
) 