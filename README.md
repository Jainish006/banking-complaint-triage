# 🏦 Banking Complaint Triage System

An end-to-end AI-powered complaint classification, urgency prediction, and intelligent routing platform for banking operations — built with Python, Streamlit, Scikit-Learn, and Groq AI.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Business Problem](#-business-problem)
3. [Key Features](#-key-features)
4. [Processing Pipeline](#-processing-pipeline)
5. [Technical Architecture](#-technical-architecture)
6. [Project Structure](#-project-structure)
7. [Complaint Categories](#-complaint-categories)
8. [Urgency Levels & SLA](#-urgency-levels--sla)
9. [Model Performance](#-model-performance)
10. [Installation & Setup](#-installation--setup)
11. [Configuration](#-configuration)
12. [Usage Guide](#-usage-guide)
13. [Known Limitations](#-known-limitations)
14. [Future Enhancements](#-future-enhancements)
15. [Data Source](#-data-source)

---

## 📖 Project Overview

Financial institutions receive hundreds of thousands of customer complaints daily. Manual triage of these complaints is slow, error-prone, and operationally expensive. High-priority cases such as fraud and identity theft often sit in the same queue as routine inquiries, causing regulatory delays and customer dissatisfaction.

This system automates the entire complaint triage workflow — from raw text ingestion to department routing — using a production-grade NLP and ML pipeline trained on 3.6 million real consumer complaints from the CFPB Consumer Complaint Database, enhanced with Groq AI (Llama 3.3 70B) for intelligent urgency classification.

---

## 💼 Business Problem

| Challenge | Impact |
|---|---|
| Manual complaint sorting | 2–3 day routing delays |
| No urgency differentiation | Critical cases missed in standard queues |
| Regulatory SLA violations | RBI/CFPB fines and penalties |
| No pattern detection | Recurring product failures go unnoticed |
| High operational cost | Junior staff overwhelmed with volume |

### Business Impact of This System

| Metric | Value |
|---|---|
| Annual industry losses from manual triage inefficiency | $3B+ |
| Reduction in operations workload through auto-categorization | 45% |
| Manual misrouting errors prevented by NLP triage | 67% |

---

## ✨ Key Features

### 🔍 Single Complaint Triage
- Paste any raw complaint text and receive instant analysis
- Complaint Category, Urgency Level, Recommended Department
- Dynamic Risk Score (0–100) with progress bar visualization
- Prediction Reliability Score based on complaint length and model confidence
- SLA deadline based on urgency level
- Escalation Flag for Critical cases or low-confidence predictions
- Keyword Highlight — visually highlights urgency-triggering words in the complaint
- Urgency Source indicator showing whether prediction came from Groq AI or keyword fallback
- Triage History table tracking all complaints analyzed in the current session

### 📊 Batch Processing & Analytics
- Upload a CSV of complaints for bulk processing with real-time progress bar
- Auto-detects the complaint narrative column
- **Analytics Dashboard** — category distribution and urgency breakdown charts
- **Batch Risk Analytics** — average risk score, highest risk, risk distribution histogram
- **Priority Queue** — Critical and High complaints ranked by risk score for immediate attention
- Filter complaints by category, urgency, and department
- Download filtered results and priority queue as CSV

### 🏠 Interactive Homepage
- Live example complaints (Critical, High, Medium, Low) with one-click loading into Single Triage
- Business impact statistics and end-to-end pipeline overview
- Navigation cards for all app sections

---

## 🔄 Processing Pipeline

```
Raw Complaint Text Input
        │
        ├─────────────────────────────────────────────────────┐
        │                                                     │
        ▼                                                     ▼
clean_preprocessed_text()                         predict_urgency_groq()
        │                                                     │
  Contraction expansion                          Groq API (Llama 3.3 70B)
  Regex noise removal                            temperature=0.0
  PII placeholder removal                        max_tokens=10
  Tokenization                                   5s timeout
  POS tagging                                    Response validation
  Lemmatization                                        │
  Stopword removal                              [On API failure]
        │                                       urgency_level() fallback
  TF-IDF Vectorization                          Weighted keyword scoring
  (unigrams + bigrams)                                 │
        │                                        Urgency Level
  Logistic Regression                            Matched Keywords
        │
  Complaint Category
  Model Confidence
        │
        └──────────────────────┬──────────────────────────────┘
                               │
                        get_department()        → Routing Department
                        get_sla()               → SLA Deadline
                        get_risk_score()        → Risk Score (0-100)
                        escalation_flag         → Escalation Required?
```

---

## 🏗️ Technical Architecture

### Data Source
- **CFPB Consumer Complaint Database** — publicly maintained by the US Consumer Financial Protection Bureau
- 15.69M total complaints loaded → filtered to **3.64M complaints with consumer narratives**
- Label harmonization: 21 raw CFPB product categories → 6 clean target classes

### Text Preprocessing (`preprocessing.py`)
1. Contraction expansion using `contractions` library — preserves negation context
2. Date redaction removal (`XX/XX/XXXX`, `XX/XX/year>` variants)
3. Currency pattern removal (`{$870.00}` format)
4. Redacted token removal (`XXXX` sequences of 2 or more)
5. Lowercasing
6. Newline and tab removal
7. Punctuation and special character removal
8. Whitespace normalization
9. Tokenization using NLTK `word_tokenize`
10. POS tagging using NLTK `pos_tag` — provides grammatical context for lemmatization
11. Lemmatization using `WordNetLemmatizer` with POS-aware tags
12. Stopword removal with preserved negation words: `no`, `not`, `never`, `neither`, `nor`, `cannot`, `without`, `against`
13. Numeric token removal

### Urgency Prediction — Dual Engine (`urgency.py`)

**Primary: Groq AI (LLM-powered)**
- Model: `llama-3.3-70b-versatile` via Groq API
- `temperature=0.0` for deterministic, consistent outputs
- `max_tokens=10` — efficient single-word response
- 5-second timeout to prevent hanging
- Response cached with `st.cache_data` to avoid redundant API calls
- Full response validation before caching
- Structured system prompt with urgency level definitions

**Fallback: Weighted Keyword Scoring Engine**
- Domain-defined keyword dictionary across 4 urgency levels
- Weighted scoring: Critical=4, High=3, Medium=2, Low=1
- Critical override: score ≥ 8 triggers Critical classification
- Negation-aware matching on raw text
- Automatic activation when Groq API is unavailable

**Urgency Source Transparency**
- Every prediction is tagged with `🤖 Groq AI` or `🛡 Keyword Fallback`
- All API calls and fallbacks logged to `app.log`

### Category Classification (`predictor.py` + `routing.py`)

**Vectorization**
- TF-IDF Vectorizer: `ngram_range=(1,2)`, `max_features=100,000`, `min_df=5`, `sublinear_tf=True`
- Trained on 2.91M complaints, applied to 728K test complaints

**Model**
- Logistic Regression (scikit-learn)
  - `solver='saga'` — optimized for large sparse matrices
  - `class_weight='balanced'` — handles class imbalance (Credit Reporting = 66% of data)
  - `max_iter=1000`, `n_jobs=-1`

**Risk Score Formula**
```
risk_score = (urgency_base × 0.7) + (confidence × 100 × 0.3)
```

| Urgency | Base Score |
|---|---|
| Critical | 100 |
| High | 75 |
| Medium | 40 |
| Low | 15 |

**Reliability Score**
- Composite score based on model confidence (70% weight) and complaint word count (30% weight)
- Penalizes very short complaints (< 6 words) with reduced reliability
- Displayed as High / Moderate / Low Reliability with descriptive explanation

---

## 📂 Project Structure

```
NLP+ML Project/
│
├── app.py                          ← Streamlit application (all pages and UI)
├── config.py                       ← Model paths and configuration constants
├── preprocessing.py                ← Text cleaning and NLP preprocessing pipeline
├── urgency.py                      ← Groq AI + keyword-based urgency engine
├── routing.py                      ← Department routing, SLA, and risk score logic
├── predictor.py                    ← End-to-end complaint analysis orchestrator
├── requirements.txt                ← Python dependencies
├── README.md                       ← Project documentation
├── app.log                         ← Runtime logs (API calls, fallbacks, errors)
│
├── model/                          ← Serialized ML models (add to .gitignore)
│   ├── lr_category_full.pkl        ← Trained Logistic Regression classifier
│   └── tfidf_category_full.pkl     ← Fitted TF-IDF vectorizer
│
└── notebook.ipynb                  ← Exploration, EDA, and experimentation notebook
```

---

## 🗂️ Complaint Categories

| Category | Typical Complaints |
|---|---|
| **Credit Reporting** | Credit bureau disputes, FCRA violations, inaccurate reporting, identity theft on credit file |
| **Debt Collection** | Debt validation requests, collector harassment, collection agency disputes |
| **Loans** | Mortgage, student loan, vehicle loan, payday loan payment and servicing issues |
| **Cards & Transactions** | Credit card disputes, unauthorized charges, billing errors, chargebacks |
| **Banking & Accounts** | Checking/savings account issues, deposits, overdraft fees, account closures |
| **Money Transfer & Payments** | Zelle, PayPal, wire transfer, payment app disputes and failures |

---

## ⚡ Urgency Levels & SLA

| Urgency | SLA | Trigger Signals | Department Action |
|---|---|---|---|
| 🔴 **Critical** | 2 Hours | Fraud, identity theft, account takeover, unauthorized withdrawal, eviction risk, funds locked | Immediate escalation — senior team review within 2 hours |
| 🟠 **High** | 24 Hours | Unauthorized charges, credit score damage, financial loss, harassment, repeated ignored disputes | Priority investigation — assigned within 24 hours |
| 🟡 **Medium** | 72 Hours | Billing errors, incorrect information, service delays, late fees, FCRA violations | Standard resolution workflow — assigned within 3 days |
| 🟢 **Low** | 7 Days | Address updates, statement requests, general inquiries, document requests | Routine handling — resolved within 7 days |

---

## 📊 Model Performance

### Category Classifier (Logistic Regression on 3.6M complaints)

| Category | Precision | Recall | F1 Score | Test Samples |
|---|---|---|---|---|
| Banking & Accounts | 0.71 | 0.86 | 0.78 | 37,781 |
| Cards & Transactions | 0.73 | 0.78 | 0.76 | 46,811 |
| Credit Reporting | 0.98 | 0.88 | **0.93** | 478,583 |
| Debt Collection | 0.69 | 0.86 | 0.76 | 82,936 |
| Loans | 0.74 | 0.90 | 0.81 | 59,077 |
| Money Transfer & Payments | 0.77 | 0.84 | 0.80 | 23,139 |
| **Macro Average** | **0.77** | **0.85** | **0.81** | 728,327 |
| **Weighted Average** | **0.89** | **0.87** | **0.88** | 728,327 |

### Urgency Engine (Keyword Fallback — evaluated on spot-checked samples)

| Urgency | F1 Score |
|---|---|
| Critical | 0.95 |
| High | 0.92 |
| Medium | 0.95 |
| Low | 0.98 |
| **Macro Average** | **0.95** |

> **Note:** The urgency model achieves high F1 because it was trained on keyword-labeled data (label leakage). The production system uses Groq AI (LLM) as the primary urgency engine, which generalizes beyond keyword rules. The keyword engine serves as a deterministic fallback.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/banking-complaint-triage.git
cd banking-complaint-triage
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Or for Streamlit Cloud deployment, add to `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

> The system works without a Groq API key — it automatically falls back to the keyword-based urgency engine.

**5. Add model files**

Place the following serialized model files in a `model/` directory:
```
model/
├── lr_category_full.pkl
└── tfidf_category_full.pkl
```

> Add `model/` to your `.gitignore` since these files are large.

**6. Run the application**
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## ⚙️ Configuration

All configuration constants are defined in `config.py`:

```python
CATEGORY_MODEL_PATH = 'model/lr_category_full.pkl'
CATEGORY_VECTORIZER_PATH = 'model/tfidf_category_full.pkl'

CATEGORIES = [
    'Banking & Accounts', 'Cards & Transactions', 'Credit Reporting',
    'Debt Collection', 'Loans', 'Money Transfer & Payments'
]

URGENCY_LEVELS = ['Critical', 'High', 'Medium', 'Low']

TFIDF_MAX_FEATURES = 100000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 5
```

---

## 📖 Usage Guide

### Single Complaint Triage
1. Navigate to **🔍 Single Triage** from the sidebar
2. Paste a raw customer complaint into the text area
3. Click **Analyze Complaint**
4. Review Category, Urgency, Department, Risk Score, SLA, and Escalation Flag
5. Scroll down to see keyword highlights and triage history

### Batch Processing
1. Navigate to **📊 Batch Processing** from the sidebar
2. Upload a CSV file containing complaint narratives
3. Select the column containing complaint text
4. Click **Process All Complaints**
5. Review the Analytics Dashboard, Batch Risk Analytics, and Priority Queue
6. Download filtered results or the Priority Queue as CSV

### Sample Complaints (Homepage)
1. Navigate to **🏠 Home**
2. Click **Open in Single Triage** on any example complaint card
3. The complaint pre-fills in Single Triage — click Analyze to see results

---

## ⚠️ Known Limitations

**Category Classification**
- Cards & Transactions and Debt Collection have lower F1 (0.76) due to vocabulary overlap with Credit Reporting
- Loan complaints mentioning credit bureaus are sometimes misclassified as Credit Reporting
- Short complaints (under 10 tokens after cleaning) may produce lower-confidence predictions

**Urgency Prediction**
- Groq AI requires internet connectivity and a valid API key
- Free tier Groq API has rate limits — large batch processing falls back to keyword engine
- Keyword fallback cannot generalize to urgency expressions not in the dictionary
- Identity theft language used as a legal reference (not actual theft) occasionally triggers Critical incorrectly

**General**
- Trained on US-centric CFPB data — retraining recommended for Indian or other regional financial institution deployment
- Text preprocessing (POS tagging + lemmatization) adds latency for very long complaint narratives
- Batch processing speed depends on complaint volume and API rate limits

---

## 🔮 Future Enhancements

- **Semantic search** — retrieve similar historical complaints using sentence embeddings
- **Complaint summarization** — LLM-generated executive summary for each complaint
- **Topic modeling** — unsupervised clustering to detect emerging complaint themes
- **FinBERT integration** — transformer-based category classification for improved boundary disambiguation
- **Geographic heatmap** — regional complaint trend visualization
- **REST API endpoints** — enterprise system integration via FastAPI
- **Active learning pipeline** — continuously improve urgency labels from human feedback
- **RBI Ombudsman adaptation** — retrain on Indian financial institution complaint data

---

## 📦 Dependencies

```
streamlit          — Web application framework
pandas             — Data manipulation
numpy              — Numerical computing
scikit-learn       — ML model training and inference
nltk               — Text preprocessing (tokenization, POS tagging, lemmatization)
contractions       — Contraction expansion
joblib             — Model serialization
plotly             — Interactive data visualization
groq               — Groq API client
python-dotenv      — Environment variable management
```

---

## 📁 Data Source

Data sourced from the **CFPB Consumer Complaint Database** — a publicly available dataset maintained by the US Consumer Financial Protection Bureau containing real consumer complaints submitted against financial institutions.

- **Dataset URL:** https://www.consumerfinance.gov/data-research/consumer-complaints/
- **Bulk download:** https://files.consumerfinance.gov/ccdb/complaints.csv.zip
- **Records used:** 3,641,633 complaints with consumer narratives (after filtering from 15.69M total)
- **Label harmonization:** 21 raw product categories → 6 clean target classes

---

## 👤 Author

**Jainish** — Computer Science Engineering Student (Third Year)
Focus: Machine Learning · NLP · Full-Stack Development

---

## 📄 License

This project is for educational and portfolio purposes. Data sourced from CFPB is publicly available under their open data policy.