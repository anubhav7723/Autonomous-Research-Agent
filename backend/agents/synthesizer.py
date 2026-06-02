from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_client import get_llm

llm = get_llm()

SYNTHESIZER_PROMPT = """
You are a research synthesizer. You are given a user query and results 
collected from multiple research tools.

Your job is to:
- Combine all results into a single, coherent, well-structured report
- Include key findings, important details, and sources where available
- Be comprehensive but concise
- Use clear headings and bullet points
"""

def synthesize(query: str, tool_results: list) -> str:
    print(f"\n[SYNTHESIZER] Combining {len(tool_results)} results...\n")
    
    # Format all results into one block
    combined = ""
    for i, result in enumerate(tool_results):
        combined += f"\n--- Result {i+1} (from {result['tool']}) ---\n"
        combined += result["output"]
    
    response = llm.invoke([
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(content=f"""
            User Query: {query}
            
            Research Results:
            {combined}
            
            Now write a comprehensive research report answering the query.
        """)
    ])
    
    return response.content