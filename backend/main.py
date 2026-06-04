from agents.graph import build_graph
from memory.vector_store import clear, count

def main():
    agent = build_graph()
    
    print("Research Agent Started")
    print("Commands: 'exit' | 'clear' (reset history) | 'memory' (show stored chunks)\n")
    
    conversation_history = []
    
    while True:
        query = input("Ask a question: ")
        
        if query.lower() == "exit":
            break
        
        if query.lower() == "clear":
            conversation_history = []
            print("[Memory Cleared]\n")
            continue
        
        if query.lower() == "memory":
            print(f"[Vector store has {count()} chunks stored]\n")
            continue
        
        conversation_history.append({
            'role': 'user',
            'content': query
        })
        
        print("\n[AGENT] Starting research...\n")
        
        result = agent.invoke({
            "query": query,
            "conversation_history": conversation_history,
            "tasks": [],
            "tool_results": [],
            "memory_context": "",
            "final_report": ""
        })
        
        conversation_history.append({
            'role': 'assistant',
            'content': result['final_report']
        })
        
        print("\n" + "="*50)
        print("RESEARCH REPORT")
        print("="*50)
        print(result["final_report"])
        print(f"\n[Memory: {len(conversation_history)} messages | {count()} vector chunks]")
        print("="*50 + "\n")

if __name__ == "__main__":
    main()