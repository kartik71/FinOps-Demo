import streamlit as st
import pandas as pd
import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="FinOps Approval Workflow",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .persona-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
        text-align: center;
        background-color: white;
        border-left: 4px solid #e0e0e0;
    }
    
    .persona-box.active {
        border-left-color: #1976d2;
        box-shadow: 0 3px 10px rgba(25, 118, 210, 0.15);
    }
    
    .persona-box.completed {
        border-left-color: #2e7d32;
    }
    
    .log-entry {
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 6px;
        background-color: #f9f9f9;
        border-left: 3px solid #ccc;
    }
    
    .log-entry.alex {
        border-left-color: #2196f3;
    }
    
    .log-entry.sam {
        border-left-color: #ff9800;
    }
    
    .log-entry.mira {
        border-left-color: #9c27b0;
    }
    
    .log-entry.jordan {
        border-left-color: #f44336;
    }
    
    .log-entry.sam-decision {
        border-left-color: #4caf50;
    }
    
    .log-entry.taylor {
        border-left-color: #795548;
    }
    
    .log-entry.alex-summary {
        border-left-color: #607d8b;
    }
    
    .data-flow {
        height: 2px;
        background: linear-gradient(90deg, #2196f3, #4caf50);
        margin-top: 10px;
        margin-bottom: 10px;
        animation: progressAnimation 2s ease-in-out;
        transform-origin: left;
    }
    
    @keyframes progressAnimation {
        0% { transform: scaleX(0); }
        100% { transform: scaleX(1); }
    }
    
    .status-badge {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.7em;
        font-weight: 500;
        float: right;
    }
    
    .status-pending {
        background-color: #f5f5f5;
        color: #757575;
    }
    
    .status-active {
        background-color: #1976d2;
        color: white;
    }
    
    .status-completed {
        background-color: #2e7d32;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_stage' not in st.session_state:
    st.session_state.workflow_stage = 0
    
if 'logs' not in st.session_state:
    st.session_state.logs = []
    
if 'api_response' not in st.session_state:
    st.session_state.api_response = None

# Function to add log entries
def add_log(persona, message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append({
        "timestamp": timestamp,
        "persona": persona,
        "message": message
    })

# Function to load sample data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Create a simple sample dataframe if file is not found
        data = {
            "Project_ID": ["P0001", "P0002", "P0003"],
            "PO_Requested": [5000, 15000, 8000],
            "Cost_Center": ["IT-001", "HR-002", "FIN-003"],
            "Supplier": ["VendorX", "VendorY", "VendorZ"],
            "Budget_Remaining": [10000, 5000, 20000],
            "Variance": [0.05, 0.15, 0.02]
        }
        return pd.DataFrame(data)

# Load data
df = load_data()

# App title and description
st.title("🏢 FinOps Approval Workflow")
st.markdown("""
This demo showcases an automated financial operations approval workflow using LangGraph.
The system processes purchase orders through multiple agents that handle different aspects of the approval process.
""")

# Sidebar with configuration
with st.sidebar:
    st.header("Configuration")
    
    # API URL configuration
    api_url = st.text_input(
        "API URL",
        value=os.environ.get("FINOPS_API_URL", "http://localhost:8000/finops-workflow/invoke"),
        help="URL of the deployed LangGraph workflow API"
    )
    
    # Project selection
    selected_project = st.selectbox(
        "Select Project",
        options=df["Project_ID"].tolist(),
        index=0,
        help="Select a project to process"
    )
    
    # Display project details
    if selected_project:
        project_data = df[df["Project_ID"] == selected_project].iloc[0]
        st.subheader("Project Details")
        st.info(f"""
        **Project ID:** {project_data['Project_ID']}
        **PO Amount:** ${project_data['PO_Requested']:,.2f}
        **Cost Center:** {project_data['Cost_Center']}
        **Supplier:** {project_data['Supplier']}
        **Budget Remaining:** ${project_data['Budget_Remaining']:,.2f}
        """)
    
    # Demo controls
    st.subheader("Demo Controls")
    
    if st.session_state.workflow_stage == 0:
        if st.button("Start Workflow", use_container_width=True):
            st.session_state.workflow_stage = 1
            add_log("System", f"Starting workflow for project {selected_project}")
    else:
        if st.button("Reset Demo", use_container_width=True):
            st.session_state.workflow_stage = 0
            st.session_state.logs = []
            st.session_state.api_response = None
            st.rerun()
    
    # Demo speed control
    demo_speed = st.slider("Demo Speed", min_value=1, max_value=5, value=3, help="Control the speed of the demo")
    
    # Auto-advance toggle
    auto_advance = st.checkbox("Auto Advance", value=True, help="Automatically advance through workflow stages")

# Function to determine persona status
def persona_status(persona_name, stage_number):
    current_stage = st.session_state.workflow_stage
    
    if current_stage > stage_number:
        return "completed"
    elif current_stage == stage_number:
        return "active"
    else:
        return "pending"

# Main content layout with two columns
col1, col2 = st.columns([2, 1])

# Workflow visualization column
with col1:
    st.header("Workflow Visualization")
    
    # Create a container for the workflow
    workflow_container = st.container()
    
    with workflow_container:
        # Define persona information
        personas = [
            {"name": "Alex", "role": "User Interface", "description": "Handles user input and project selection", "stage": 1},
            {"name": "Sam", "role": "Data Retriever", "description": "Retrieves project data from database", "stage": 2},
            {"name": "Mira", "role": "Budget Analyst", "description": "Checks if PO amount is within budget", "stage": 3},
            {"name": "Jordan", "role": "Compliance Officer", "description": "Verifies supplier compliance", "stage": 3},
            {"name": "Sam Decision", "role": "Approval Manager", "description": "Makes final approval decision", "stage": 4},
            {"name": "Taylor", "role": "Financial Analyst", "description": "Analyzes variance data", "stage": 5},
            {"name": "Alex Summary", "role": "Report Generator", "description": "Generates final summary", "stage": 6}
        ]
        
        # Display personas in a grid
        cols = st.columns(len(personas))
        
        for i, persona in enumerate(personas):
            status = persona_status(persona["name"], persona["stage"])
            
            with cols[i]:
                st.markdown(f"""
                <div class="persona-box {status}">
                    <span class="status-badge status-{status}">{status.upper()}</span>
                    <h4>{persona["name"]}</h4>
                    <p><strong>{persona["role"]}</strong></p>
                    <p style="font-size: 0.8em;">{persona["description"]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Process workflow stages
        if st.session_state.workflow_stage >= 1:
            # Alex stage
            add_log("Alex", f"Processing user input for project {selected_project}")
            
            # Display data flow
            st.markdown('<div class="data-flow"></div>', unsafe_allow_html=True)
            
            if auto_advance and st.session_state.workflow_stage == 1:
                time.sleep(2.0 / demo_speed)
                st.session_state.workflow_stage = 2
                st.rerun()
        
        if st.session_state.workflow_stage >= 2:
            # Sam stage
            project_data = df[df["Project_ID"] == selected_project].iloc[0]
            add_log("Sam", f"Retrieved data for project {selected_project}")
            add_log("Sam", f"PO Amount: ${project_data['PO_Requested']:,.2f}, Budget: ${project_data['Budget_Remaining']:,.2f}, Supplier: {project_data['Supplier']}")
            
            # Display data flow
            st.markdown('<div class="data-flow"></div>', unsafe_allow_html=True)
            
            if auto_advance and st.session_state.workflow_stage == 2:
                time.sleep(2.0 / demo_speed)
                st.session_state.workflow_stage = 3
                st.rerun()
        
        if st.session_state.workflow_stage >= 3:
            # Mira and Jordan stage
            project_data = df[df["Project_ID"] == selected_project].iloc[0]
            budget_ok = project_data['PO_Requested'] <= project_data['Budget_Remaining']
            compliance_ok = project_data['Supplier'] != "VendorY"
            
            add_log("Mira", f"Budget check: {'✅ PASSED' if budget_ok else '❌ FAILED'}")
            add_log("Jordan", f"Compliance check: {'✅ PASSED' if compliance_ok else '❌ FAILED'}")
            
            # Display data flow
            st.markdown('<div class="data-flow"></div>', unsafe_allow_html=True)
            
            if auto_advance and st.session_state.workflow_stage == 3:
                time.sleep(2.0 / demo_speed)
                st.session_state.workflow_stage = 4
                st.rerun()
        
        if st.session_state.workflow_stage >= 4:
            # Sam Decision stage
            project_data = df[df["Project_ID"] == selected_project].iloc[0]
            budget_ok = project_data['PO_Requested'] <= project_data['Budget_Remaining']
            compliance_ok = project_data['Supplier'] != "VendorY"
            approved = budget_ok and compliance_ok
            
            reason = ""
            if not budget_ok:
                reason = "Budget exceeded"
            elif not compliance_ok:
                reason = "Compliance issue with supplier"
                
            st.session_state.api_response = {"approved": approved, "reason": reason}
            
            add_log("Sam Decision", f"Decision: {'✅ APPROVED' if approved else f'❌ REJECTED - {reason}'}")
            
            # Display data flow
            st.markdown('<div class="data-flow"></div>', unsafe_allow_html=True)
            
            if auto_advance and st.session_state.workflow_stage == 4:
                time.sleep(2.0 / demo_speed)
                st.session_state.workflow_stage = 5
                st.rerun()
        
        if st.session_state.workflow_stage >= 5:
            # Taylor stage
            project_data = df[df["Project_ID"] == selected_project].iloc[0]
            variance = project_data['Variance']
            
            add_log("Taylor", f"Variance analysis: {variance:.2%}")
            
            # Display data flow
            st.markdown('<div class="data-flow"></div>', unsafe_allow_html=True)
            
            if auto_advance and st.session_state.workflow_stage == 5:
                time.sleep(2.0 / demo_speed)
                st.session_state.workflow_stage = 6
                st.rerun()
        
        if st.session_state.workflow_stage >= 6:
            # Alex Summary stage
            approved = st.session_state.api_response.get('approved', False)
            
            summary = "PO validated, budget and compliance passed, variance analyzed." if approved else f"PO rejected: {st.session_state.api_response.get('reason', 'Unknown reason')}"
            
            add_log("Alex Summary", f"Final summary: {summary}")
            
            # Display final result
            if approved:
                st.success("✅ Purchase Order Approved")
            else:
                st.error(f"❌ Purchase Order Rejected: {st.session_state.api_response.get('reason', 'Unknown reason')}")

# Activity log column
with col2:
    st.header("Activity Log")
    
    # Display logs in reverse chronological order
    for log in reversed(st.session_state.logs):
        persona_class = log["persona"].lower().replace(" ", "-")
        
        st.markdown(f"""
        <div class="log-entry {persona_class}">
            <strong>{log["timestamp"]}</strong> - <strong>{log["persona"]}</strong>: {log["message"]}
        </div>
        """, unsafe_allow_html=True)

# Add a section for API integration
st.header("API Integration")
with st.expander("View API Request/Response"):
    st.subheader("API Request")
    st.code(json.dumps({"project_id": selected_project}, indent=2), language="json")
    
    st.subheader("API Response")
    if st.session_state.api_response:
        st.code(json.dumps(st.session_state.api_response, indent=2), language="json")
    else:
        st.info("No API response yet. Start the workflow to see the response.")

# Footer
st.markdown("---")
st.markdown("FinOps Approval Workflow POC - Powered by LangGraph")
