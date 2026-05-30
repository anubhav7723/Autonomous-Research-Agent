from ddgs import DDGS
from langchain.tools import tool

@tool
def web_search(query : str) -> str:
    ''' search web and return top results.'''
    print(f"\n[TOOL CALLED] Query: {query}\n")
    
    results = []
    
    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=5)
        
        for r in search_results:
            results.append(
                f"""
                Title: {r.get('title')}
                Snippet: {r.get('body')}
                URL: {r.get('href')}
                """
            )
         
    return "\n".join(results)