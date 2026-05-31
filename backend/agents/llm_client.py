from langchain_groq import ChatGroq
from config import model_name

llm = ChatGroq(
    model= model_name,
    temperature=0.6,
#     model_kwargs={
#         "tool_choice": "auto"
#     }
)

def get_llm():
    return llm