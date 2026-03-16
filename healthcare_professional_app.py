import streamlit as st
import openai
from PyPDF2 import PdfReader
import docx
from io import BytesIO
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MedPro Hub", page_icon="🩺", layout="wide")
st.title("🩺 MedPro Hub – Healthcare Professional Platform")
st.markdown("**CME Tracker • ATS CV Builder • ATS Score Checker • AI Career Advisor**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Settings")
    xai_api_key = st.text_input("xAI Grok API Key", type="password", help="Get it from https://console.x.ai")
    if xai_api_key:
        client = openai.OpenAI(api_key=xai_api_key, base_url="https://api.x.ai/v1")
    else:
        client = None
        st.warning("Enter your xAI API key to unlock AI Career Advisory")

    page = st.radio("Navigate", 
                    ["🏠 Home", 
                     "📊 CME/ATS Tracker", 
                     "📝 ATS CV Builder", 
                     "🔍 ATS Score Checker", 
                     "🤖 AI Career Advisory"])

# ====================== SESSION STATE ======================
if "cme_data" not in st.session_state:
    st.session_state.cme_data = pd.DataFrame(columns=["Date", "Activity", "Credits", "Notes"])
if "cv_data" not in st.session_state:
    st.session_state.cv_data = {
        "name": "", "title": "", "email": "", "phone": "", "linkedin": "",
        "summary": "", "experience": [], "education": [], "skills": [], "certifications": []
    }

# ====================== HOME ======================
if page == "🏠 Home":
    st.image("https://picsum.photos/1200/400?random=medical", use_column_width=True)
    st.markdown("""
    Welcome to **MedPro Hub** – your all-in-one platform for healthcare professionals.  
    Track CME credits, build ATS-friendly CVs, check ATS scores, and get AI-powered career advice from Grok.
    """)
    st.success("Built for doctors, nurses, pharmacists, therapists & allied health professionals.")

# ====================== CME/ATS TRACKER ======================
elif page == "📊 CME/ATS Tracker":
    st.header("CME Credits & ATS Activity Tracker")
    
    col1, col2 = st.columns([3,1])
    with col1:
        activity = st.text_input("Activity / Conference / Course")
        credits = st.number_input("CME Credits", min_value=0.0, step=0.5)
        notes = st.text_area("Notes (optional)")
        if st.button("Log Activity"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Activity": activity,
                "Credits": credits,
                "Notes": notes
            }])
            st.session_state.cme_data = pd.concat([st.session_state.cme_data, new_row], ignore_index=True)
            st.success("Logged!")
    
    st.subheader("Your Log")
    if not st.session_state.cme_data.empty:
        st.dataframe(st.session_state.cme_data, use_container_width=True)
        total_credits = st.session_state.cme_data["Credits"].sum()
        st.metric("Total CME Credits", f"{total_credits:.1f}")
        
        # Download
        csv = st.session_state.cme_data.to_csv(index=False).encode()
        st.download_button("Download Tracker CSV", csv, "cme_tracker.csv", "text/csv")
    else:
        st.info("No activities logged yet.")

# ====================== ATS CV BUILDER ======================
elif page == "📝 ATS CV Builder":
    st.header("ATS-Optimized CV Builder")
    
    with st.form("cv_form"):
        st.subheader("Personal Info")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=st.session_state.cv_data["name"])
            title = st.text_input("Professional Title (e.g., Cardiologist)", value=st.session_state.cv_data["title"])
        with col2:
            email = st.text_input("Email", value=st.session_state.cv_data["email"])
            phone = st.text_input("Phone", value=st.session_state.cv_data["phone"])
        
        linkedin = st.text_input("LinkedIn / Profile URL", value=st.session_state.cv_data["linkedin"])
        summary = st.text_area("Professional Summary (use keywords: patient care, EMR, ICU, etc.)", value=st.session_state.cv_data["summary"], height=150)
        
        st.subheader("Experience (add as many as you want)")
        exp_count = st.number_input("Number of Experiences", min_value=1, max_value=10, value=len(st.session_state.cv_data["experience"]) or 1)
        experiences = []
        for i in range(exp_count):
            with st.expander(f"Experience {i+1}"):
                company = st.text_input(f"Organization {i+1}", key=f"comp{i}")
                role = st.text_input(f"Role {i+1}", key=f"role{i}")
                dates = st.text_input(f"Dates {i+1} (e.g., Jan 2022 – Present)", key=f"dates{i}")
                desc = st.text_area(f"Description {i+1} (use bullet points & keywords)", key=f"desc{i}", height=100)
                experiences.append({"company": company, "role": role, "dates": dates, "desc": desc})
        
        st.subheader("Education & Skills")
        edu = st.text_area("Education (one per line)")
        skills = st.text_input("Skills (comma separated)", value=",".join(st.session_state.cv_data["skills"]))
        certs = st.text_input("Certifications (comma separated)")
        
        submitted = st.form_submit_button("Save & Generate CV")
    
    if submitted:
        st.session_state.cv_data = {
            "name": name, "title": title, "email": email, "phone": phone, "linkedin": linkedin,
            "summary": summary, "experience": experiences,
            "education": edu.split("\n") if edu else [],
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "certifications": [c.strip() for c in certs.split(",") if c.strip()]
        }
        st.success("CV saved!")

    # Generate downloadable Word CV
    if st.session_state.cv_data["name"]:
        doc = docx.Document()
        doc.add_heading(st.session_state.cv_data["name"], 0)
        doc.add_paragraph(st.session_state.cv_data["title"])
        doc.add_paragraph(f"{st.session_state.cv_data['email']} | {st.session_state.cv_data['phone']} | {st.session_state.cv_data['linkedin']}")
        doc.add_heading("Professional Summary", level=1)
        doc.add_paragraph(st.session_state.cv_data["summary"])
        
        doc.add_heading("Experience", level=1)
        for exp in st.session_state.cv_data["experience"]:
            if exp["role"]:
                p = doc.add_paragraph()
                p.add_run(f"{exp['role']} at {exp['company']}").bold = True
                p.add_run(f" – {exp['dates']}")
                for line in exp["desc"].split("\n"):
                    if line.strip():
                        doc.add_paragraph(line.strip(), style="List Bullet")
        
        doc.add_heading("Education", level=1)
        for e in st.session_state.cv_data["education"]:
            if e.strip(): doc.add_paragraph(e)
        
        doc.add_heading("Skills", level=1)
        doc.add_paragraph(", ".join(st.session_state.cv_data["skills"]))
        
        doc.add_heading("Certifications", level=1)
        doc.add_paragraph(", ".join(st.session_state.cv_data["certifications"]))
        
        bio = BytesIO()
        doc.save(bio)
        st.download_button("Download CV as Word (.docx)", bio.getvalue(), 
                           f"{st.session_state.cv_data['name'].replace(' ','_')}_ATS_CV.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ====================== ATS SCORE CHECKER ======================
elif page == "🔍 ATS Score Checker":
    st.header("ATS Score Checker")
    
    cv_file = st.file_uploader("Upload CV (PDF or TXT)", type=["pdf", "txt"])
    job_desc = st.text_area("Paste Job Description / Keywords (or target role)", height=200,
                            placeholder="e.g., 'Board-certified emergency physician, EMR, ACLS, patient care, ICU, 5+ years experience...'")
    
    if st.button("Check ATS Score") and cv_file and job_desc:
        # Extract text
        if cv_file.type == "application/pdf":
            reader = PdfReader(cv_file)
            text = "".join(page.extract_text() or "" for page in reader.pages)
        else:
            text = cv_file.getvalue().decode()
        
        # Simple but effective keyword scoring
        keywords = [k.lower().strip() for k in job_desc.split() if len(k) > 3]
        text_lower = text.lower()
        matches = sum(1 for k in keywords if k in text_lower)
        score = round((matches / len(keywords) * 100), 1) if keywords else 0
        
        st.subheader(f"ATS Compatibility Score: **{score}%**")
        if score >= 80:
            st.success("Excellent! Your CV is highly ATS-friendly.")
        elif score >= 60:
            st.warning("Good – needs minor optimization.")
        else:
            st.error("Needs improvement.")
        
        st.info("**Top missing keywords:** " + ", ".join([k for k in keywords if k not in text_lower][:10]))

# ====================== AI CAREER ADVISORY ======================
elif page == "🤖 AI Career Advisory":
    st.header("AI Career Advisor (Powered by Grok)")
    
    if not client:
        st.error("Please enter your xAI API key in the sidebar.")
    else:
        st.write("Tell me about your career:")
        experience = st.text_area("Current role, years of experience, specialty")
        goals = st.text_area("Career goals (e.g., move to telemedicine, leadership role, research)")
        challenges = st.text_area("Challenges you're facing (optional)")
        
        if st.button("Get Personalized Advice"):
            with st.spinner("Consulting Grok..."):
                try:
                    response = client.chat.completions.create(
                        model="grok-4-20-beta",   # ← Latest flagship as of March 2026 (check docs.x.ai for exact ID)
                        messages=[
                            {"role": "system", "content": "You are an expert career advisor for healthcare professionals (doctors, nurses, pharmacists, etc.). Give honest, actionable, step-by-step advice."},
                            {"role": "user", "content": f"Current situation: {experience}\nGoals: {goals}\nChallenges: {challenges}\nProvide detailed career advice, next steps, and ATS/CV tips."}
                        ],
                        temperature=0.7,
                        max_tokens=1200
                    )
                    advice = response.choices[0].message.content
                    st.markdown(advice)
                except Exception as e:
                    st.error(f"API error: {e}")

st.caption("MedPro Hub • Built with ❤️ for healthcare heroes • Streamlit + xAI Grok")