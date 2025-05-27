import os
import uvicorn
from langgraph_server import app

def run_server():
    """Run the FastAPI server locally"""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_server()
