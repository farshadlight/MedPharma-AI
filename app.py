import os
import json
import requests
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

st.set_page_config(
    page_title="MedPharma-AI | Clinical & Pharmacovigilance Decision Support",
    page_icon="🧬",
    layout="wide"
)

def fetch_fda_drug_info(drug_name: str) -> dict:
    """Fetch structured drug label metadata from the official OpenFDA API."""
    url = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{drug_name}"+openfda.brand_name:"{drug_name}"&limit=1'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()["results"][0]
            return {
                "indications": data.get("indications_and_usage", ["Not specified"])[0][:1500],
                "warnings": data.get("warnings", data.get("boxed_warning", ["Not specified"]))[0][:1500],
                "interactions": data.get("drug_interactions", ["Not specified"])[0][:1500],
                "adverse_reactions": data.get("adverse_reactions", ["Not specified"])[0][:1500],
                "mechanism": data.get("mechanism_of_action", ["Not specified"])[0][:1500],
            }
    except Exception:
        pass
    return {}

with st.sidebar:
    st.title("🧬 MedPharma-AI Config")
    api_source = st.selectbox(
        "AI Inference Provider:",
        [
            "Google Gemini API (OpenAI-Compatible)",
            "GitHub Models (Free via GitHub PAT)",
            "OpenAI Official API",
            "OpenRouter (Free Tier Models)"
        ]
    )

    if api_source == "Google Gemini API (OpenAI-Compatible)":
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        default_model = "gemini-2.5-flash"
        st.caption("🔑 Get a free API key from aistudio.google.com")
    elif api_source == "GitHub Models (Free via GitHub PAT)":
        base_url = "https://models.inference.ai.azure.com"
        default_model = "gpt-4o-mini"
        st.caption("🔑 Use your GitHub Personal Access Token (PAT)")
    elif api_source == "OpenAI Official API":
        base_url = "https://api.openai.com/v1"
        default_model = "gpt-4o-mini"
        st.caption("🔑 Use your OpenAI Platform API Key")
    else:
        base_url = "https://openrouter.ai/api/v1"
        default_model = "meta-llama/llama-3.3-70b-instruct:free"
        st.caption("🔑 Get a free key from openrouter.ai")

    api_key = st.text_input("API Key / Token:", type="password")
    model_name = st.text_input("Model Identifier:", value=default_model)
    st.divider()
    st.caption("⚠️ For clinical research and pharmacovigilance study only. Not a substitute for medical advice.")

st.title("🔬 MedPharma-AI: Open-Source Pharmacovigilance & Clinical Triage")

tab1, tab2, tab3 = st.tabs([
    "📋 1. Clinical Case & EHR Analysis",
    "💊 2. OpenFDA Drug Profiling & Risk-Benefit",
    "🧪 3. Drug-Drug Interaction & Synergy Research"
])

def run_inference(system_prompt: str, user_prompt: str):
    if not api_key:
        st.error("Please enter your API Key or Token in the sidebar.")
        return
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        with st.spinner("Running biomedical inference..."):
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"API Error: {e}")

with tab1:
    st.subheader("Electronic Health Record (EHR) & Case Triage")
    uploaded_pdf = st.file_uploader("Upload Patient Lab Report / Case History (PDF/TXT):", type=["pdf", "txt"])
    clinical_notes = st.text_area(
        "Clinical Notes, Symptoms, Comorbidities, and Biomarkers:",
        height=140,
        placeholder="e.g., 58yo male with T2DM and hypertension, presenting with joint pain and eGFR 42 mL/min..."
    )
    if st.button("🔍 Analyze Case & Therapeutic Classes", key="btn_case"):
        extracted_text = ""
        if uploaded_pdf:
            if uploaded_pdf.name.endswith(".pdf"):
                reader = PdfReader(uploaded_pdf)
                extracted_text = "\n".join([p.extract_text() or "" for p in reader.pages])
            else:
                extracted_text = uploaded_pdf.read().decode("utf-8", errors="ignore")
        sys_prompt = (
            "You are a clinical pharmacology research assistant. Analyze the provided case history and respond (in Persian or English matching user input) with:\n"
            "1. Clinical risk stratification and organ function considerations (renal/hepatic).\n"
            "2. Evidence-based first-line and second-line therapeutic drug classes.\n"
            "3. Contraindicated drug classes based on comorbidities.\n"
            "4. Standard clinical disclaimer."
        )
        run_inference(sys_prompt, f"Notes:\n{clinical_notes}\n\nAttached Document:\n{extracted_text[:8000]}")

with tab2:
    st.subheader("Pharmacological Classification & OpenFDA Adverse Event Profiling")
    drug_query = st.text_input("Generic Drug Name (English):", placeholder="e.g., Metformin, Atorvastatin, Lisinopril")
    if st.button("📊 Fetch OpenFDA Data & Analyze", key="btn_fda"):
        fda_data = fetch_fda_drug_info(drug_query)
        if fda_data:
            st.success(f"Verified OpenFDA label retrieved for {drug_query}.")
            with st.expander("View Raw OpenFDA JSON"):
                st.json(fda_data)
        sys_prompt = (
            "You are an expert pharmacologist. Using the provided OpenFDA label data, provide a structured analysis in Persian:\n"
            "- Pharmacological Class & Mechanism of Action\n"
            "- Primary Approved Indications & Evidence-Based Off-Label Uses\n"
            "- Contraindications, Adverse Reactions, and Boxed Warnings\n"
            "- Risk-Benefit Ratio across patient subpopulations"
        )
        run_inference(sys_prompt, f"Drug: {drug_query}\nOpenFDA Data:\n{json.dumps(fda_data, ensure_ascii=False)}")

with tab3:
    st.subheader("Multi-Drug Interaction, Synergy & Drug Repurposing Hypothesis")
    col1, col2 = st.columns(2)
    with col1:
        drugs_list = st.text_input("Candidate Drugs (comma-separated):", placeholder="e.g., Lisinopril, Hydrochlorothiazide")
    with col2:
        target_disease = st.text_input("Target Condition / Disease:", placeholder="e.g., Resistant Hypertension")
    if st.button("🧪 Evaluate Interaction & Repurposing Synergy", key="btn_synergy"):
        sys_prompt = (
            "You are a senior researcher in computational pharmacology and drug repurposing. Analyze the drug combination for the target disease in Persian:\n"
            "1. Severe Drug-Drug Interactions (DDIs) and pharmacokinetic conflicts (CYP450, renal clearance).\n"
            "2. Mechanistic Synergy (whether pathways complement each other as a fixed-dose or combination therapy).\n"
            "3. Drug Repurposing Hypothesis based on signaling pathways.\n"
            "4. Explicit scientific caveat that de-novo chemical synthesis requires wet-lab validation and clinical trials."
        )
        run_inference(sys_prompt, f"Drugs: {drugs_list}\nTarget Condition: {target_disease}")
