# 🏦 Banking Complaint Triage System

An enterprise-grade, NLP-powered application designed to automatically classify, prioritize, route, and risk-score customer complaints for banking operations. Built with Python, Streamlit, and Scikit-Learn, this system simulates an end-to-end triage pipeline to reduce manual routing inefficiencies and prevent SLA violations.

---

## 📑 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Technical Architecture](#-technical-architecture)
4. [Project Structure](#-project-structure)
5. [Installation & Setup](#-installation--setup)
6. [Usage Guide](#-usage-guide)
7. [Model Details](#-model-details)
8. [Future Enhancements](#-future-enhancements)
9. [License](#-license)

---

## 📖 Overview

Banks receive thousands of customer complaints daily. Sorting these manually creates severe operational friction, delays investigations, and increases the risk of regulatory SLA violations. 

This project demonstrates how Natural Language Processing (NLP) and Machine Learning can automate complaint intake. Trained on patterns from over 3.6 million Consumer Financial Protection Bureau (CFPB) records, the system categorizes complaints into 6 major banking domains, predicts urgency based on strict keyword heuristics, and routes cases to specific operational departments while calculating a dynamic risk score.

---

## ✨ Key Features

* **🔍 Single Complaint Triage:** Instantly analyze individual customer narratives. Extracts predicted categories, urgency levels, risk scores, and optimal department routing in real-time.
* **📊 Batch Processing & Analytics:** Upload a CSV of complaints to process thousands of records simultaneously. Automatically generates an interactive analytics dashboard with Plotly visualizations.
* **🏢 Intelligent Routing:** Maps the combination of predicted product categories and urgency levels to specialized departments (e.g., *Fraud & Identity Protection*, *Legal & Collections Team*).
* **🎯 Dynamic Risk & Reliability Scoring:** Calculates a composite operational risk score (0-100) based on urgency severity and ML model confidence. Flags short or ambiguous complaints for manual review.
* **📋 Priority Queueing:** Automatically isolates `Critical` and `High` urgency complaints, sorting them by risk score for immediate supervisory attention and CSV export.

---

## 🏗️ Technical Architecture

The application processes text through a multi-stage pipeline:

1. **Text Preprocessing (`preprocessing.py`):** Expands contractions, removes noise/PII placeholders, tokenizes, applies POS (Part-of-Speech) tagging, and lemmatizes text using NLTK.
2. **Feature Extraction:** Transforms cleaned text using a pre-fitted TF-IDF Vectorizer (Unigrams & Bigrams).
3. **ML Classification (`predictor.py`):** A Logistic Regression model (SAGA solver) classifies the vector into one of 6 banking categories.
4. **Urgency Prediction (`urgency.py`):** Employs a weighted, rule-based keyword matching algorithm to determine urgency (`Critical`, `High`, `Medium`, `Low`). Ensures deterministic compliance guardrails.
5. **Routing & SLA Logic (`routing.py`):** Synthesizes the ML category and rule-based urgency to assign the case and calculate expected resolution deadlines (SLAs).

---

## 📂 Project Structure

```text
├── app.py                 # Main Streamlit application and UI frontend
├── config.py              # System configuration, hyperparameters, and file paths
├── predictor.py           # Core inference orchestration (combines ML and Rules)
├── preprocessing.py       # NLTK text cleaning and lemmatization pipeline
├── routing.py             # Department mapping, SLA calculations, and risk scoring
├── urgency.py             # Rule-based NLP heuristics for urgency prediction
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
└── model/                 # Directory for serialized ML models (Gitignored)
    ├── lr_category_full.pkl
    └── tfidf_category_full.pkl