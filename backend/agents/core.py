from langgraph.prebuilt import create_react_agent
from agents.llm_client import get_llm

# Tools -> 
from tools.web_search import web_search
from tools.wikipedia_search import wikipedia_search
from tools.pdf_reader import pdf_reader
from tools.arvix_search import arxiv_search


tools = [web_search, wikipedia_search, pdf_reader, arxiv_search]

def build_agent():
    llm = get_llm()
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="""
            You are an autonomous research assistant wih access of these tools:
            - web_search : for current news, recent events, latest information
            - search_wikipedia : for background knowledge, definations, historical information
            - pdf_reader: for reading PDFs from a URL or local file path 
            - arxiv_search : for academic papers, research studies, scientific topics
            
            RULES:
            - Always pick the most appropriate tool for the query.
            - for recent curent informartion - use web_search
            - for background/ factual/ historical/ info - use wikipedia
            - for reading PDFs from a URL or local file path - use pdf_reader
            - for research papers - use arxiv_search, then pdf_reader on relevant results.
            - Never answer research questions from memory alone.
            
        """
    )
    return agent