from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
from agents.graph import build_graph
from memory.vector_store import clear, count
from frontend.streaming import StreamCallback
import json
import queue
import threading
import os

app = Flask(__name__, template_folder="templates")
CORS(app)
agent = build_graph()

# Keyed by session_id sent from frontend
session_histories = {}
session_queues = {}

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def get_history(session_id: str) -> list:
    if session_id not in session_histories:
        session_histories[session_id] = []
    return session_histories[session_id]


def get_queue(session_id: str) -> queue.Queue:
    if session_id not in session_queues:
        session_queues[session_id] = queue.Queue()
    return session_queues[session_id]



def stream_agent(session_id: str, query: str):
    q = get_queue(session_id)
    history = get_history(session_id)

    q.put({"type": "status", "message": "Planning research tasks..."})

    try:
        result = agent.invoke(
            {
                "query": query,
                "conversation_history": history,
                "tasks": [],
                "tool_results": [],
                "memory_context": "",
                "final_report": ""
            },
            config={"callbacks": [StreamCallback(q)]}
        )

        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": result["final_report"]})

        # Keep last 20 messages only
        if len(history) > 20:
            session_histories[session_id] = history[-20:]

        q.put({"type": "report", "message": result["final_report"]})
        q.put({"type": "done", "message": ""})

    except Exception as e:
        q.put({"type": "error", "message": f"Agent error: {str(e)}"})
        q.put({"type": "done", "message": ""})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research():
    data = request.get_json()
    query = data.get("query", "").strip()
    session_id = data.get("session_id", "").strip()  # ✅ from frontend

    if not query:
        return {"error": "Empty query"}, 400
    if len(query) < 5:
        return {"error": "Query too short"}, 400
    if not session_id:
        return {"error": "Missing session_id"}, 400

    q = get_queue(session_id)
    while not q.empty():
        q.get()

    thread = threading.Thread(target=stream_agent, args=(session_id, query))
    thread.daemon = True
    thread.start()

    return {"status": "started"}, 200

@app.route("/stream/<session_id>")
def stream(session_id):
    print(f"[STREAM] New connection for session: {session_id}")  # ✅ add this
    q = get_queue(session_id)

    def generate():
        print(f"[STREAM] Generating for session: {session_id}")  # ✅ add this
        while True:
            try:
                event = q.get(timeout=60)
                yield f"data: {json.dumps(event)}\n\n"
                if event["type"] == "done":
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Request timed out'})}\n\n"
                break

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/history/<session_id>", methods=["GET"])
def history(session_id):
    h = get_history(session_id)
    return {"history": h, "count": len(h)}


@app.route("/clear", methods=["POST"])
def clear_memory():
    data = request.get_json()
    session_id = data.get("session_id", "")
    session_histories[session_id] = []
    clear()
    return {"status": "cleared"}


@app.route("/memory", methods=["GET"])
def memory_count():
    return {"chunks": count()}


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)