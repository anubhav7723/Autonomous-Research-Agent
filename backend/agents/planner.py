import json 
import re
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_client import get_llm

llm = get_llm()

PLANNER_PROMPT = """
You are a research planner. You will be given:
- A conversation history
- Relevant memory from previous research sessions (if any)
- A new query

If the memory context already answers the query well, return fewer tasks.
Use memory to avoid redundant tool calls.

Available tools (use EXACTLY these names):
- web_search: current news, recent events
- wikipedia_search: background knowledge, definitions, history
- pdf_reader: read a PDF from URL or file path
- arxiv_search: academic papers, research studies

QUERY WRITING RULES:
- For arxiv_search: write specific technical queries with keywords, avoid generic phrases.
  BAD:  "AI medical assistant research papers"
  GOOD: "large language models clinical decision support 2024"
  
  BAD:  "transformer architecture AI"
  GOOD: "attention mechanism transformer natural language processing Vaswani"

- For web_search: write natural news-style queries with year if relevant.
  BAD:  "AI news"
  GOOD: "latest large language model releases 2025"

- For wikipedia_search: write the exact topic or concept name.
  BAD:  "what is RAG in AI"
  GOOD: "Retrieval Augmented Generation"

Respond ONLY in this JSON format, nothing else:
{
    "tasks": [
        {"tool": "tool_name", "query": "specific query for this tool"}
    ]
}
"""

def plan(query: str, conversation_history: list = [], memory_context: str = "") -> list:
    print(f"\n[PLANNER] Breaking down: {query}\n")
    
    history_text = ""
    if conversation_history:
        history_text = "\nConversation History:\n"
        for msg in conversation_history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:300] + "..." if len(msg["content"]) > 300 else msg["content"]
            history_text += f"{role}: {content}\n"
    
    memory_text = ""
    if memory_context:
        # ✅ trimmed and marked clearly so planner doesn't over-rely on it
        memory_text = f"\nRelated memory (use only as supplement, always generate at least 1 task):\n{memory_context[:500]}\n"
    
    response = llm.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=f"""
            {history_text}
            {memory_text}
            New Query: {query}
            
            IMPORTANT: Always generate at least 1 task, even if memory seems relevant.
        """)
    ])
    
    try:
        text = response.content
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            tasks = data.get("tasks", [])
            
            # ✅ fallback if planner returns empty tasks
            if not tasks:
                print("[PLANNER] No tasks generated, falling back to web_search")
                return [{"tool": "web_search", "query": query}]
            
            print(f"[PLANNER] Generated {len(tasks)} tasks:")
            for i, t in enumerate(tasks):
                print(f"  {i+1}. {t['tool']} → {t['query']}")
            return tasks
    except Exception as e:
        print(f"[PLANNER] Error parsing plan: {e}")
    
    return [{"tool": "web_search", "query": query}]