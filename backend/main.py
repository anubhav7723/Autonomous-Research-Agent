from agents.graph import build_graph

def main():
    agent = build_graph()
    
    print("Research Agent Started")
    print("Type 'exit' to quit\n")
    print("Type clear to reset conversation history\n")
    
    conversation_history = []
    
    while True:
        query = input("Ask a question: ")
        
        if query.lower() == "exit":
            break
        
        if query.lower() == "clear":
            conversation_history = []
            print("[Memort Cleared]\n")
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
        print("="*50 + "\n")

if __name__ == "__main__":
    main()