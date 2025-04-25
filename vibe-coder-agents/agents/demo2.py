from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.newspaper import NewspaperTools
import os
from dotenv import load_dotenv

load_dotenv()

load_dotenv()
os.environ['GEMINI_API_KEY']  = os.getenv("GEMINI_API_KEY") 
os.environ['GROQ_API_KEY']  = os.getenv("GROQ_API_KEY") 

#creating
agent1 = Agent(
    model= Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    description = "You are an expert Business Analyst, give best business solution and you are the world leading Business Analyst",
    tools = [NewspaperTools()],
    markdown = True
) 

agent1.print_response("Today's Latest news with the Date also in proper format?")