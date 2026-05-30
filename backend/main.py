from agents.core import build_agent

def main():
    agent = build_agent()
    
    print("Research Agent Started")
    print("Type 'exit' to quit\n")
    
    while True:
        query = input("Ask a question: ")
        
        if query.lower() == "exit":
            break
        
        result = agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        
        print("\nAnswer:\n")
        print(result["messages"][-1].content)
        print()

if __name__ == "__main__":
    main()