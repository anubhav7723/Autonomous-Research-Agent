import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

model_name = "mixtral-8x7b-32768"