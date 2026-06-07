from langchain_core.callbacks.base import BaseCallbackHandler
import queue

class StreamCallback(BaseCallbackHandler):
    def __init__(self, q: queue.Queue):
        self.queue = q
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "unknown")
        self.queue.put({
            "type": "tool_start",
            "message": f"Running {tool_name}...",
            "tool": tool_name,
            "input": str(input_str)[:100]
        })
    
    def on_tool_end(self, output, **kwargs):
        self.queue.put({
            "type": "tool_end",
            "message": "Tool finished",
        })
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        name = serialized.get("name", "")
        if name == "planner":
            self.queue.put({"type": "status", "message": "Planning tasks..."})
        elif name == "executor":
            self.queue.put({"type": "status", "message": "Executing research..."})
        elif name == "synthesizer":
            self.queue.put({"type": "status", "message": "Synthesizing report..."})