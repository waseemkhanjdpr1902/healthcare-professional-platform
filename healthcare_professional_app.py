import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO
import docx

# ────────────────────────────────────────────────
# Page config & styling
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="MedPro Hub",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3.2rem;
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin: 1rem 0 2rem;
    }
    .card {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .metric {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 1.4rem;
        border-radius: 12px;
        text-align: center;
    }
    .stButton > button {
        background: #1e40af !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.4rem !important;
    }
    .stButton > button:hover {
        background: #1e3a8a !important;
    }
    hr { margin: 2rem 0; border-color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Session state initialization
# ────────────────────────────────────────────────
if "cme" not in st.session_state:
    st.session_state.cme = pd.DataFrame(columns=["Date", "Activity", "Credits", "Notes"])

if "cv" not in st.session_state:
    st.session_state.cv = {
        "name": "", "title": "", "email": "", "phone": "", "linkedin": "",
        "summary": "", "experience": [], "education": [], "skills": []
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────────────────────────
# Sidebar – Navigation & xAI key
# ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#1e40af; text-align:center;'>🩺 MedPro Hub</h2>", unsafe_allow_html=True)
    st.caption("Professional tools for healthcare workers")

    xai_key = st.text_input("xAI API Key (optional)", type="password", help="For AI Career Advisor")
    client = None
    if xai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1")
        except:
            st.error("Invalid xAI key format")

    page = st.radio(
        "Navigate",
        ["🏠 Home", "📊 CME Tracker", "📝 CV Builder", "🔍 ATS Checker", "🤖 AI Advisor"]
    )

# ────────────────────────────────────────────────
# Home
# ────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">MedPro Hub</h1>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="metric"><h3>CME</h3><h2>{:.1f}</h2><p>credits tracked</p></div>'.format(st.session_state.cme["Credits"].sum() if not st.session_state.cme.empty else 0), unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="metric"><h3>ATS</h3><h2>—</h2><p>not checked</p></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown('<div class="metric"><h3>Grok</h3><h2>{}</h2><p>advisor ready</p></div>'.format("✅" if client else "🔒"), unsafe_allow_html=True)

    st.markdown("### Quick actions")
    c1, c2, c3, c4 = st.columns(4)
    c1.button("Log CME", use_container_width=True)
    c2.button("Build CV", use_container_width=True)
    c3.button("Check ATS", use_container_width=True)
    c4.button("Ask Grok", use_container_width=True)

# ────────────────────────────────────────────────
# CME Tracker
# ────────────────────────────────────────────────
elif page == "📊 CME Tracker":
    st.header("CME Credits Tracker")

    with st.form("cme_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1.2])
        with col1:
            activity = st.text_input("Activity / Course / Conference")
        with col2:
            credits = st.number_input("Credits", min_value=0.0, max_value=50.0, step=0.25)

        notes = st.text_area("Notes / Provider", height=80)

        submitted = st.form_submit_button("Log Activity", type="primary", use_container_width=True)

    if submitted and activity.strip():
        new_row = pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Activity": [activity],
            "Credits": [credits],
            "Notes": [notes]
        })
        st.session_state.cme = pd.concat([st.session_state.cme, new_row], ignore_index=True)
        st.success("Activity logged!")

    if not st.session_state.cme.empty:
        total = st.session_state.cme["Credits"].sum()
        st.metric("Total CME Credits", f"{total:.1f}")

        fig = px.bar(
            st.session_state.cme,
            x="Date",
            y="Credits",
            title="Credits earned over time",
            color_discrete_sequence=["#3b82f6"]
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(st.session_state.cme.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────
# CV Builder + Download
# ────────────────────────────────────────────────
elif page == "📝 CV Builder":
    st.header("ATS-friendly CV Builder")

    with st.form("cv_form"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        st.session_state.cv["name"] = col1.text_input("Full Name", value=st.session_state.cv["name"])
        st.session_state.cv["title"] = col2.text_input("Title / Specialty", value=st.session_state.cv["title"])

        col1, col2, col3 = st.columns(3)
        st.session_state.cv["email"] = col1.text_input("Email", value=st.session_state.cv["email"])
        st.session_state.cv["phone"] = col2.text_input("Phone", value=st.session_state.cv["phone"])
        st.session_state.cv["linkedin"] = col3.text_input("LinkedIn", value=st.session_state.cv["linkedin"])

        st.subheader("Professional Summary")
        st.session_state.cv["summary"] = st.text_area(
            "Summary (include keywords: patient care, EMR, ICU, ACLS, ...)",
            value=st.session_state.cv["summary"],
            height=140
        )

        if st.form_submit_button("Save & Download CV", type="primary"):
            doc = docx.Document()
            doc.add_heading(st.session_state.cv["name"], 0)
            doc.add_paragraph(st.session_state.cv["title"])
            doc.add_paragraph(f"{st.session_state.cv['email']}  •  {st.session_state.cv['phone']}  •  {st.session_state.cv['linkedin']}")
            doc.add_paragraph(st.session_state.cv["summary"])

            bio = BytesIO()
            doc.save(bio)
            bio.seek(0)

            st.download_button(
                label="Download Word (.docx)",
                data=bio,
                file_name=f"{st.session_state.cv['name'].replace(' ', '_')}_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# ────────────────────────────────────────────────
# ATS Checker (simple keyword match)
# ────────────────────────────────────────────────
elif page == "🔍 ATS Checker":
    st.header("ATS Score Checker")

    cv_file = st.file_uploader("Upload your CV (PDF or TXT)", type=["pdf", "txt"])
    job_desc = st.text_area("Paste job description or keywords", height=160)

    if st.button("Check ATS Score", type="primary") and cv_file and job_desc:
        if cv_file.type == "application/pdf":
            reader = PdfReader(cv_file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            text = cv_file.getvalue().decode("utf-8", errors="ignore")

        keywords = [w.lower().strip() for w in job_desc.split() if len(w) > 3]
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        score = round(100 * matches / len(keywords), 1) if keywords else 0

        st.metric("ATS Compatibility Score", f"{score}%")

        if score >= 80:
            st.success("Excellent match – very ATS friendly!")
        elif score >= 60:
            st.warning("Good base – add more keywords from the job description")
        else:
            st.error("Needs improvement – include more job-specific terms")

        missing = [kw for kw in set(keywords) if kw not in text_lower][:8]
        if missing:
            st.info("Some missing keywords:  " + " • ".join(missing))

# ────────────────────────────────────────────────
# AI Advisor (Grok)
# ────────────────────────────────────────────────
elif page == "🤖 AI Advisor":
    st.header("Grok-powered Career Advisor")

    if not client:
        st.warning("Please add your xAI API key in the sidebar to use the advisor.")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask anything about your career, CV, specialty switch, interviews…"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Grok is thinking…"):
                    try:
                        response = client.chat.completions.create(
                            model="grok-beta",
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            temperature=0.7,
                            max_tokens=900
                        )
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"API error: {str(e)}")

st.markdown("---")
st.caption("MedPro Hub • Streamlit • Local session storage • March 2026")
