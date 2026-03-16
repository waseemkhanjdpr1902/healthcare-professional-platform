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
    url: str = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key: str = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    st.session_state.supabase = create_client(url, key)

supabase: Client = st.session_state.supabase

# ────────────────────────────────────────────────
# SESSION STATE
# ────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ────────────────────────────────────────────────
# SIDEBAR – Login / Navigation
# ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#2563eb;'>🩺 MedPro Hub</h2>", unsafe_allow_html=True)
    st.caption("Tools for Healthcare Professionals")

    if st.session_state.user:
        st.success(f"Signed in as {st.session_state.user.email}")
        if st.button("Sign Out"):
            st.session_state.user = None
            st.rerun()

        xai_key = st.text_input("xAI Grok API Key", type="password")
        client = openai.OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1") if xai_key else None

        st.session_state.page = st.radio("Go to", ["Home", "CME Tracker", "CV Builder", "ATS Checker", "AI Advisor"])
    else:
        st.info("Sign in to continue")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if res.user:
                        st.session_state.user = res.user
                        st.rerun()
                    else:
                        st.error("Login failed")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        with col2:
            if st.button("Sign Up"):
                try:
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Check your email to confirm account")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if not st.session_state.user:
    st.stop()

user_id = st.session_state.user.id

# ────────────────────────────────────────────────
# PAGES
# ────────────────────────────────────────────────
if st.session_state.page == "Home":
    st.markdown('<h1 class="main-header">MedPro Hub</h1>', unsafe_allow_html=True)
    st.markdown("Your professional platform for CME tracking, ATS CVs & career guidance")
    cols = st.columns(3)
    cols[0].markdown('<div class="metric-card"><h3>CME Credits</h3><h2>Track progress</h2></div>', unsafe_allow_html=True)
    cols[1].markdown('<div class="metric-card"><h3>ATS Score</h3><h2>Optimize CV</h2></div>', unsafe_allow_html=True)
    cols[2].markdown('<div class="metric-card"><h3>AI Advisor</h3><h2>Powered by Grok</h2></div>', unsafe_allow_html=True)

elif st.session_state.page == "CME Tracker":
    st.header("CME Credits Tracker")

    with st.form("cme"):
        act = st.text_input("Activity / Course")
        cred = st.number_input("Credits", min_value=0.0, step=0.25)
        notes = st.text_area("Notes")
        if st.form_submit_button("Log", type="primary"):
            if act.strip():
                supabase.table("cme_logs").insert({
                    "user_id": user_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "activity": act,
                    "credits": cred,
                    "notes": notes
                }).execute()
                st.success("Logged!")
                st.rerun()

    resp = supabase.table("cme_logs").select("*").eq("user_id", user_id).execute()
    if resp.data:
        df = pd.DataFrame(resp.data)
        total = df["credits"].sum()
        st.metric("Total CME Credits", f"{total:.1f}")
        fig = px.bar(df, x="date", y="credits", title="Credits Over Time")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.sort_values("date", ascending=False))

elif st.session_state.page == "CV Builder":
    st.header("ATS CV Builder")
    st.info("Form + preview + Word download – expand from your previous version")

    # Add your CV form logic here (name, experience, summary, etc.)
    # On submit → supabase.table("user_cvs").upsert({"user_id": user_id, "cv_data": your_dict}).execute()

elif st.session_state.page == "ATS Checker":
    st.header("ATS Score Checker")
    st.info("Upload CV + job desc → keyword match gauge – add from previous code")

elif st.session_state.page == "AI Advisor":
    st.header("Grok AI Career Advisor")
    if client:
        prompt = st.chat_input("Ask career advice...")
        if prompt:
            st.chat_message("user").markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        res = client.chat.completions.create(
                            model="grok-beta",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        st.markdown(res.choices[0].message.content)
                    except Exception as e:
                        st.error(str(e))
    else:
        st.warning("Add xAI API key in sidebar")

st.caption("MedPro Hub • Streamlit + Supabase • 2026")
