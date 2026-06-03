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

Respond ONLY in this JSON format, nothing else:
{
    "tasks": [
        {"tool": "tool_name", "query": "specific query for this tool"}
    ]
}
"""

def plan(query: str, conversation_history: list = [], memory_context: str = "") -> list:
    
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
    print("\n Planner : breaking down {query}\n")
    
    response = llm.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=f"{history_text}{memory_text}\nNew Query: {query}")
    ])
    
    try:
        text = response.content
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            tasks = data.get("tasks", [])
            print(f"[PLANNER] Generated {len(tasks)} tasks:")
            for i, t in enumerate(tasks):
                print(f"  {i+1}. {t['tool']} → {t['query']}")
            return tasks
    except Exception as e:
        print(f"[PLANNER] Error parsing plan: {e}")
    
    return [{'tool': 'web_search', 'query': query}]