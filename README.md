# 🧬 MedPharma-AI: Open-Source Clinical Decision Support & Pharmacovigilance Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenFDA API](https://img.shields.io/badge/Data-OpenFDA-green.svg)](https://open.fda.gov/)

**MedPharma-AI** is an open-source computational pharmacology and clinical decision support research framework. It bridges official regulatory drug databases (**OpenFDA**) with Large Language Models (OpenAI, Google Gemini, and GitHub Models) to mitigate hallucination in biomedical text analysis, adverse drug event (ADE) triage, and multi-drug synergy research.

## ✨ Key Features
- **Grounded OpenFDA Integration:** Real-time retrieval of FDA drug labels, boxed warnings, contraindications, and mechanisms of action.
- **Clinical Case & EHR Triage:** Parses unstructured clinical notes and lab PDFs to stratify renal/hepatic risk factors and map evidence-based therapeutic classes.
- **Drug-Drug Interaction (DDI) & Repurposing Engine:** Evaluates pharmacokinetic conflicts (e.g., CYP450 pathways) and explores multi-target mechanistic synergy for drug repurposing hypotheses.
- **Multi-Provider LLM Agnostic:** Natively supports OpenAI API, Google Gemini (`v1beta/openai`), and GitHub Models.

## 🚀 Quickstart

```bash
git clone https://github.com/farshadlight/MedPharma-AI.git
cd MedPharma-AI
pip install -r requirements.txt
streamlit run app.py
```

## ⚠️ Medical Disclaimer
This software is strictly for academic research, pharmacovigilance study, and educational exploration. It is not a certified medical device and must never be used for direct patient diagnosis or unsupervised medication changes.
