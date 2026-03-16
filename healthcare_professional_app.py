import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from PIL import Image
import io
import base64
import time
import hashlib
import hmac

# Page configuration
st.set_page_config(
    page_title="Claude-Style App Builder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #0d9488 0%, #115e59 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #4b5563;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: all 0.3s;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
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
        animation: slideIn 0.3s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #0d9488 0%, #115e59 100%);
        color: white;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: #f3f4f6;
        color: #1f2937;
        margin-right: 20%;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Code block styling */
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
        background: linear-gradient(90deg, #0d9488 0%, #115e59 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 9999px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 15px -3px rgba(13,148,136,0.3);
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0d9488;
        margin-bottom: 1rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #0d9488 0%, #115e59 100%);
    }
    
    /* Metric styling */
    .metric-card {
        background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    
    /* Tool card styling */
    .tool-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .tool-card:hover {
        background: #f9fafb;
        border-color: #0d9488;
    }
    
    /* Status indicators */
    .status-online {
        color: #10b981;
        font-size: 0.8rem;
    }
    
    .status-offline {
        color: #ef4444;
        font-size: 0.8rem;
    }
    
    /* Divider styling */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #0d9488, transparent);
        margin: 2rem 0;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #0d9488;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = {}
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Simple authentication (replace with your own)
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

# Comment out authentication if not needed
# if not check_password():
#     st.stop()

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-header">🤖 AI App Builder</p>', unsafe_allow_html=True)
    
    # User profile section
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://ui-avatars.com/api/?name=User&background=0d9488&color=fff&size=100", width=50)
    with col2:
        st.markdown("**Welcome back!**")
        st.markdown('<span class="status-online">● Online</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    pages = ["Chat Assistant", "Project Builder", "Code Generator", "Analytics Dashboard", "Settings"]
    selected_page = st.radio("", pages, label_visibility="collapsed")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Recent projects
    st.markdown("### 📁 Recent Projects")
    if st.session_state.projects:
        for project in st.session_state.projects[-3:]:
            if st.button(f"📄 {project}", key=f"project_{project}", use_container_width=True):
                st.session_state.current_project = project
    else:
        st.info("No projects yet. Start a conversation to create one!")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_project = None
            st.rerun()
    with col2:
        if st.button("💾 Save", use_container_width=True):
            if st.session_state.current_project:
                st.success(f"Project '{st.session_state.current_project}' saved!")
            else:
                st.warning("No active project to save")
    
    # Stats
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Today's Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Messages", "24", "+12")
    with col2:
        st.metric("Tokens", "1.2k", "+450")
    with col3:
        st.metric("Projects", "3", "+1")

# Main content area
if selected_page == "Chat Assistant":
    # Header
    st.markdown('<h1 class="main-header">AI App Builder Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Build your healthcare platform with AI assistance</p>', unsafe_allow_html=True)
    
    # Quick prompts
    st.markdown("### 🚀 Quick Start Prompts")
    cols = st.columns(4)
    prompts = [
        "Create a healthcare dashboard",
        "Build a CME tracker",
        "Design a telemedicine UI",
        "Generate ATS CV template"
    ]
    for i, col in enumerate(cols):
        with col:
            if st.button(prompts[i], use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompts[i]})
                # Simulate AI response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Great! I'll help you {prompts[i].lower()}. Let me generate the code for you..."
                })
                st.rerun()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display messages
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
                    <strong>AI Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Code display if available
        if st.session_state.generated_code:
            with st.expander("📝 View Generated Code", expanded=True):
                for filename, code in st.session_state.generated_code.items():
                    st.markdown(f"**{filename}**")
                    st.code(code, language="python")
                    
                    # Download button
                    st.download_button(
                        label=f"📥 Download {filename}",
                        data=code,
                        file_name=filename,
                        mime="text/plain",
                        key=f"download_{filename}"
                    )
    
    # Chat input
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Type your message...", key="user_input", label_visibility="collapsed")
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Simulate AI thinking
        with st.spinner("AI is thinking..."):
            time.sleep(1.5)
            
            # Generate response based on input
            if "dashboard" in user_input.lower():
                response = """I'll create a healthcare dashboard for you. Here's the code:

```python
import streamlit as st
import pandas as pd
import plotly.express as px

# Healthcare Dashboard
st.title("🏥 Healthcare Analytics Dashboard")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Patients", "1,234", "+123")
with col2:
    st.metric("Appointments", "89", "+12")
with col3:
    st.metric("CME Credits", "456", "+45")
with col4:
    st.metric("Licenses", "3", "0")

# Patient demographics chart
data = pd.DataFrame({
    'Age Group': ['0-18', '19-35', '36-50', '51-65', '65+'],
    'Count': [150, 320, 280, 190, 110]
})
fig = px.bar(data, x='Age Group', y='Count', title='Patient Demographics')
st.plotly_chart(fig)
```"""
            elif "cme" in user_input.lower():
                response = """I'll build a CME tracker for you:

```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# CME Tracker
st.title("📚 CME Credits Tracker")

# Initialize session state
if 'cme_records' not in st.session_state:
    st.session_state.cme_records = []

# Add new CME record
with st.expander("➕ Add New CME Record"):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Course Title")
        provider = st.text_input("Provider")
        credits = st.number_input("Credits", min_value=0.0, step=0.5)
    with col2:
        date = st.date_input("Completion Date")
        expiry = st.date_input("Expiry Date")
    
    if st.button("Add Record"):
        st.session_state.cme_records.append({
            'title': title,
            'provider': provider,
            'credits': credits,
            'date': date,
            'expiry': expiry
        })
        st.success("Record added!")

# Display records
if st.session_state.cme_records:
    df = pd.DataFrame(st.session_state.cme_records)
    st.dataframe(df)
    
    # Summary metrics
    total_credits = df['credits'].sum()
    st.metric("Total CME Credits", total_credits)
```"""
            elif "telemedicine" in user_input.lower():
                response = """Here's a telemedicine UI component:

```python
import streamlit as st
import time

# Telemedicine Interface
st.title("📹 Telemedicine Consultation")

# Doctor info
col1, col2, col3 = st.columns([1,2,1])
with col1:
    st.image("https://via.placeholder.com/150", caption="Dr. Smith")
with col2:
    st.markdown("### Dr. Sarah Johnson")
    st.markdown("Cardiologist • Available Now")
with col3:
    if st.button("📞 Start Call"):
        st.info("Connecting...")

# Consultation controls
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.button("🎥 Camera")
with col2:
    st.button("🎤 Mic")
with col3:
    st.button("📋 Notes")
with col4:
    st.button("💊 Prescribe")
with col5:
    st.button("📊 Share Screen")

# Patient info
with st.expander("Patient Information"):
    st.markdown("**Name:** John Doe")
    st.markdown("**Age:** 45")
    st.markdown("**Chief Complaint:** Chest pain")
    st.markdown("**Vitals:** BP 120/80, HR 72")
```"""
            else:
                response = "I understand you want to build a healthcare application. Could you provide more details about what specific features you need?"
            
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

elif selected_page == "Project Builder":
    st.markdown('<h1 class="main-header">📱 Project Builder</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Project Configuration")
        
        # Project details
        project_name = st.text_input("Project Name", value=st.session_state.current_project or "Healthcare App")
        project_type = st.selectbox(
            "Project Type",
            ["Healthcare Dashboard", "CME Tracker", "Telemedicine Platform", "License Management", "Job Board"]
        )
        
        st.markdown("### Features")
        features = st.multiselect(
            "Select Features",
            ["User Authentication", "Database Integration", "Analytics", "File Upload", "Email Notifications", "Payment Processing"],
            default=["User Authentication", "Database Integration"]
        )
        
        st.markdown("### Tech Stack")
        tech_stack = st.multiselect(
            "Choose Technologies",
            ["Streamlit", "FastAPI", "Supabase", "PostgreSQL", "Plotly", "Pandas", "OpenCV"],
            default=["Streamlit", "Supabase", "Pandas"]
        )
        
        if st.button("🚀 Generate Project", use_container_width=True):
            st.session_state.current_project = project_name
            if project_name not in st.session_state.projects:
                st.session_state.projects.append(project_name)
            
            # Generate project files
            st.session_state.generated_code = {
                "app.py": f"""# {project_name}
import streamlit as st
import pandas as pd
from supabase import create_client
import plotly.express as px

# Initialize Supabase
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

st.title("{project_name}")

# Your generated code here...
""",
                "requirements.txt": """streamlit==1.28.0
pandas==2.0.3
plotly==5.17.0
supabase==1.2.0
python-dotenv==1.0.0""",
                "README.md": f"""# {project_name}

A healthcare application built with AI assistance.

## Features
{chr(10).join(['- ' + f for f in features])}

## Tech Stack
{chr(10).join(['- ' + t for t in tech_stack])}

## Installation
```bash
pip install -r requirements.txt
streamlit run app.py
```"""
            }
            
            st.success(f"Project '{project_name}' generated successfully!")
    
    with col2:
        st.markdown("### Project Preview")
        
        if st.session_state.current_project:
            st.markdown(f"**Current Project:** {st.session_state.current_project}")
            st.markdown(f"**Type:** {project_type}")
            st.markdown(f"**Features:** {', '.join(features) if features else 'None'}")
            
            # Progress indicator
            st.markdown("### Development Progress")
            progress = len(features) * 10
            st.progress(min(progress, 100) / 100)
            
            # Next steps
            st.markdown("### Next Steps")
            steps = [
                "✅ Configure Supabase database",
                "⬜ Set up authentication",
                "⬜ Create database tables",
                "⬜ Build user interface",
                "⬜ Implement analytics"
            ]
            for step in steps:
                st.markdown(step)
        else:
            st.info("Configure and generate a project to see preview")

elif selected_page == "Code Generator":
    st.markdown('<h1 class="main-header">⚡ Code Generator</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Generate Code")
        
        code_type = st.selectbox(
            "Code Type",
            ["Streamlit App", "Supabase Integration", "Database Schema", "API Endpoints", "Authentication", "Data Visualization"]
        )
        
        description = st.text_area(
            "Describe what you want to build",
            height=150,
            placeholder="Example: Create a patient intake form with name, age, symptoms, and store in Supabase"
        )
        
        if st.button("🔨 Generate Code", use_container_width=True):
            with st.spinner("Generating code..."):
                time.sleep(2)
                
                if code_type == "Streamlit App":
                    code = """import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="Healthcare App", page_icon="🏥")

# Title
st.title("Patient Intake Form")

# Form
with st.form("patient_intake"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    with col2:
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        visit_date = st.date_input("Visit Date", datetime.now())
    
    symptoms = st.text_area("Chief Complaint / Symptoms")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        # Save to database
        st.success(f"Patient {name} registered successfully!")
        
        # Display summary
        st.subheader("Patient Summary")
        st.json({
            "name": name,
            "age": age,
            "gender": gender,
            "phone": phone,
            "email": email,
            "visit_date": str(visit_date),
            "symptoms": symptoms
        })"""
                
                elif code_type == "Supabase Integration":
                    code = """from supabase import create_client
import streamlit as st

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# CRUD Operations
def create_patient(data):
    """Create a new patient record"""
    result = supabase.table("patients").insert(data).execute()
    return result.data

def get_patient(patient_id):
    """Get patient by ID"""
    result = supabase.table("patients").select("*").eq("id", patient_id).execute()
    return result.data[0] if result.data else None

def get_all_patients():
    """Get all patients"""
    result = supabase.table("patients").select("*").execute()
    return result.data

def update_patient(patient_id, updates):
    """Update patient record"""
    result = supabase.table("patients").update(updates).eq("id", patient_id).execute()
    return result.data

def delete_patient(patient_id):
    """Delete patient record"""
    result = supabase.table("patients").delete().eq("id", patient_id).execute()
    return result.data

# Example usage in Streamlit
def main():
    st.title("Patient Management System")
    
    # Create form
    with st.form("new_patient"):
        name = st.text_input("Name")
        age = st.number_input("Age")
        if st.form_submit_button("Save"):
            data = {"name": name, "age": age}
            result = create_patient(data)
            st.success(f"Patient {name} created with ID: {result[0]['id']}")
    
    # Display patients
    patients = get_all_patients()
    if patients:
        st.dataframe(patients)

if __name__ == "__main__":
    main()"""
                
                elif code_type == "Database Schema":
                    code = """-- Healthcare Database Schema for Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Patients table
CREATE TABLE patients (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT,
    phone TEXT,
    email TEXT UNIQUE,
    address TEXT,
    emergency_contact TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Medical Records table
CREATE TABLE medical_records (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    record_date DATE DEFAULT NOW(),
    diagnosis TEXT,
    treatment TEXT,
    notes TEXT,
    physician TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appointments table
CREATE TABLE appointments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    appointment_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status TEXT DEFAULT 'scheduled',
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- CME Credits table
CREATE TABLE cme_credits (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    physician_id UUID REFERENCES auth.users(id),
    course_name TEXT NOT NULL,
    provider TEXT,
    credits DECIMAL(5,2),
    completion_date DATE,
    expiry_date DATE,
    certificate_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Licenses table
CREATE TABLE licenses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    physician_id UUID REFERENCES auth.users(id),
    license_number TEXT,
    jurisdiction TEXT,
    issue_date DATE,
    expiry_date DATE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE cme_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own patients" ON patients 
    FOR SELECT USING (auth.uid() = physician_id);

CREATE POLICY "Users can insert patients" ON patients 
    FOR INSERT WITH CHECK (auth.uid() = physician_id);

-- Create indexes
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);
"""
                
                st.session_state.generated_code = {"generated_code.py": code}
                st.rerun()
    
    with col2:
        st.markdown("### Templates")
        templates = {
            "🏥 Patient Intake": "Form with patient registration",
            "📊 Analytics Dashboard": "Healthcare metrics visualization",
            "📅 Appointment Scheduler": "Calendar and booking system",
            "💊 Prescription Manager": "Medication tracking",
            "📚 CME Tracker": "Education credits manager"
        }
        
        for template, desc in templates.items():
            with st.container():
                st.markdown(f"""
                <div class="tool-card">
                    <strong>{template}</strong>
                    <p style="color: #6b7280; font-size: 0.9rem;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Use Template", key=f"template_{template}"):
                    st.info(f"Loading {template} template...")

elif selected_page == "Analytics Dashboard":
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Generate sample data
    np.random.seed(42)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #6b7280; font-size: 0.9rem;">Total Users</h3>
            <p style="font-size: 2rem; font-weight: bold; color: #0d9488;">1,234</p>
            <p style="color: #10b981;">↑ 12.3%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #6b7280; font-size: 0.9rem;">Active Projects</h3>
            <p style="font-size: 2rem; font-weight: bold; color: #0d9488;">45</p>
            <p style="color: #10b981;">↑ 8.1%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #6b7280; font-size: 0.9rem;">Code Generations</h3>
            <p style="font-size: 2rem; font-weight: bold; color: #0d9488;">892</p>
            <p style="color: #ef4444;">↓ 2.4%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #6b7280; font-size: 0.9rem;">Success Rate</h3>
            <p style="font-size: 2rem; font-weight: bold; color: #0d9488;">94%</p>
            <p style="color: #10b981;">↑ 5.2%</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Usage Over Time")
        # Generate sample time series data
        dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
        values = np.random.randint(50, 150, size=len(dates))
        df = pd.DataFrame({'Date': dates, 'Usage': values})
        
        fig = px.line(df, x='Date', y='Usage', title='Daily Active Users')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Project Types")
        # Generate sample pie chart data
        project_types = ['Healthcare Dashboard', 'CME Tracker', 'Telemedicine', 'License Manager', 'Job Board']
        counts = np.random.randint(10, 50, size=len(project_types))
        df_pie = pd.DataFrame({'Type': project_types, 'Count': counts})
        
        fig = px.pie(df_pie, values='Count', names='Type', title='Projects by Type')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("### Recent Activity")
    
    activity_data = {
        'Time': ['2 min ago', '15 min ago', '1 hour ago', '3 hours ago', '5 hours ago'],
        'User': ['john@example.com', 'sarah@hospital.com', 'mike@clinic.org', 'emma@health.org', 'david@med.com'],
        'Action': ['Generated CME Tracker', 'Created Dashboard', 'Uploaded Schema', 'Built API', 'Deployed App'],
        'Status': ['✅ Success', '✅ Success', '⚠️ Warning', '✅ Success', '❌ Failed']
    }
    
    df_activity = pd.DataFrame(activity_data)
    st.dataframe(df_activity, use_container_width=True)

elif selected_page == "Settings":
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Profile Settings")
        
        with st.form("profile_settings"):
            name = st.text_input("Display Name", value="Dr. Sarah Johnson")
            email = st.text_input("Email", value="sarah@healthcare.com")
            specialty = st.selectbox("Specialty", ["Emergency Medicine", "Cardiology", "Pediatrics", "Surgery", "Internal Medicine"])
            
            st.markdown("### Preferences")
            theme = st.selectbox("Theme", ["Light", "Dark", "System"])
            language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
            
            if st.form_submit_button("Save Settings"):
                st.success("Settings saved successfully!")
    
    with col2:
        st.markdown("### API Configuration")
        
        with st.form("api_settings"):
            st.text_input("Supabase URL", value="https://your-project.supabase.co", type="default")
            st.text_input("Supabase Anon Key", value="••••••••••••••••", type="password")
            st.text_input("OpenAI API Key", value="", type="password")
            
            st.markdown("### Model Preferences")
            model = st.selectbox("Default Model", ["GPT-4", "Claude-3", "Gemini Pro", "Llama 3"])
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
            max_tokens = st.number_input("Max Tokens", 100, 4000, 2000)
            
            if st.form_submit_button("Update API Settings"):
                st.success("API settings updated!")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Danger zone
    st.markdown("### ⚠️ Danger Zone")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear All Projects", use_container_width=True):
            st.session_state.projects = []
            st.session_state.current_project = None
            st.warning("All projects cleared!")
    
    with col2:
        if st.button("🔄 Reset Settings", use_container_width=True):
            st.info("Settings reset to default")
    
    with col3:
        if st.button("📤 Export Data", use_container_width=True):
            # Create export data
            export_data = {
                "projects": st.session_state.projects,
                "messages": st.session_state.messages,
                "timestamp": str(datetime.now())
            }
            
            # Convert to JSON
            json_str = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="📥 Download Export",
                data=json_str,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <p>Built with ❤️ for healthcare professionals</p>
        <p style="font-size: 0.8rem;">© 2024 AI App Builder | Powered by Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
