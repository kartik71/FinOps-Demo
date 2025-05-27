import os
from typing import Dict, Any
from fastapi import FastAPI
from langserve import add_routes
from langgraph.graph import StateGraph
from agents import alex, sam, mira, jordan, sam_decision, taylor, alex_summary

# Import the main graph
from main import graph

# Create a FastAPI app
app = FastAPI(
    title="FinOps Approval Workflow",
    description="A LangGraph application for financial operations approval workflow",
    version="1.0",
)

# Add routes for the graph with config for LangGraph Smith
add_routes(
    app,
    graph,
    path="/finops-workflow",
    input_type=Dict[str, Any],
    config_keys=["configurable"],
)

# Root endpoint for health check
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "FinOps Approval Workflow is running"}

# Only run the server when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    
    # Get the port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)
