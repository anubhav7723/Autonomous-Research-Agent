# Autonomous Research Agent/run.py
import sys
import os

# Add backend to Python path so frontend can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from frontend.app import app

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)