import os
import sys
from dotenv import load_dotenv
from langsmith import Client

# Load environment variables from .env file
load_dotenv()

def deploy_to_langsmith():
    """Deploy the application to LangGraph Smith"""
    
    # Check if API key is set
    api_key = os.environ.get("LANGCHAIN_API_KEY")
    if not api_key:
        print("Error: LANGCHAIN_API_KEY environment variable not set.")
        print("Please set it in the .env file or as an environment variable.")
        sys.exit(1)
    
    print("Deploying application to LangGraph Smith...")
    
    try:
        # Initialize LangSmith client
        client = Client()
        
        # Create a deployment project
        project_name = "finops-approval-workflow"
        
        print(f"Creating project: {project_name}")
        project = client.create_project(project_name, description="FinOps Approval Workflow Application")
        
        print(f"Project created with ID: {project.id}")
        print(f"Your application will be available at: https://smith.langchain.com/o/e6cf59c8-b7a3-5aab-b88e-cc31c4aed2d3/host/deployments?mode=graph")
        
        print("\nTo complete the deployment:")
        print("1. Go to the URL above")
        print("2. Click on 'New Deployment'")
        print("3. Select 'Upload from local'")
        print("4. Upload the finops_approval_workflow.zip file")
        print("5. Follow the prompts to complete the deployment")
        
    except Exception as e:
        print(f"Error deploying application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_to_langsmith()
