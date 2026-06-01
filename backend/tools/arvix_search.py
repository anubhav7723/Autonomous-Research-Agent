import arxiv
from langchain.tools import tool

@tool
def arxiv_search(query: str)->str:
    '''Search arXiv for academic/research papers on a topic.
    Use this when the user asks about research papers, scientific studies,
    academic work, or wants to find papers on a specific topic.'''
    
    print(f"\n[ARXIV CALLED] Query: {query}\n")
    
    try:
        client = arxiv.Client()
        
        search = arxiv.Search(
            query= query,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        
        for paper in client.results(search):
            results.append(
                f"""
                Title: {paper.title}
                Authors: {', '.join(a.name for a in paper.authors[:3])}
                Published: {paper.published.strftime('%Y-%m-%d')}
                Summary: {paper.summary[:300]}...
                PDF URL: {paper.pdf_url}
                """
            )
            
        if not results:
            return f"No paper found on {query}"
        
        return "\n---\n".join(results)
    
    except Exception as e:
        return f"arXiv search error: {str(e)}"