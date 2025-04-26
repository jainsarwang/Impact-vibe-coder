from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.github import GithubTools

import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GEMINI_API_KEY']  = os.getenv("GEMINI_API_KEY") 
os.environ['GROQ_API_KEY']  = os.getenv("GROQ_API_KEY") 

#creatingx``
solution_architect_agent = Agent(
    name="Solution Architect Maestro",
    model=Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct"),
    add_context=True,
    description="You are a Solution Architecture Expert who creates visual architectural flows and diagrams. You focus exclusively on high-level architecture design and relationships between components without implementation details or code.",
    tools=[
        GoogleSearchTools(fixed_max_results=2, fixed_language="en"), 
        GithubTools(base_url="https://github.com/unlight/solution-architecture")
    ],
    show_tool_calls=True,
    markdown=True,
    goal="Provide comprehensive architectural flow diagrams that illustrate system components, relationships, and user journeys without implementation code.",
    instructions="""
    As Solution Architect Maistro, analyze each query carefully and deliver exceptional architectural flow diagrams following these guidelines:
    
    1. First, understand the full context and requirements behind the query
    2. Use Google Search and GitHub to research relevant architectural patterns and best practices
    3. Focus EXCLUSIVELY on creating architectural flows showing:
       - Component relationships
       - User journeys
       - Data flows
       - System boundaries
       - Key interactions between elements
    4. DO NOT provide any implementation code, pseudocode, or technical implementation details
    5. Use clear, professional formatting with flow diagrams using ASCII/text art
    6. Present architecture in both JSON structure and visual flow diagram format
    7. Always focus on relationships and flows rather than implementation specifics
    8. Structure your response exactly like the expected output format
    9. If the query mentions specific technologies, incorporate them in the architectural components, but don't provide implementation details
    10. Your ONLY deliverable should be architectural flow diagrams - absolutely no code
    """,
    expected_output='''
    {
  "project_name": "ProjectName",
  "project_description": "Brief description of the project's purpose and functionality.",
  "architectural_flow": {
    "user_journey": [
      "Step 1 → Step 2 → Step 3",
      "Alternative Path → Step X → Step Y"
    ],
    "key_relationships": {
      "Component A → Component B": "Description of relationship",
      "Component C ↔ Component D": "Bidirectional relationship description"
    },
    "detailed_flow": {
      "1. Process Name": [
        "Starting Point → Decision Point? [Yes] → Outcome 1",
        "Starting Point → Decision Point? [No] → Outcome 2"
      ],
      "2. Another Process": [
        "Process steps in sequence"
      ]
    }
  }
}
Architectural Flow Diagram:
Component A → Component B  
    ↓           ↓  
Component C ← Component D  
    ↓           ↑  
Component E → Component F
    '''
)

solution_architect_agent.print_response(
  """
{
    "ProjectMetadata": {
        "Title": "Scientific Calculator",
        "Description": "Advanced mathematical calculator for scientific and engineering applications"
    },
    "TechnicalSpecification": {
        "Architecture": "Microservices with React frontend and Node.js backend",
        "CoreComponents": [
            "Trigonometric functions",
            "Exponential and logarithmic functions",
            "Hyperbolic functions",
            "Statistical functions",
            "Matrix operations",
            "Complex number support",
            "Calculus-related functions",
            "Unit conversions"
        ]
    },
    "FunctionalRequirements": {
        "UserStories": [
            {
                "Persona": "Student",
                "Flow": "Select function â†’ Enter input values â†’ Calculate â†’ Display result"
            }
        ],
        "SystemFlows": [
            {
                "Touchpoint": "Trigonometric function",
                "Description": "Calculate sin(x) using Taylor series expansion"
            }
        ]
    },
    "NonFunctionalRequirements": {
        "Performance": "Calculate results within 1 second",
        "Security": "None"
    },
    "DevelopmentSpecification": {
        "TechnologyStack": {
            "Frontend": "React",
            "Backend": "Node.js",
            "Database": "Local storage"
        },
        "ThirdPartyServices": []
    },
    "ProjectStory": {
        "Narrative": "As a student, I use the scientific calculator to calculate the derivative of a function. I select the derivative function, enter the input values, and the calculator displays the result. I can also access a history of my previous calculations and recall them for future reference."
    }
}
  """, stream=True, show_full_reasoning=True, stream_intermediate_steps=True)