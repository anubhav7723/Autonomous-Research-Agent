from langchain.tools import tool
from langchain.agents import create_agent

from agents.llm_client import get_llm
from tools.web_search import get_tools

tools = get_tools()

def build_agent():
    llm = get_llm()
    agent = create_agent(
        model= llm,
        tools=tools,
        system_prompt="""
            You are an autonomous research assistant.

            IMPORTANT:
            - Whenever the user asks to search, look up, find information, browse, or get current information, you MUST use the web_search tool.
            - Do not answer search requests from your own knowledge.
            - Use tools whenever external information may be helpful.
            """
    )
    
    return agent