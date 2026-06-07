from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
from agents.graph import build_graph
from memory.vector_store import clear, count
from frontend.streaming import StreamCallback
import json
import queue
import threading

app = Flask(__name__, template_folder="templates")
CORS(app)
agent = build_graph()

conversation_history = []
event_queue = queue.Queue()

def stream_agent(query: str):
    event_queue.put({"type": "status", "message": "Planning research tasks..."})
    
    result = agent.invoke(
        {
            "query": query,
            "conversation_history": conversation_history,
            "tasks": [],
            "tool_results": [],
            "memory_context": "",
            "final_report": ""
        },
        config={"callbacks": [StreamCallback(event_queue)]}
    )
    
    event_queue.put({"type": "report", "message": result["final_report"]})
    event_queue.put({"type": "done", "message": ""})
    
    conversation_history.append({"role": "user", "content": query})
    conversation_history.append({"role": "assistant", "content": result["final_report"]})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research():
    data = request.get_json()
    query = data.get("query", "").strip()
    
    if not query:
        return {"error": "Empty query"}, 400
    
    while not event_queue.empty():
        event_queue.get()
    
    thread = threading.Thread(target=stream_agent, args=(query,))
    thread.daemon = True
    thread.start()
    
    return {"status": "started"}, 200


@app.route("/stream")
def stream():
    def generate():
        while True:
            try:
                event = event_queue.get(timeout=60)
                yield f"data: {json.dumps(event)}\n\n"
                if event["type"] == "done":
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Timeout'})}\n\n"
                break
    
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/memory", methods=["GET"])
def memory_count():
    return {"chunks": count()}


@app.route("/clear", methods=["POST"])
def clear_memory():
    global conversation_history
    conversation_history = []
    clear()
    return {"status": "cleared"}