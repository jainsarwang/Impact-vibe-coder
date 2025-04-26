from agno.agent import Agent, RunResponse

from agno.models.groq import Groq
from agno.models.google import Gemini

from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools

import os
from dotenv import load_dotenv
import json
from prompts import business_goal, busienss_instruction, business_description, business_expected_outcome, user_prompt
load_dotenv()
os.environ['GEMINI_API_KEY']  = os.getenv("GEMINI_API_KEY") 
os.environ['GROQ_API_KEY']  = os.getenv("GROQ_API_KEY") 

#business Analyst
business_agent = Agent(
    name="Business Analyst Maestro",    
    # model=Groq(id="deepseek-r1-distill-llama-70b"),
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY")),
    add_context=True,
    description=business_description,
    tools=[
        GoogleSearchTools(fixed_max_results=3, fixed_language="en"),
        ],
    goal=business_goal,
    instructions=[busienss_instruction],
    expected_output=json.dumps(business_expected_outcome),
)

business_agent.print_response(message=json.dumps(user_prompt), stream=True)

