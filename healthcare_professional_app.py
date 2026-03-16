import streamlit as st
from supabase import create_client, Client
import openai
from PyPDF2 import PdfReader
import docx
from io import BytesIO
import pandas as pd
from datetime import datetime
import plotly.express as px

# ────────────────────────────────────────────────
# PAGE CONFIG & CSS (professional medical look)
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="MedPro Hub",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 3rem; background: linear-gradient(90deg, #2563eb, #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; text-align: center; }
    .card { background: white; padding: 1.8rem; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(135deg, #2563eb, #0ea5e9); color: white; padding: 1.5rem; border-radius: 12px; text-align: center; }
    .stButton > button { background: #2563eb !important; color: white !important; border-radius: 10px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# SUPABASE CLIENT (no cache → fixes serialization error)
# ────────────────────────────────────────────────
if "supabase" not in st.session_state:
import streamlit as st
from supabase import create_client, Client

# ────────────────────────────────────────────────
# Load Supabase credentials with fallback & clear errors
# ────────────────────────────────────────────────
def get_supabase_client() -> Client | None:
    """
    Loads Supabase URL & key from secrets.
    Supports both nested [connections.supabase] and flat format.
    """
    # Option 1: nested format (official Streamlit + Supabase docs style)
    try:
        supabase_section = st.secrets["connections"]["supabase"]
        url = supabase_section["https://sspruywktrnvyccsbadk.supabase.co"]
        key = supabase_section["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNzcHJ1eXdrdHJudnljY3NiYWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0Mzk1MjMsImV4cCI6MjA4ODAxNTUyM30.zqXBks-EIcONnzU-NxhqliOy3c6t0IGIckn5wFQ43AU"]
    except (KeyError, TypeError):
        # Option 2: flat keys (very common when people copy-paste wrong)
        try:
            url = st.secrets["https://sspruywktrnvyccsbadk.supabase.co"]
            key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNzcHJ1eXdrdHJudnljY3NiYWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0Mzk1MjMsImV4cCI6MjA4ODAxNTUyM30.zqXBks-EIcONnzU-NxhqliOy3c6t0IGIckn5wFQ43AU"]
        except KeyError:
            url = None
            key = None

    if not url or not key:
        st.error("""
        **Supabase credentials missing or misconfigured.**
        
        Please go to your Streamlit app → Manage app → Settings → Secrets  
        and add one of the following formats:
        
        **Preferred (nested):**
        ```toml
        [connections.supabase]
        SUPABASE_URL = "https://sspruywktrnvyccsbadk.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNzcHJ1eXdrdHJudnljY3NiYWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0Mzk1MjMsImV4cCI6MjA4ODAxNTUyM30.zqXBks-EIcONnzU-NxhqliOy3c6t0IGIckn5wFQ43AU"
