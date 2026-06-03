from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_client import get_llm

llm = get_llm()

SYNTHESIZER_PROMPT = """
You are a research synthesizer. You are given:
- A conversation history (for context on follow-up questions)
- Relevant memory from previous research (if any)
- A user query
- Fresh results collected from research tools

Your job is to:
- Combine memory + fresh results into a clear concise answer
- For simple queries: 2-3 paragraphs maximum
- For complex queries like "summarize research": use headings and bullets
- If memory already covers the topic, prioritize it and supplement with fresh results
- Always cite sources at the end
"""

def synthesize(query: str, tool_results: list, conversation_history: list = [], memory_context: str = "") -> str:
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
            
    memory_text = ""
    if memory_context:
        memory_text = f"\nRelevant Memory from Previous Research:\n{memory_context[:1000]}\n"
        
    response = llm.invoke([
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(content=f"""
            {history_text}
            {memory_text}
            
            Current Query: {query}
            
            Research Results:
            {combined}
            
            Write a clear concise answer.
        """)
    ])
    
    return response.content