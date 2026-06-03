import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

model_name = "llama-3.3-70b-versatile"
hf_token = os.getenv("HF_TOKEN")  # ✅ silences the warning