import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import random
import hashlib

# Page configuration
st.set_page_config(
    page_title="AI Healthcare App Builder",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0d9488 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        transition: all 0.3s;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        border-color: #0d9488;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #0d9488 0%, #059669 100%);
        color: white;
        margin-left: auto;
    }
    
    .assistant-message {
        background: #f3f4f6;
        color: #1f2937;
        margin-right: auto;
    }
    
    /* Code block */
    .code-block {
        background: #1f2937;
        color: #d1d5db;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        overflow-x: auto;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0d9488 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border-radius: 9999px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(13,148,136,0.3);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-warning {
        background: #fed7aa;
        color: #92400e;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #0d9488, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'messages': [],
        'projects': [],
        'current_project': None,
        'generated_code': {},
        'templates': [],
        'user_preferences': {},
        'conversation_history': [],
        'app_count': 0,
        'authenticated': True,  # Always true for demo
        'theme': 'light',
        'api_keys_configured': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Sidebar
with st.sidebar:
    st.markdown("## 🏥 **AI App Builder**")
    st.markdown("---")
    
    # User info (simulated)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://ui-avatars.com/api/?name=Dr+Smith&background=0d9488&color=fff&size=100", width=50)
    with col2:
        st.markdown("**Dr. Smith**")
        st.markdown("Emergency Medicine")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📋 Menu")
    page = st.radio(
        "",
        ["💬 Chat Assistant", "🏗️ Project Builder", "⚡ Code Generator", "📊 Templates", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Projects", len(st.session_state.projects))
    with col2:
        st.metric("Messages", len(st.session_state.messages))
    
    st.markdown("---")
    
    # Recent projects
    if st.session_state.projects:
        st.markdown("### 📁 Recent Projects")
        for project in st.session_state.projects[-3:]:
            if st.button(f"📄 {project}", key=f"proj_{project}", use_container_width=True):
                st.session_state.current_project = project
                st.rerun()
    
    # New project button
    if st.button("➕ New Project", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_project = None
        st.session_state.generated_code = {}
        st.rerun()

# Main content area
if page == "💬 Chat Assistant":
    st.markdown('<h1 class="main-title">🤖 AI Healthcare Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Build your healthcare applications with AI guidance</p>', unsafe_allow_html=True)
    
    # Quick prompts
    st.markdown("### 🚀 Quick Start")
    cols = st.columns(5)
    prompts = [
        "Create patient intake form",
        "Build CME tracker",
        "Design dashboard",
        "Generate database schema",
        "Create API endpoints"
    ]
    
    for i, col in enumerate(cols):
        with col:
            if st.button(prompts[i], use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompts[i]})
                
                # Generate response based on prompt
                if "patient" in prompts[i].lower():
                    response = """I'll help you create a patient intake form. Here's a complete Streamlit implementation:

```python
import streamlit as st
import pandas as pd
from datetime import datetime

# Patient Intake Form
st.title("🏥 Patient Intake Form")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Patient Info", "Medical History", "Insurance"])

with tab1:
    with st.form("patient_info"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", min_value=datetime(1900,1,1))
        
        with col2:
            phone = st.text_input("Phone Number")
            email = st.text_input("Email")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        address = st.text_area("Address")
        
        if st.form_submit_button("Save Patient Info"):
            st.success(f"Patient {first_name} {last_name} registered successfully!")

with tab2:
    st.info("Medical history form will appear here")

with tab3:
    st.info("Insurance information form will appear here")

# Display recent patients
st.subheader("📋 Recent Patients")
sample_data = pd.DataFrame({
    'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
    'Date': ['2024-01-15', '2024-01-14', '2024-01-13'],
    'Status': ['Completed', 'In Progress', 'Completed']
})
st.dataframe(sample_data)
```"""
                elif "cme" in prompts[i].lower():
                    response = """Here's a CME tracker application:

```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# CME Credits Tracker
st.title("📚 CME Credits Tracker")

# Initialize session state for storing CME records
if 'cme_records' not in st.session_state:
    st.session_state.cme_records = [
        {
            'course': 'Advanced Cardiac Life Support',
            'provider': 'American Heart Association',
            'credits': 8.0,
            'date': '2024-01-15',
            'expiry': '2026-01-15',
            'status': 'Active'
        },
        {
            'course': 'Pediatric Advanced Life Support',
            'provider': 'American Academy of Pediatrics',
            'credits': 6.5,
            'date': '2023-11-20',
            'expiry': '2025-11-20',
            'status': 'Active'
        }
    ]

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Credits", "14.5", "+2.5")
with col2:
    st.metric("Active Courses", "2", "0")
with col3:
    st.metric("Expiring Soon", "1", "⚠️")
with col4:
    st.metric("Compliance", "85%", "+5%")

# Add new CME record
with st.expander("➕ Add New CME Record"):
    with st.form("new_cme"):
        col1, col2 = st.columns(2)
        with col1:
            course = st.text_input("Course Name")
            provider = st.text_input("Provider")
            credits = st.number_input("Credits", min_value=0.0, step=0.5)
        with col2:
            date = st.date_input("Completion Date")
            expiry = st.date_input("Expiry Date")
        
        if st.form_submit_button("Add Record"):
            st.session_state.cme_records.append({
                'course': course,
                'provider': provider,
                'credits': credits,
                'date': str(date),
                'expiry': str(expiry),
                'status': 'Active'
            })
            st.success("CME record added!")

# Display records
st.subheader("📋 Your CME Records")
if st.session_state.cme_records:
    df = pd.DataFrame(st.session_state.cme_records)
    st.dataframe(df, use_container_width=True)
    
    # Export option
    if st.button("📥 Export to CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"cme_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
```"""
                else:
                    response = f"I'll help you {prompts[i].lower()}. Here's a template to get started. Would you like me to add more specific features?"
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>AI Assistant:</strong> 
                </div>
                """, unsafe_allow_html=True)
                
                # Handle code blocks in response
                if "```python" in message["content"]:
                    parts = message["content"].split("```python")
                    st.markdown(parts[0])
                    if len(parts) > 1:
                        code_parts = parts[1].split("```")
                        if len(code_parts) > 0:
                            st.code(code_parts[0], language="python")
                            if len(code_parts) > 1:
                                st.markdown(code_parts[1])
                else:
                    st.markdown(message["content"])
    
    # Chat input
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Type your message...", key="chat_input", label_visibility="collapsed")
    with col2:
        send = st.button("📤 Send", use_container_width=True)
    
    if send and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Simulate AI response
        with st.spinner("AI is thinking..."):
            time.sleep(1)
            
            if "dashboard" in user_input.lower():
                response = """Here's a healthcare dashboard component:

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Healthcare Dashboard
st.title("🏥 Clinical Dashboard")

# Generate sample data
np.random.seed(42)
dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
patients = np.random.randint(20, 50, size=len(dates))
appointments = np.random.randint(15, 40, size=len(dates))

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", "1,234", "+123")
with col2:
    st.metric("Today's Appointments", "28", "+5")
with col3:
    st.metric("Wait Time", "12 min", "-3 min")
with col4:
    st.metric("Satisfaction", "94%", "+2%")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📅 Schedule", "👥 Patients"])

with tab1:
    # Patient volume chart
    df = pd.DataFrame({
        'Date': dates,
        'Patients': patients,
        'Appointments': appointments
    })
    
    fig = px.line(df, x='Date', y=['Patients', 'Appointments'], 
                  title='Daily Patient Volume')
    st.plotly_chart(fig, use_container_width=True)
    
    # Department distribution
    depts = ['Emergency', 'Cardiology', 'Pediatrics', 'Surgery', 'Orthopedics']
    counts = np.random.randint(50, 200, size=5)
    df_depts = pd.DataFrame({'Department': depts, 'Count': counts})
    
    fig2 = px.pie(df_depts, values='Count', names='Department', 
                  title='Patients by Department')
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.info("Schedule view coming soon...")

with tab3:
    st.info("Patient list coming soon...")
```"""
            else:
                response = "I understand. Could you provide more details about what you'd like to build? I can help with patient forms, CME tracking, dashboards, database schemas, and more."
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

elif page == "🏗️ Project Builder":
    st.markdown('<h1 class="main-title">🏗️ Project Builder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Configure and generate complete healthcare applications</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Project Configuration")
        
        # Project details
        project_name = st.text_input("Project Name", value="My Healthcare App")
        project_type = st.selectbox(
            "Project Type",
            ["Patient Management System", "CME Tracker", "Telemedicine Platform", 
             "Hospital Dashboard", "License Manager", "Job Board"]
        )
        
        st.markdown("### Select Features")
        features = st.multiselect(
            "",
            ["User Authentication", "Patient Records", "Appointment Scheduling",
             "CME Tracking", "License Management", "Analytics Dashboard",
             "Export/Reports", "Email Notifications", "PDF Generation"],
            default=["Patient Records", "Appointment Scheduling", "Analytics Dashboard"]
        )
        
        st.markdown("### Choose Tech Stack")
        tech_stack = st.multiselect(
            "",
            ["Streamlit", "FastAPI", "PostgreSQL", "MongoDB", "Plotly", 
             "Pandas", "SQLAlchemy", "Docker"],
            default=["Streamlit", "Pandas", "Plotly"]
        )
        
        if st.button("🚀 Generate Project", use_container_width=True):
            st.session_state.current_project = project_name
            if project_name not in st.session_state.projects:
                st.session_state.projects.append(project_name)
            
            # Generate project files
            st.session_state.generated_code = {
                "app.py": f'''"""Healthcare Application - {project_name}
Generated by AI App Builder
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib

# Page configuration
st.set_page_config(
    page_title="{project_name}",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d9488;
        text-align: center;
        margin-bottom: 2rem;
    }}
    .feature-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'patients' not in st.session_state:
    st.session_state.patients = []
if 'appointments' not in st.session_state:
    st.session_state.appointments = []

# Main app
def main():
    st.markdown('<h1 class="main-header">{project_name}</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Patients", "Appointments", "Reports", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Patients":
        show_patients()
    elif page == "Appointments":
        show_appointments()
    elif page == "Reports":
        show_reports()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.header("Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients", len(st.session_state.patients), "+5")
    with col2:
        st.metric("Appointments", len(st.session_state.appointments), "+2")
    with col3:
        st.metric("Today", "8", "-3")
    with col4:
        st.metric("Completion", "75%", "+5%")
    
    # Sample chart
    data = pd.DataFrame({{
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Patients': [45, 52, 48, 63, 58]
    }})
    fig = px.line(data, x='Month', y='Patients', title='Patient Volume')
    st.plotly_chart(fig, use_container_width=True)

def show_patients():
    st.header("Patient Records")
    
    # Add patient form
    with st.expander("➕ Add New Patient"):
        with st.form("new_patient"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                age = st.number_input("Age", 0, 120)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            with col2:
                phone = st.text_input("Phone")
                email = st.text_input("Email")
            
            if st.form_submit_button("Save Patient"):
                st.session_state.patients.append({{
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "email": email,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }})
                st.success("Patient added!")
    
    # Display patients
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)

def show_appointments():
    st.header("Appointments")
    st.info("Appointment management coming soon...")

def show_reports():
    st.header("Reports")
    st.info("Reports and analytics coming soon...")

def show_settings():
    st.header("Settings")
    st.info("Settings configuration coming soon...")

if __name__ == "__main__":
    main()''',
                "requirements.txt": """streamlit==1.28.0
pandas==2.0.3
plotly==5.17.0
numpy==1.24.3
python-dotenv==1.0.0""",
                "README.md": f"""# {project_name}

A healthcare application built with Streamlit.

## Features
{chr(10).join(['- ' + f for f in features])}

## Installation
```bash
pip install -r requirements.txt
streamlit run app.py
