from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.planner import plan
from agents.synthesizer import synthesize
from tools.web_search import web_search
from tools.wikipedia_search import wikipedia_search
from tools.pdf_reader import pdf_reader
from tools.arvix_search import arxiv_search

Tools = {
    'web_search': web_search,
    'wikipedia_search': wikipedia_search,
    'pdf_reader': pdf_reader,
    'arxiv_search': arxiv_search
}

class AgentState(TypedDict):
    query: str
    conversation_history: list
    tasks: list
    tool_results: list
    final_report: str
    
#Nodes
def planner_node(state: AgentState)-> AgentState:
    tasks = plan(state['query'], state['conversation_history'])
    return {**state, 'tasks': tasks}

def executor_node(state: AgentState)-> AgentState:
    results = []
    
    for task in state['tasks']:
        tool_name = task.get('tool')
        query = task.get('query')
        
        if tool_name not in Tools:
            print(f"[EXECUTOR] Unknown tool: {tool_name}, skipping")
            continue
    
        print(f"\n[EXECUTOR] Running {tool_name} → {query}")
        
        try:
            output = Tools[tool_name].invoke(query)
            results.append({
                "tool": tool_name,
                "query": query,
                "output": output
            })
        except Exception as e:
            print(f"[EXECUTOR] Tool {tool_name} failed: {e}")
            results.append({
                "tool": tool_name,
                "query": query,
                "output": f"Tool failed: {str(e)}"
            })
    return {**state, "tool_results": results}

def synthesizer_node(state: AgentState) -> AgentState:
    report = synthesize(state["query"], state["tool_results"], state['conversation_history'])
    return {**state, "final_report": report}

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("synthesizer", synthesizer_node)
    
    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "synthesizer")
    graph.add_edge("synthesizer", END)
    
    return graph.compile()