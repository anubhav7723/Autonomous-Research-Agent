# from langchain_groq import ChatGroq
# from langchain.tools import tool
# import os
# from dotenv import load_dotenv
# load_dotenv()

# api_key= os.environ.get("GROQ_API_KEY")


# @tool
# def hello(name:str)->str:
#     """Say hello."""
#     print("TOOL EXECUTED")
#     return f"Hello {name}"

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0.7
    
# )

# llm_with_tools = llm.bind_tools([hello])

# response = llm_with_tools.invoke(
#     "Call hello with name Anubhav"
# )

# print(response['messages'])