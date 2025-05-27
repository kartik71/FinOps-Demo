# FinOps Approval Workflow

A LangGraph application for financial operations approval workflow. This application processes purchase orders through a series of agents that perform budget checks, compliance verification, and variance analysis.

## Application Structure

The workflow consists of the following agents:

1. **Alex**: Handles initial user input and provides a project ID
2. **Sam**: Retrieves project data from a CSV file
3. **Mira**: Performs budget checks
4. **Jordan**: Performs compliance checks
5. **Sam_decision**: Makes approval decisions based on Mira and Jordan's outputs
6. **Taylor**: Analyzes variance data
7. **Alex_summary**: Provides a final summary

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
python run_apps.py
```

The server will start on http://localhost:8000

## API Endpoints

- `/finops-workflow`: Main workflow endpoint
- `/`: Health check endpoint

## Deploying to LangGraph Smith

1. Install the LangGraph CLI:
```bash
pip install langsmith langgraph
```

2. Login to LangGraph Smith:
```bash
langsmith login
```

3. Deploy the application:
```bash
langsmith deploy langgraph_server:app --app finops-workflow
```

4. Access your deployed application at LangGraph Smith: https://smith.langchain.com/o/e6cf59c8-b7a3-5aab-b88e-cc31c4aed2d3/host/deployments?mode=graph
