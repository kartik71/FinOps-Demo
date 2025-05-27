import streamlit as st
import pandas as pd
import requests
import time
import os
from pathlib import Path
import json

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
    /* Main container styles */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1300px;
    }
    
    /* Persona box styles - cleaner and more consistent */
    .persona-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: all 0.3s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        background-color: white;
        border-top: 3px solid #e0e0e0;
    }
    
    /* Professional hover effect */
    .persona-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
    }
    
    /* Status badge styling */
    .status-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.65em;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .status-pending { background-color: #f5f5f5; color: #757575; }
    .status-active { 
        background-color: #1976d2; 
        color: white; 
        box-shadow: 0 0 5px rgba(25, 118, 210, 0.5);
    }
    .status-completed { 
        background-color: #2e7d32; 
        color: white;
    }
    
    /* Clean active state */
    .active-persona {
        border-top-color: #1976d2;
        box-shadow: 0 3px 10px rgba(25, 118, 210, 0.15);
    }
    
    /* Workflow container and title */
    .workflow-title {
        text-align: center;
        margin: 10px 0 25px 0;
        color: #424242;
        font-weight: 500;
        font-size: 1.2rem;
    }
    .workflow-container {
        margin: 15px 0;
        padding: 5px 0;
    }
    
    /* Professional workflow connector styling */
    .workflow-connector {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 140px;
        position: relative;
    }
    .connector-line {
        height: 2px;
        width: 100%;
        background-color: #1976d2;
        position: relative;
    }
    .connector-line.inactive {
        background-color: #e0e0e0;
    }
    .arrow-right {
        width: 0;
        height: 0;
        border-top: 5px solid transparent;
        border-bottom: 5px solid transparent;
        border-left: 8px solid #1976d2;
        position: absolute;
        right: 0;
    }
    .arrow-right.inactive {
        border-left-color: #e0e0e0;
    }
    .data-packet {
        position: absolute;
        width: 8px;
        height: 8px;
        background-color: #1976d2;
        border-radius: 50%;
        animation: movePacket 1.5s infinite linear;
        box-shadow: 0 0 4px rgba(25, 118, 210, 0.5);
    }
    
    .data-flow {
        height: 2px;
        background: linear-gradient(90deg, #2196f3, #4caf50);
        margin-top: 10px;
        margin-bottom: 10px;
        animation: progressAnimation 2s ease-in-out;
        transform-origin: left;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(2, 136, 209, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(2, 136, 209, 0); }
        100% { box-shadow: 0 0 0 0 rgba(2, 136, 209, 0); }
    }
    
    @keyframes progressAnimation {
        0% { transform: scaleX(0); }
        100% { transform: scaleX(1); }
    }
    
    @keyframes movePacket {
        0% { left: 0; opacity: 1; }
        100% { left: 100%; opacity: 0; }
    }
    
    /* Enhanced persona styling */
    .persona-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }
    
    .persona-role {
        font-weight: 500;
        color: #555;
    }
    
    .persona-description {
        font-size: 0.75em;
        color: #666;
        margin: 8px 0;
    }
    
    /* Completed persona styling */
    .completed-persona {
        border-left-width: 6px;
    }
    
    /* Active persona styling */
    .active-persona .persona-icon {
        animation: bounce 1s infinite alternate;
    }
    
    @keyframes bounce {
        0% { transform: translateY(0); }
        100% { transform: translateY(-5px); }
    }
    
    /* Log container with vertical timeline */
    .log-container {
        position: relative;
        padding-left: 20px;
        max-height: 500px;
        overflow-y: auto;
        margin-top: 15px;
    }
    
    /* Vertical timeline line */
    .log-container:before {
        content: '';
        position: absolute;
        top: 0;
        left: 2px;
        width: 2px;
        height: 100%;
        background: #e0e0e0;
    }
    
    /* Clean log entry styling */
    .log-entry {
        padding: 12px 15px;
        margin-bottom: 12px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        position: relative;
        background-color: white;
        animation: fadeIn 0.4s ease-in;
        border-left: none;
    }
    
    /* Timeline marker */
    .log-entry:before {
        content: '';
        position: absolute;
        left: -24px;
        top: 15px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #1976d2;
        border: 2px solid white;
        box-shadow: 0 0 0 1px #e0e0e0;
        z-index: 1;
    }
    
    /* Latest log entry styling */
    .latest-log {
        border-left: 3px solid #1976d2;
        background-color: #f5f9ff;
        box-shadow: 0 2px 5px rgba(25, 118, 210, 0.1);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .approval-result {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
        animation: scaleIn 0.5s ease-out;
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🏢 FinOps Approval Workflow")
st.caption("An end-to-end demo of the approval process across multiple personas")

# Initialize session states
if 'workflow_stage' not in st.session_state:
    st.session_state.workflow_stage = 0  # 0: Not started, 1-7: Stages of workflow

if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = {}
    
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
    
if 'api_response' not in st.session_state:
    st.session_state.api_response = None

# Function to add log messages with timestamps
def add_log(persona, message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.log_messages.append({
        "timestamp": timestamp,
        "persona": persona,
        "message": message
    })

# Load sample data
@st.cache_data
def load_data():
    try:
        current_dir = Path(__file__).parent
        data_path = current_dir / 'data.csv'
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame({"Project_ID": ["P0001"], "PO_Requested": [5000], "Cost_Center": ["IT"], 
                           "Supplier": ["VendorX"], "Budget_Remaining": [10000], "Variance": [0.2]})

# Sidebar with configuration
with st.sidebar:
    st.header("Configuration")
    default_api_url = os.environ.get("FINOPS_API_URL", "http://localhost:8000/finops-workflow/invoke")
    api_url = st.text_input("API URL", value=default_api_url)
    
    st.header("Demo Settings")
    demo_speed = st.slider("Demo Speed", 0.5, 3.0, 1.5, 0.1, 
                          help="Controls how fast the demo progresses (higher is faster)")
    
    st.header("Persona Information")
    st.markdown("""
    - **Alex** - User Interface (Request Entry)
    - **Sam** - Data Retrieval Specialist
    - **Mira** - Budget Analyst
    - **Jordan** - Compliance Officer
    - **Sam Decision** - Approval Manager
    - **Taylor** - Financial Analyst
    - **Alex Summary** - Workflow Coordinator
    """)
    
    # Reset button
    if st.button("Reset Demo"):
        st.session_state.workflow_stage = 0
        st.session_state.workflow_data = {}
        st.session_state.log_messages = []
        st.session_state.api_response = None
        st.rerun()

# Load the data
df = load_data()

# Main interface with two columns
col1, col2 = st.columns([3, 2])

# Left column - Project selection and workflow visualization
with col1:
    # Project selection section
    st.header("Project Selection")
    
    project_col1, project_col2 = st.columns([3, 2])
    
    with project_col1:
        selected_project = st.selectbox(
            "Select a project:",
            options=df["Project_ID"].unique(),
            index=0,
            disabled=st.session_state.workflow_stage > 0
        )
        
        if selected_project:
            project_data = df[df["Project_ID"] == selected_project].iloc[0]
            st.dataframe({
                "Attribute": ["Project ID", "PO Amount", "Cost Center", "Supplier", "Budget Remaining", "Variance"],
                "Value": [
                    project_data["Project_ID"],
                    f"${project_data['PO_Requested']:,.2f}",
                    project_data["Cost_Center"],
                    project_data["Supplier"],
                    f"${project_data['Budget_Remaining']:,.2f}",
                    project_data["Variance"]
                ]
            }, hide_index=True)
    
    with project_col2:
        st.write("")
        st.write("")
        start_button = st.button(
            "Start Approval Process", 
            type="primary",
            disabled=st.session_state.workflow_stage > 0,
            use_container_width=True
        )
        
        st.markdown("### Current Status")
        
        if st.session_state.workflow_stage == 0:
            st.info("Waiting to start workflow")
        elif st.session_state.workflow_stage < 7:
            st.info(f"Processing step {st.session_state.workflow_stage} of 7")
        else:
            if st.session_state.api_response and st.session_state.api_response.get("approved", False):
                st.success("Workflow complete - PO APPROVED")
            else:
                st.error("Workflow complete - PO REJECTED")
    
    # Start the workflow when button is clicked
    if start_button:
        st.session_state.workflow_stage = 1
        add_log("System", f"Starting approval workflow for project {selected_project}")
        
        # Call the API to get real data
        try:
            with st.spinner("Processing approval workflow..."):
                # Make API call to the backend
                payload = {"project_id": selected_project}
                response = requests.post(api_url, json=payload)
                
                if response.status_code == 200:
                    st.session_state.api_response = response.json()
                    add_log("System", "API call successful")
                else:
                    add_log("System", f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            add_log("System", f"Error connecting to API: {str(e)}")
    
    # Workflow visualization
    st.markdown("### Workflow Visualization")
    
    # Display personas with their current status
    def persona_status(persona_name, stage_number):
        if st.session_state.workflow_stage == 0:
            return "status-pending", "Pending"
        elif st.session_state.workflow_stage == stage_number:
            return "status-active", "Active"
        elif st.session_state.workflow_stage > stage_number:
            return "status-complete", "Complete"
        else:
            return "status-pending", "Pending"
    
    # Auto-advance the workflow for the demo
    if 1 <= st.session_state.workflow_stage < 7:
        # This will be executed once per page refresh
        time.sleep(3.0 / demo_speed)  # Speed controlled by demo_speed
        st.session_state.workflow_stage += 1
        st.rerun()
    
    # Create a container for the workflow section with a cleaner look
    with st.container():
        # Clean header for the workflow
        st.markdown("<h3 class='workflow-title'>FinOps Approval Workflow Process</h3>", unsafe_allow_html=True)
        
        # Add some space before the workflow visualization
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        
        # Create columns with appropriate spacing for each persona
        persona_cols = st.columns([1, 0.25, 1, 0.25, 1, 0.25, 1, 0.25, 1, 0.25, 1, 0.25, 1])
        
        # Define persona data with icons and roles - simplified and consistent descriptions
        personas = [
            {"name": "Alex", "stage": 1, "icon": "👨‍💼", "role": "Request Intake", "col_idx": 0, "color": "persona-alex"},
            {"name": "Sam", "stage": 2, "icon": "👨‍💻", "role": "Data Retrieval", "col_idx": 2, "color": "persona-sam"},
            {"name": "Mira", "stage": 3, "icon": "👩‍💼", "role": "Budget Check", "col_idx": 4, "color": "persona-mira"},
            {"name": "Jordan", "stage": 4, "icon": "👨‍⚖️", "role": "Compliance", "col_idx": 6, "color": "persona-jordan"},
            {"name": "Sam Decision", "stage": 5, "icon": "👨‍💻", "role": "Approval", "col_idx": 8, "color": "persona-sam-decision"},
            {"name": "Taylor", "stage": 6, "icon": "👩‍🔬", "role": "Variance Analysis", "col_idx": 10, "color": "persona-taylor"},
            {"name": "Alex Summary", "stage": 7, "icon": "👨‍💼", "role": "Final Summary", "col_idx": 12, "color": "persona-alex-summary"},
        ]
    
    # Add connectors between personas with improved styling
    for i in range(len(personas) - 1):
        connector_idx = personas[i]["col_idx"] + 1
        with persona_cols[connector_idx]:
            if st.session_state.workflow_stage > personas[i]["stage"]:
                # Active connector with animation
                st.markdown(f"""
                <div class='workflow-connector active-connector'>
                    <div class='connector-line'></div>
                    <div class='arrow-right'></div>
                    <div class='data-packet'></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Inactive connector
                st.markdown(f"""
                <div class='workflow-connector'>
                    <div class='connector-line inactive'></div>
                    <div class='arrow-right inactive'></div>
                </div>
                """, unsafe_allow_html=True)
    
    # Render each persona with enhanced styling
    for persona in personas:
        with persona_cols[persona["col_idx"]]:
            status_class, status_text = persona_status(persona["name"], persona["stage"])
            
            # Add active-persona class if this is the current stage
            active_class = " active-persona" if st.session_state.workflow_stage == persona["stage"] else ""
            completed_class = " completed-persona" if st.session_state.workflow_stage > persona["stage"] else ""
            
            # Simplified and cleaner persona box rendering
            st.markdown(f"""
            <div class="persona-box {persona['color']}{active_class}{completed_class}">
                <div class="persona-icon">{persona['icon']}</div>
                <h4>{persona['name']}</h4>
                <p class="persona-role">{persona['role']}</p>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Add log messages based on workflow stage
    if st.session_state.workflow_stage >= 1:
        add_log("Alex", f"Received request for project {selected_project}")
        
    if st.session_state.workflow_stage >= 2 and st.session_state.api_response:
        add_log("Sam", f"Retrieved project data: PO Amount ${st.session_state.api_response.get('po_amount', 'N/A')}, Supplier: {st.session_state.api_response.get('supplier', 'N/A')}")
        
    if st.session_state.workflow_stage >= 3 and st.session_state.api_response:
        budget_ok = st.session_state.api_response.get('budget_ok', False)
        add_log("Mira", f"Budget check: {'✅ PASSED' if budget_ok else '❌ FAILED'}")
        
    if st.session_state.workflow_stage >= 4 and st.session_state.api_response:
        compliance_ok = st.session_state.api_response.get('compliance_ok', False)
        add_log("Jordan", f"Compliance check: {'✅ PASSED' if compliance_ok else '❌ FAILED'}")
        
    if st.session_state.workflow_stage >= 5 and st.session_state.api_response:
        approved = st.session_state.api_response.get('approved', False)
        reason = st.session_state.api_response.get('reason', 'No specific reason')
        add_log("Sam Decision", f"Decision: {'✅ APPROVED' if approved else f'❌ REJECTED - {reason}'}")
        
    if st.session_state.workflow_stage >= 6 and st.session_state.api_response:
        variance = st.session_state.api_response.get('variance', 'N/A')
        add_log("Taylor", f"Variance analysis: {variance}")
        
    if st.session_state.workflow_stage >= 7 and st.session_state.api_response:
        summary = st.session_state.api_response.get('summary', 'Process complete')
        add_log("Alex Summary", f"Final summary: {summary}")

    # Display final results when complete
    if st.session_state.workflow_stage >= 7 and st.session_state.api_response:
        st.markdown("---")
        st.header("Approval Results")
        
        # Display approval status with appropriate styling
        if st.session_state.api_response.get("approved", False):
            st.success("### ✅ PURCHASE ORDER APPROVED")
        else:
            st.error(f"### ❌ PURCHASE ORDER REJECTED: {st.session_state.api_response.get('reason', 'No reason provided')}")
        
        # Show key metrics
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            st.metric("Project ID", st.session_state.api_response.get('project_id', 'N/A'))
        with metrics_cols[1]:
            st.metric("PO Amount", f"${st.session_state.api_response.get('po_amount', 0):,.2f}")
        with metrics_cols[2]:
            st.metric("Budget Remaining", f"${st.session_state.api_response.get('budget_remaining', 0):,.2f}")
        with metrics_cols[3]:
            st.metric("Variance", f"{st.session_state.api_response.get('variance', 'N/A')}")
        
        # Display summary
        st.info(f"**Summary:** {st.session_state.api_response.get('summary', 'N/A')}")

# Right column - Real-time logs and technical details
with col2:
    st.header("Real-time Activity Log")
    
    # Icons for personas
    persona_icons = {
        "System": "🖥️",
        "Alex": "👨‍💼",
        "Sam": "👨‍💻",
        "Mira": "👩‍💼",
        "Jordan": "👨‍⚖️",
        "Sam Decision": "👨‍💻",
        "Taylor": "👩‍🔬",
        "Alex Summary": "👨‍💼"
    }
    
    # Colors for personas
    persona_colors = {
        "System": "#6c757d",
        "Alex": "#0288d1",
        "Sam": "#388e3c",
        "Mira": "#fbc02d",
        "Jordan": "#d32f2f",
        "Sam Decision": "#388e3c",
        "Taylor": "#7b1fa2",
        "Alex Summary": "#0288d1"
    }
    
    # Background colors for log entries
    persona_bg_colors = {
        "System": "#f8f9fa",
        "Alex": "#e3f2fd",
        "Sam": "#e8f5e9",
        "Mira": "#fffde7",
        "Jordan": "#ffebee",
        "Sam Decision": "#e8f5e9",
        "Taylor": "#f3e5f5",
        "Alex Summary": "#e3f2fd"
    }
    
    # Create a container for the log messages with the vertical timeline
    st.markdown("<div class='log-container'>", unsafe_allow_html=True)
    
    # Calculate the progression marker positions for the timeline
    # This will position markers at the appropriate spots along the timeline
    total_stages = 7
    current_stage = min(st.session_state.workflow_stage, total_stages)
    progress_percentage = (current_stage / total_stages) * 100
    
    # Create the log messages with clean timeline styling
    for i, log in enumerate(reversed(st.session_state.log_messages)):
        persona = log["persona"]
        icon = persona_icons.get(persona, "🔹")
        color = persona_colors.get(persona, "#6c757d")
        
        # Different styling for the most recent log entry
        highlight_class = "" 
        if i == 0 and st.session_state.workflow_stage < 7:  # First entry and workflow not complete
            highlight_class = "latest-log"
            
        st.markdown(f"""
        <div class="log-entry {highlight_class}">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.25em; margin-right: 12px;">{icon}</div>
                <div style="flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: {color}; font-weight: 500;">{persona}</span>
                        <span style="color: #757575; font-size: 0.75em;">{log['timestamp']}</span>
                    </div>
                    <div style="margin-top: 6px; color: #424242;">{log['message']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Close the log container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add a progress bar to visually show the workflow progression
    if st.session_state.workflow_stage > 0:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.progress(progress_percentage / 100)
    
    # Technical details section
    if st.session_state.api_response:
        st.markdown("---")
        st.header("Technical Details")
        
        # Add tabs for different views
        tech_tab1, tech_tab2 = st.tabs(["API Response", "Workflow Metadata"])
        
        with tech_tab1:
            st.json(st.session_state.api_response)
        
        with tech_tab2:
            # Display information about the workflow
            st.markdown("### Workflow Information")
            st.markdown("**Graph Type:** LangGraph Financial Approval Workflow")
            st.markdown("**Number of Agents:** 7")
            st.markdown("**Current Stage:** " + ("Complete" if st.session_state.workflow_stage >= 7 else f"Step {st.session_state.workflow_stage} of 7"))
            
            # Progress bar for workflow completion
            progress = min(st.session_state.workflow_stage / 7, 1.0)
            st.progress(progress)

# Footer
st.markdown("---")
st.caption("FinOps Approval Workflow - Powered by LangGraph & Streamlit")

