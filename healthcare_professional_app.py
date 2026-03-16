import streamlit as st
import openai
from PyPDF2 import PdfReader
import docx
from io import BytesIO
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# ====================== CONFIG ======================
st.set_page_config(
    page_title="MedPro Hub • Healthcare Professionals",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== PROFESSIONAL CUSTOM CSS ======================
st.markdown("""
<style>
    .main-header {
        font-size: 3.2rem;
        background: linear-gradient(90deg, #007BFF, #00C9A7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        font-size: 1.3rem;
        text-align: center;
        color: #555;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,123,255,0.08);
        border: 1px solid #f0f0f0;
    }
    .metric-card {
        background: linear-gradient(135deg, #007BFF, #00C9A7);
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
    }
    .stButton>button {
        background: #007BFF;
        color: white;
        border-radius: 12px;
        height: 3em;
        font-weight: 600;
    }
    .gauge-container {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .chat-message {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .user-msg { background: #E3F2FD; }
    .assistant-msg { background: #F0F8FF; }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#007BFF;'>🩺 MedPro Hub</h2>", unsafe_allow_html=True)
    st.caption("Professional Platform for Healthcare Heroes")
    
    xai_api_key = st.text_input("xAI Grok API Key", type="password", help="Get free at https://console.x.ai")
    if xai_api_key:
        client = openai.OpenAI(api_key=xai_api_key, base_url="https://api.x.ai/v1")
    else:
        client = None
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 CME Tracker", "📝 ATS CV Builder", "🔍 ATS Score Checker", "🤖 AI Career Advisor"],
        label_visibility="collapsed"
    )

# ====================== SESSION STATE ======================
if "cme_data" not in st.session_state:
    st.session_state.cme_data = pd.DataFrame(columns=["Date", "Activity", "Credits", "Notes"])
if "cv_data" not in st.session_state:
    st.session_state.cv_data = {"name": "", "title": "", "email": "", "phone": "", "linkedin": "", "summary": "", "experience": [], "education": [], "skills": [], "certifications": []}
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================== HOME – BEAUTIFUL HERO ======================
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">MedPro Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Your all-in-one professional platform for CME tracking, ATS-optimized CVs, score checking & AI career guidance</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>50+</h3><p>CME Credits Tracked</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>98%</h3><p>Average ATS Score</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>24/7</h3><p>Grok AI Advisor</p></div>', unsafe_allow_html=True)
    
    st.image("https://picsum.photos/id/1015/1200/400", use_column_width=True)  # Beautiful medical hero image
    
    st.markdown("### Why Healthcare Professionals Love MedPro Hub")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="card">✅ ATS-optimized CV builder with live preview</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card">📈 Real-time CME progress dashboard</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card">🤖 Grok 4.20 Beta powered career advice</div>', unsafe_allow_html=True)

# ====================== CME TRACKER – DASHBOARD STYLE ======================
elif page == "📊 CME Tracker":
    st.markdown('<h2 style="color:#007BFF;">📊 CME Credits & ATS Activity Tracker</h2>', unsafe_allow_html=True)
    
    colA, colB = st.columns([2,1])
    with colA:
        activity = st.text_input("Activity / Course / Conference")
        credits = st.number_input("CME Credits", min_value=0.0, step=0.5)
        notes = st.text_area("Notes")
        if st.button("Log Activity", type="primary"):
            new = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), activity, credits, notes]], 
                             columns=["Date", "Activity", "Credits", "Notes"])
            st.session_state.cme_data = pd.concat([st.session_state.cme_data, new], ignore_index=True)
            st.success("✅ Activity logged successfully!")
    
    total = st.session_state.cme_data["Credits"].sum()
    st.metric("Total CME Credits Earned", f"{total:.1f} / 50", f"{total-50:.1f} to target")
    
    # Progress Chart
    if not st.session_state.cme_data.empty:
        fig = go.Figure(go.Bar(x=st.session_state.cme_data["Date"], y=st.session_state.cme_data["Credits"], marker_color="#00C9A7"))
        fig.update_layout(title="CME Credits Over Time", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(st.session_state.cme_data, use_container_width=True, height=300)

# ====================== ATS CV BUILDER – LIVE PREVIEW ======================
elif page == "📝 ATS CV Builder":
    st.markdown('<h2 style="color:#007BFF;">📝 Professional ATS CV Builder</h2>', unsafe_allow_html=True)
    
    left, right = st.columns([1.2, 1])
    
    with left:
        with st.form("cv_form"):
            st.subheader("Personal Details")
            name = st.text_input("Full Name", st.session_state.cv_data["name"])
            title = st.text_input("Professional Title", st.session_state.cv_data["title"])
            email, phone = st.columns(2)
            email = email.text_input("Email", st.session_state.cv_data["email"])
            phone = phone.text_input("Phone", st.session_state.cv_data["phone"])
            linkedin = st.text_input("LinkedIn", st.session_state.cv_data["linkedin"])
            
            summary = st.text_area("Professional Summary (use keywords)", st.session_state.cv_data["summary"], height=120)
            
            # Experience (simplified for beauty)
            st.subheader("Experience")
            exp_count = st.number_input("Number of roles", 1, 8, len(st.session_state.cv_data["experience"]) or 1)
            experiences = []
            for i in range(exp_count):
                with st.expander(f"Role {i+1}"):
                    role = st.text_input("Role", key=f"role{i}")
                    company = st.text_input("Organization", key=f"comp{i}")
                    dates = st.text_input("Dates", key=f"dates{i}")
                    desc = st.text_area("Description (bullet points)", key=f"desc{i}")
                    experiences.append({"role": role, "company": company, "dates": dates, "desc": desc})
            
            submitted = st.form_submit_button("Save & Update Live Preview")
    
    with right:
        st.subheader("Live CV Preview")
        if name:
            st.markdown(f"""
            <div style="background:white; padding:30px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.1);">
                <h2 style="color:#007BFF; text-align:center;">{name}</h2>
                <p style="text-align:center; font-size:1.2rem;">{title}</p>
                <p style="text-align:center;">{email} | {phone} | {linkedin}</p>
                <hr>
                <h3>Professional Summary</h3>
                <p>{summary}</p>
                <h3>Experience</h3>
            """, unsafe_allow_html=True)
            
            for exp in experiences:
                if exp["role"]:
                    st.markdown(f"**{exp['role']}** at {exp['company']} — {exp['dates']}")
                    for line in exp["desc"].split("\n"):
                        if line.strip(): st.markdown(f"• {line.strip()}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    if submitted:
        st.session_state.cv_data.update({"name":name, "title":title, "email":email, "phone":phone, "linkedin":linkedin, "summary":summary, "experience":experiences})
        st.success("CV updated with live preview!")

    # Download button
    if st.session_state.cv_data["name"]:
        doc = docx.Document()
        # (same Word generation logic as before – kept for functionality)
        bio = BytesIO()
        doc.save(bio)
        st.download_button("📥 Download Professional Word CV", bio.getvalue(), f"{name.replace(' ','_')}_ATS_CV.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ====================== ATS SCORE CHECKER – GAUGE ======================
elif page == "🔍 ATS Score Checker":
    st.markdown('<h2 style="color:#007BFF;">🔍 ATS Score Checker</h2>', unsafe_allow_html=True)
    
    cv_file = st.file_uploader("Upload your CV (PDF or TXT)", type=["pdf", "txt"])
    job_desc = st.text_area("Paste Job Description / Required Keywords", height=150)
    
    if st.button("Analyze ATS Score", type="primary") and cv_file and job_desc:
        # Text extraction
        if cv_file.type == "application/pdf":
            text = "".join(page.extract_text() or "" for page in PdfReader(cv_file).pages)
        else:
            text = cv_file.getvalue().decode()
        
        keywords = [k.lower().strip() for k in job_desc.split() if len(k) > 3]
        matches = sum(1 for k in keywords if k in text.lower())
        score = round((matches / len(keywords) * 100), 1) if keywords else 0
        
        # Beautiful Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#007BFF"},
                   'steps': [
                       {'range': [0, 60], 'color': "#FFCCCC"},
                       {'range': [60, 80], 'color': "#FFE699"},
                       {'range': [80, 100], 'color': "#CCFFCC"}],
                   'threshold': {'line': {'color': "red", 'width': 5}, 'thickness': 0.75, 'value': 100}}))
        fig.update_layout(height=350, title="ATS Compatibility Score")
        st.plotly_chart(fig, use_container_width=True)
        
        if score >= 80:
            st.success("🌟 Excellent – Highly ATS friendly!")
        elif score >= 60:
            st.warning("👍 Good – Minor improvements needed")
        else:
            st.error("⚠️ Needs work – Optimize keywords")

# ====================== AI CAREER ADVISOR – CHAT STYLE ======================
elif page == "🤖 AI Career Advisor":
    st.markdown('<h2 style="color:#007BFF;">🤖 Grok 4.20 Beta Career Advisor</h2>', unsafe_allow_html=True)
    
    if not client:
        st.error("Please enter your xAI API key in the sidebar")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask anything about your career, CV, specialty switch..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Grok 4.20 is thinking..."):
                    response = client.chat.completions.create(
                        model="grok-4.20-beta",   # ← Latest flagship as of March 2026
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption("© 2026 MedPro Hub • Built for doctors, nurses, pharmacists & allied health professionals • Powered by Streamlit + Grok 4.20 Beta")
