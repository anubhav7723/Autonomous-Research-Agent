from tools.web_search import web_search
from langgraph.prebuilt import create_react_agent
from agents.llm_client import get_llm

tools = [web_search]

def build_agent():
    llm = get_llm()
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="""
            You are an autonomous research assistant.
            - Always use the web_search tool for any search, lookup, or current info requests.
            - Never answer search requests from memory.
        """
    )
    return agent