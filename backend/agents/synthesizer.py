from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_client import get_llm

llm = get_llm()

SYNTHESIZER_PROMPT = """
You are a research synthesizer. You are given:
- A conversation history (for context on follow-up questions)
- A user query
- Results collected from multiple research tools

Your job is to:
- Write a clear, concise answer — not a full academic paper unless asked
- For simple queries: 2-3 paragraphs maximum
- For complex queries like "summarize research" or "write a report": use full structure with headings
- If this is a follow-up question, reference previous context naturally
- Always cite sources at the end
"""

def synthesize(query: str, tool_results: list, conversation_history: list = []) -> str:
    print(f"\n[SYNTHESIZER] Combining {len(tool_results)} results...\n")
    
    # Format all results into one block
    combined = ""
    for i, result in enumerate(tool_results):
        combined += f"\n--- Result {i+1} (from {result['tool']}) ---\n"
        combined += result["output"]
    
    history_text = ""
    if conversation_history:
        history_text = "\n Conversation History: \n"
        for msg in conversation_history[-6:]: #last 3 turns only
            role =  "User" if msg['role'] == 'user' else 'Assistant'
            # trim long response
            content = msg["content"][:300] + "..." if len(msg["content"]) > 300 else msg["content"]
            history_text += f"{role} : {content}\n"
            
    response = llm.invoke([
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(content=f"""
            {history_text}
            
            Current Query: {query}
            
            Research Results:
            {combined}
            
            Now write a comprehensive research report answering the query.
        """)
    ])
    
    return response.content