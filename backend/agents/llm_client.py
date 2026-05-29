from langchain_groq import ChatGroq
from config import model_name

llm = ChatGroq(
    model= model_name,
    temperature=0.7
)

def get_llm():
    return llm