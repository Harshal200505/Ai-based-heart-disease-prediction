import streamlit as st
import pandas as pd
import ollama
from fpdf import FPDF
from datetime import datetime
import io
import re

# ============================================
# PAGE CONFIG & SETUP
# ============================================
st.set_page_config(
    page_title="Heart Disease Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# PROFESSIONAL CUSTOM CSS & STYLING
# ============================================
# ============================================
# MODERN CLINICAL GLASS-THEME CSS
# ============================================
st.markdown("""
    <style>
    /* Importing Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;600;800&display=swap');

    :root {
        --clinical-red: #FF3B3F;
        --deep-navy: #0B132B;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --neon-accent: #00F5FF;
    }

    /* Background Theme Adjustment */
    .stApp {
        background-color: #050A18;
    }

    /* THE MAIN TITLE - High Contrast & Stylish */
    .main-title {
        font-family: 'Playfair Display', serif;
        background: linear-gradient(to right, #FFFFFF, #FF3B3F, #A4161A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -2px;
        filter: drop-shadow(0px 10px 10px rgba(0,0,0,0.5));
    }

    /* SUBTITLE STYLE */
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #6B7280;
        text-align: center;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 0.9rem;
        margin-bottom: 40px;
    }

    /* SECTION HEADERS - Bold & Clean */
    .section-header {
        font-family: 'Inter', sans-serif;
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        border-bottom: 2px solid var(--clinical-red);
        padding-bottom: 8px;
        margin-top: 30px;
    }

    /* GLASS CARD FOR AI ADVICE */
    .ai-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 6px solid var(--neon-accent);
        padding: 30px;
        border-radius: 20px;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        line-height: 1.8;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }

    /* ENHANCED PREDICT BUTTON */
    .stButton > button {
        background: linear-gradient(135deg, #FF3B3F 0%, #A4161A 100%) !important;
        font-family: 'Inter', sans-serif;
        color: white !important;
        border: none !important;
        padding: 20px !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 10px 20px rgba(255, 59, 63, 0.3) !important;
    }

    .stButton > button:hover {
        transform: scale(1.02) translateY(-3px) !important;
        box-shadow: 0 15px 30px rgba(255, 59, 63, 0.5) !important;
    }

    /* SIDEBAR GLASS LOOK */
    [data-testid="stSidebar"] {
        background: #0B132B !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* METRIC FONT BOLDING */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 900 !important;
        color: white !important;
    }

    </style>
""", unsafe_allow_html=True)

# ============================================
# PDF GENERATION (ENCODING FIXED)
# ============================================
def create_professional_pdf(patient_name, age, sex, risk, ai_advice, clinical_data):
    pdf = FPDF()
    pdf.add_page()
    
    def clean(text):
        if not text: return ""
        return re.sub(r'[^\x00-\xff]', '', str(text))
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(230, 57, 70)
    pdf.cell(0, 15, "HEART DISEASE MEDICAL REPORT", ln=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Patient: {clean(patient_name)} /n| Age: {age} /n| Risk: {risk}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Clinical Metrics:", ln=True)
    pdf.set_font("Arial", '', 10)
    for k, v in clinical_data.items():
        pdf.cell(0, 6, f"- {k.upper()}: {v}", ln=True)
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AI Recommendations:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, clean(ai_advice))
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/833/833472.png", width=100)
    st.markdown('<div class="section-header">👤 Patient Profile</div>', unsafe_allow_html=True)
    patient_name = st.text_input("Full Name", value="", placeholder="Enter name")
    
    age = st.slider("Age", 20, 80, 45)
    sex_choice = st.selectbox("Gender", ["Male", "Female"])
    sex = 1 if sex_choice == "Male" else 0
    
    st.markdown('<div class="section-header">🏥 Clinical Data</div>', unsafe_allow_html=True)
    cp = st.selectbox("Chest Pain Type", [0, 1, 2, 3])
    trestbps = st.number_input("Blood Pressure", 60, 200, 120)
    chol = st.number_input("Cholesterol", 40, 400, 200)
    thalach = st.number_input("Max Heart Rate", 60, 220, 150)
    
    with st.expander("🔬 Advanced Metrics"):
        fbs = st.selectbox("Fasting Sugar > 120", [0, 1])
        restecg = st.selectbox("ECG Results", [0, 1, 2])
        exang = st.selectbox("Exercise Angina", [0, 1])
        oldpeak = st.number_input("ST Depression", 0.0, 6.0, 0.0)
        slope = st.selectbox("ST Slope", [0, 1, 2])
        ca = st.selectbox("Blocked Vessels", [0, 1, 2, 3])
        thal = st.selectbox("Thalassemia", [1, 2, 3])

clinical_data_dict = {'BP': str(trestbps), 'CHOL': str(chol), 'HR': str(thalach), 'ST': str(oldpeak)}
input_df = pd.DataFrame([[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]], 
                        columns=["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"])

# ============================================
# MAIN UI
# ============================================
st.markdown("<h1 class='main-title'>HEART DISEASE PREDICTOR</h1>", unsafe_allow_html=True)

from groq import Groq

def get_ai_advice(data, risk_level, name):
    try:
        # Get a free key at https://console.groq.com/
        client = Groq(api_key=st.secrets["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"]) 
        
        prompt = f"Act as Cardiologist. Patient {name}, Risk {risk_level}, Data {data.to_dict()}. Provide 3 concise advice points."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"



if st.button("🔥 GENERATE CLINICAL REPORT", use_container_width=True):
    if not patient_name.strip():
        st.error("⚠️ Please enter Patient Full Name in the sidebar.")
    else:
        # Score calculation
        score = 0
        risk_factors = []
        if chol > 180: score += 3; risk_factors.append("High Cholesterol")
        if trestbps > 140: score += 2; risk_factors.append("Elevated Blood Pressure")
        if oldpeak > 2.0: score += 4; risk_factors.append("High ST Depression")
        
        risk = "LOW" if score <= 4 else "HIGH"
        risk_css = "success" if risk == "LOW" else "danger"
        
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            st.markdown(f"<div class='section-header'>📋 Assessment for {patient_name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='risk-{risk_css}'><div class='risk-label'>{risk} RISK</div>"
                        f"<p style='color:white;'>Risk Score: <strong>{score}/15</strong></p></div>", unsafe_allow_html=True)
            
            st.markdown("### Identified Risk Factors:")
            if risk_factors:
                for f in risk_factors: st.markdown(f"**• {f}**")
            else: st.success("✅ No major risks")
            
            st.divider()
            
            # Vital Metrics Summary
            st.markdown("### Vital Metrics Summary:")
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric("Blood Pressure", f"{int(trestbps)} ...", delta="Normal" if trestbps <= 140 else "High", delta_color="normal" if trestbps <= 140 else "inverse")
                st.metric("Cholesterol", f"{int(chol)} ...", delta="High" if chol > 180 else "Normal", delta_color="inverse" if chol > 180 else "normal")
            with m_col2:
                st.metric("Heart Rate", f"{int(thalach)} b...", delta="Avg")
                st.metric("ST Depression", f"{oldpeak}", delta="Indicator")

        with col_right:
            st.markdown(f"<div class='section-header'>🤖 AI Clinical Advice</div>", unsafe_allow_html=True)
            with st.spinner("Analyzing..."):
                ai_result = get_ai_advice(input_df, risk, patient_name)
            
            st.markdown(f"<div class='ai-box'>{ai_result}</div>", unsafe_allow_html=True)
            
            try:
                pdf_bytes = create_professional_pdf(patient_name, age, sex_choice, risk, ai_result, clinical_data_dict)
                st.download_button("📥 Download Report", data=pdf_bytes, file_name=f"{patient_name}_Report.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"PDF Error: {str(e)}")
