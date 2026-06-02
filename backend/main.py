from agents.graph import build_graph

def main():
    agent = build_graph()
    
    print("Research Agent Started")
    print("Type 'exit' to quit\n")
    
    while True:
        query = input("Ask a question: ")
        
        if query.lower() == "exit":
            break
        
        print("\n[AGENT] Starting research...\n")
        
        result = agent.invoke({
            "query": query,
            "tasks": [],
            "tool_results": [],
            "final_report": ""
        })
        
        print("\n" + "="*50)
        print("RESEARCH REPORT")
        print("="*50)
        print(result["final_report"])
        print("="*50 + "\n")

if __name__ == "__main__":
    main()