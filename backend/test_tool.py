from langchain_groq import ChatGroq
from tools.web_search import web_search
from config import api_key

llm = ChatGroq(model="llama-3.3-70b-versatile",api_key=api_key, temperature=0)
llm_with_tools = llm.bind_tools([web_search])

response = llm_with_tools.invoke("Search the web and tell me latest AI news")
print(response)
print("Tool calls:", response.tool_calls)