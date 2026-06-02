import json 
import re
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_client import get_llm

llm = get_llm()

PLANNER_PROMPT = """
You are a research planner. Break down the user's query into 2 - 3 subtasks.

Available Tools:
- web_search: current news, recent events
- wikipedia: background knowledge, definitions, history
- pdf_reader: read a PDF from URL or file path
- arxiv_search: academic papers, research studies

Respond ONLY in this JSON format, nothing else:
{
    "tasks": [
        {"tool": "tool_name", "query": "specific query for this tool"},
        {"tool": "tool_name", "query": "specific query for this tool"}
    ]
}
"""

def plan(query: str) -> list:
    print("\n Planner : breaking down {query}\n")
    
    response = llm.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=query)
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