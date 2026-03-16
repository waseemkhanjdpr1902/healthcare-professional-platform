import streamlit as st
import openai
from PyPDF2 import PdfReader
import docx
from io import BytesIO
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ────────────────────────────────────────────────
# CONFIG & PAGE SETUP
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="MedPro Hub – Professional Tools",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
# THEME & CUSTOM CSS (modern medical look)
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --teal: #0ea5e9;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--gray-100);
    }

    .stApp > header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--teal) 100%) !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--gray-800);
        font-weight: 600;
    }

    .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 500 !important;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37,99,235,0.25) !important;
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 1.6rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid var(--gray-200);
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.1);
    }

    .metric {
        background: linear-gradient(135deg, var(--primary) 0%, var(--teal) 100%);
        color: white;
        padding: 1.4rem;
        border-radius: 12px;
        text-align: center;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid var(--gray-200);
        border-bottom: none;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }

    hr {
        margin: 2rem 0;
        border-color: var(--gray-200);
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/stethoscope.png", width=80)
    st.title("MedPro Hub")
    st.caption("Professional toolkit for healthcare professionals")

    api_key = st.text_input("xAI Grok API Key", type="password", help="Required for AI Career Advisor")

    if api_key:
        client = openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    else:
        client = None
        st.info("Enter API key to unlock AI Advisor")

    page = st.radio(
        "Main Navigation",
        options=[
            "🏠 Dashboard",
            "📊 CME Tracker",
            "📝 CV Builder",
            "🔍 ATS Checker",
            "🧠 Career Advisor"
        ]
    )

# ────────────────────────────────────────────────
# SESSION STATE INIT
# ────────────────────────────────────────────────
if "cme" not in st.session_state:
    st.session_state.cme = pd.DataFrame(columns=["Date", "Activity", "Credits", "Notes"])

if "cv" not in st.session_state:
    st.session_state.cv = {
        "name": "", "title": "", "contact": "", "summary": "",
        "experience": [], "education": [], "skills": "", "certs": ""
    }

if "chat" not in st.session_state:
    st.session_state.chat = []

# ────────────────────────────────────────────────
# PAGE: HOME / DASHBOARD
# ────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.title("Welcome to MedPro Hub")
    st.markdown("Your professional companion for career growth in healthcare")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric"><h3>CME</h3><h2>{:.1f}</h2><p>credits tracked</p></div>'.format(st.session_state.cme["Credits"].sum()), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric"><h3>ATS</h3><h2>—</h2><p>score not checked yet</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric"><h3>Grok</h3><h2>4.20</h2><p>AI Advisor ready</p></div>', unsafe_allow_html=True)

    st.markdown("### Quick Actions")
    cols = st.columns(4)
    cols[0].button("➕ Log CME", use_container_width=True)
    cols[1].button("📄 Build CV", use_container_width=True)
    cols[2].button("🔎 Check ATS", use_container_width=True)
    cols[3].button("💡 Ask Grok", use_container_width=True)

# ────────────────────────────────────────────────
# PAGE: CME TRACKER
# ────────────────────────────────────────────────
elif page == "📊 CME Tracker":
    st.header("CME Credits Tracker")

    with st.form("cme_form"):
        col1, col2 = st.columns([3,1])
        with col1:
            act = st.text_input("Activity / Course / Conference")
        with col2:
            cred = st.number_input("Credits", min_value=0.0, max_value=50.0, step=0.25)

        notes = st.text_area("Notes / Provider", height=80)

        submitted = st.form_submit_button("Log Activity", type="primary", use_container_width=True)

    if submitted and act.strip():
        new_row = pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Activity": [act],
            "Credits": [cred],
            "Notes": [notes]
        })
        st.session_state.cme = pd.concat([st.session_state.cme, new_row], ignore_index=True)
        st.success("Activity logged successfully!")

    if not st.session_state.cme.empty:
        total = st.session_state.cme["Credits"].sum()

        st.metric("Total CME Credits", f"{total:.1f}", delta_color="normal")

        fig = px.bar(
            st.session_state.cme,
            x="Date", y="Credits",
            title="Credits Earned Over Time",
            color_discrete_sequence=["#2563eb"]
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(st.session_state.cme.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────
# PAGE: CV BUILDER
# ────────────────────────────────────────────────
elif page == "📝 CV Builder":
    st.header("ATS-Friendly CV Builder")

    left, right = st.columns([1, 1.3])

    with left:
        with st.form("cv_builder"):
            st.subheader("Personal Information")
            name = st.text_input("Full Name", value=st.session_state.cv["name"])
            title = st.text_input("Current / Desired Title", value=st.session_state.cv["title"])
            contact = st.text_input("Email • Phone • LinkedIn", value=st.session_state.cv["contact"])

            st.subheader("Professional Summary")
            summary = st.text_area("Summary (keyword rich, 4–6 lines)", value=st.session_state.cv["summary"], height=140)

            st.subheader("Experience")
            exp_count = st.number_input("Number of positions", 1, 10, len(st.session_state.cv["experience"]) or 3)
            experiences = []
            for i in range(int(exp_count)):
                with st.expander(f"Position {i+1}"):
                    role = st.text_input("Role", key=f"r{i}")
                    org = st.text_input("Organization", key=f"o{i}")
                    period = st.text_input("Period (e.g. Jan 2022 – Present)", key=f"p{i}")
                    bullets = st.text_area("Key responsibilities & achievements (one per line)", key=f"b{i}", height=120)
                    experiences.append({"role":role, "org":org, "period":period, "bullets":bullets})

            if st.form_submit_button("Save & Preview", type="primary"):
                st.session_state.cv.update({
                    "name":name, "title":title, "contact":contact,
                    "summary":summary, "experience":experiences
                })
                st.success("CV data saved!")

    with right:
        st.subheader("Live Preview")
        if st.session_state.cv["name"]:
            st.markdown(f"""
            <div class="card">
                <h1 style="text-align:center; margin-bottom:0.2rem;">{st.session_state.cv['name']}</h1>
                <p style="text-align:center; color:var(--primary); font-size:1.25rem; margin:0.4rem 0;">
                    {st.session_state.cv['title']}
                </p>
                <p style="text-align:center; color:var(--gray-700); font-size:0.95rem;">
                    {st.session_state.cv['contact']}
                </p>
                <hr>
                <h3>Professional Summary</h3>
                <p>{st.session_state.cv['summary'] or '—'}</p>

                <h3>Professional Experience</h3>
            """, unsafe_allow_html=True)

            for exp in st.session_state.cv["experience"]:
                if exp["role"].strip():
                    st.markdown(f"""
                    **{exp['role']}**  
                    {exp['org']}  •  {exp['period']}
                    """)
                    for line in exp["bullets"].split("\n"):
                        line = line.strip()
                        if line:
                            st.markdown(f"• {line}")

            st.markdown("</div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# PAGE: ATS CHECKER
# ────────────────────────────────────────────────
elif page == "🔍 ATS Checker":
    st.header("ATS Score & Keyword Analyzer")

    cv_file = st.file_uploader("Upload CV (PDF or plain text)", type=["pdf", "txt"])
    jd = st.text_area("Job Description / Target Keywords", height=180)

    if st.button("Analyze ATS Match", type="primary") and cv_file and jd:
        if cv_file.type == "application/pdf":
            reader = PdfReader(cv_file)
            text = " ".join(p.extract_text() or "" for p in reader.pages)
        else:
            text = cv_file.getvalue().decode("utf-8", errors="ignore")

        words = [w.lower().strip(".,;()[]{}") for w in jd.split() if len(w) > 3]
        unique_kws = list(set(words))
        found = sum(1 for kw in unique_kws if kw in text.lower())
        score = round(100 * found / len(unique_kws), 1) if unique_kws else 0

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ATS Compatibility"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "royalblue"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))

        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

        if score >= 85:
            st.success(f"**Excellent match** — {score}%")
        elif score >= 65:
            st.warning(f"**Good base** — {score}% (optimize more keywords)")
        else:
            st.error(f"**Needs improvement** — {score}%")

        missing = [kw for kw in unique_kws if kw not in text.lower()][:12]
        if missing:
            st.info("Top missing keywords:  " + " • ".join(missing))

# ────────────────────────────────────────────────
# PAGE: CAREER ADVISOR
# ────────────────────────────────────────────────
elif page == "🧠 Career Advisor":
    st.header("Grok-powered Career Advisor")

    if not client:
        st.error("Please add your xAI API key in the sidebar")
    else:
        for msg in st.session_state.chat:
            role = "assistant" if msg["role"] == "assistant" else "user"
            with st.chat_message(role):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ask about career moves, CV tips, specialty change, interviews…")

        if prompt:
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Grok is thinking…"):
                    try:
                        resp = client.chat.completions.create(
                            model="grok-beta",
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat],
                            temperature=0.7,
                            max_tokens=1100
                        )
                        answer = resp.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.chat.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"API error → {str(e)}")

st.markdown("---")
st.caption("MedPro Hub  •  Built for healthcare professionals  •  March 2026")
