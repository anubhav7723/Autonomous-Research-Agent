from flask import Flask
from backend.agents.graph import build_graph
from backend.memory.vector_store import clear, count

app = Flask(__name__, template_folder="templates")
agent = build_graph()

conversation_history = []

