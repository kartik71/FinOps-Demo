#!/bin/bash

# Check if LANGCHAIN_API_KEY is provided
if [ -z "$1" ]; then
  echo "Usage: ./deploy.sh YOUR_LANGCHAIN_API_KEY"
  exit 1
fi

# Set the API key as an environment variable
export LANGCHAIN_API_KEY=$1

# Deploy the application using langchain CLI
python -m langchain app deploy langgraph_server:app --app finops-approval-workflow

echo "Deployment complete! Your application should now be available at:"
echo "https://smith.langchain.com/o/e6cf59c8-b7a3-5aab-b88e-cc31c4aed2d3/host/deployments?mode=graph"
