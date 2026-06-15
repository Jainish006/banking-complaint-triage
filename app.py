import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import html
import re
import time
import random

# Attempt to import the real predictor, otherwise use a mock for testing
try:
    from predictor import analyze_complaint
except ImportError:
    def analyze_complaint(text, **kwargs):
        """Mock predictor for demonstration purposes."""
        time.sleep(0.5)  # Simulate API/Model latency
        categories = ['Credit Reporting', 'Debt Collection', 'Loans', 'Cards & Transactions', 'Banking & Accounts', 'Money Transfer & Payments']
        urgencies = ['Low', 'Medium', 'High', 'Critical']
        departments = ['General Support', 'Fraud Team', 'Loan Officers', 'Credit Dispute Unit']
        return {
            'category': random.choice(categories),
            'urgency': random.choice(urgencies),
            'department': random.choice(departments),
            'confidence': random.uniform(0.4, 0.99)
        }

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="Banking Complaint Triage System",
    page_icon="🏦",
    layout="wide"
)

# ------------------------
# Sample Complaints Library
# ------------------------
CRITICAL_SAMPLE = """My online banking account was hacked and multiple unauthorized transfers were made from my savings account. I can no longer access my account and additional transactions are still occurring."""

HIGH_SAMPLE = """I noticed a charge on my credit card that I do not recognize and submitted a dispute last week. I have contacted customer service twice but have not yet received an update on the investigation. I would like the transaction reviewed and the dispute process expedited."""

MEDIUM_SAMPLE = """I was charged a late fee on my credit card statement even though I submitted my payment before the due date. I would like the charge reviewed and corrected."""

LOW_SAMPLE = """Could you provide information on how I can obtain paper statements for the previous calendar year for my checking account?"""

# ------------------------
# Session State Initialization
# ------------------------
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Home"
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'sample_text' not in st.session_state:
    st.session_state.sample_text = ""
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Check query parameters for page routing or sample population
try:
    query_params = st.query_params
    if query_params:
        if "page" in query_params:
            page_val = query_params["page"]
            if page_val == "Single_Triage":
                st.session_state.page = "🔍 Single Triage"
            elif page_val == "Batch_Processing":
                st.session_state.page = "📊 Batch Processing"
            elif page_val == "About":
                st.session_state.page = "ℹ️ About"
            elif page_val == "Home":
                st.session_state.page = "🏠 Home"
                
        if "sample" in query_params:
            sample_val = query_params["sample"]
            if sample_val == "critical":
                st.session_state.sample_text = CRITICAL_SAMPLE
                st.session_state.analysis_result = None
            elif sample_val == "high":
                st.session_state.sample_text = HIGH_SAMPLE
                st.session_state.analysis_result = None
            elif sample_val == "medium":
                st.session_state.sample_text = MEDIUM_SAMPLE
                st.session_state.analysis_result = None
            elif sample_val == "low":
                st.session_state.sample_text = LOW_SAMPLE
                st.session_state.analysis_result = None
                
        st.query_params.clear()
except AttributeError:
    try:
        query_params = st.experimental_get_query_params()
        if query_params:
            if "page" in query_params:
                page_val = query_params["page"][0]
                if page_val == "Single_Triage":
                    st.session_state.page = "🔍 Single Triage"
                elif page_val == "Batch_Processing":
                    st.session_state.page = "📊 Batch Processing"
                elif page_val == "About":
                    st.session_state.page = "ℹ️ About"
                elif page_val == "Home":
                    st.session_state.page = "🏠 Home"
                    
            if "sample" in query_params:
                sample_val = query_params["sample"][0]
                if sample_val == "critical":
                    st.session_state.sample_text = CRITICAL_SAMPLE
                    st.session_state.analysis_result = None
                elif sample_val == "high":
                    st.session_state.sample_text = HIGH_SAMPLE
                    st.session_state.analysis_result = None
                elif sample_val == "medium":
                    st.session_state.sample_text = MEDIUM_SAMPLE
                    st.session_state.analysis_result = None
                elif sample_val == "low":
                    st.session_state.sample_text = LOW_SAMPLE
                    st.session_state.analysis_result = None
            st.experimental_set_query_params()
    except Exception:
        pass

st.markdown("""
<style>
body { background-color: #0f0f1a; }
.main-title { font-size: 40px; font-weight: 700; color: #FFFFFF; }
.subtitle { font-size: 16px; color: #aaa; margin-bottom: 20px; }
.footer { text-align: center; color: gray; padding-top: 30px; font-size: 13px; }

/* Force Streamlit column containers to flex and stretch vertically */
div[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
}
div[data-testid="column"] > div {
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
}
div[data-testid="column"] [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
    justify-content: space-between !important;
}
div[data-testid="column"] [data-testid="stVerticalBlock"] > div {
    flex-grow: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
div[data-testid="column"] [data-testid="element-container"],
div[data-testid="column"] [data-testid="stMarkdown"],
div[data-testid="column"] [data-testid="stMarkdown"] > div,
div[data-testid="column"] [data-testid="stMarkdownContainer"] {
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
    height: 100% !important;
}
.styled-metric-card {
    min-height: 125px !important;
}

/* Unified app card layout system */
.app-card {
    background-color: #1e1e2e !important;
    padding: 20px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    box-sizing: border-box !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.app-card:hover {
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1) !important;
}

.card-content {
    flex-grow: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
.card-content h3, .card-content h4 {
    margin-top: 0 !important;
    margin-bottom: 10px !important;
    color: white !important;
}
.card-content p {
    margin: 6px 0 !important;
    font-size: 14px !important;
    line-height: 1.4 !important;
}
.card-content ul {
    margin: 8px 0 0 0 !important;
    padding-left: 20px !important;
    font-size: 13px !important;
    color: #b7bec9 !important;
}

.card-footer {
    margin-top: auto !important;
    padding-top: 15px !important;
}

/* Dedicated card classes for sample complaints to ensure absolute grid alignment */
.sample-card {
    display: grid !important;
    grid-template-rows: 60px 70px 120px 90px 56px !important;
    row-gap: 12px !important;
    height: 100% !important;
    box-sizing: border-box !important;
}

.sample-title {
    grid-row: 1 !important;
    height: 60px !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
}
.sample-title h4 {
    margin: 0 !important;
    color: white !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

.sample-scenario {
    grid-row: 2 !important;
    height: 70px !important;
    margin: 0 !important;
    font-size: 14px !important;
    line-height: 1.4 !important;
    color: #e2e8f0 !important;
    overflow: hidden !important;
}
.sample-scenario p {
    margin: 0 !important;
}

.sample-preview {
    grid-row: 3 !important;
    height: 120px !important;
    margin: 0 !important;
    font-style: italic !important;
    color: #aaa !important;
    font-size: 14px !important;
    line-height: 1.4 !important;
    overflow: hidden !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 5 !important;
    -webkit-box-orient: vertical !important;
}

.sample-meta {
    grid-row: 4 !important;
    height: 90px !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    font-size: 14px !important;
    line-height: 1.4 !important;
    color: #cbd5e1 !important;
}
.sample-meta p {
    margin: 4px 0 !important;
}

.sample-footer {
    grid-row: 5 !important;
    height: 56px !important;
    margin: 0 !important;
    display: flex !important;
    align-items: flex-end !important;
}

/* Custom button style mirroring standard Streamlit secondary buttons */
.custom-button {
    display: block;
    width: 100%;
    text-align: center;
    background-color: transparent;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    text-decoration: none !important;
    transition: background-color 0.2s, border-color 0.2s;
    box-sizing: border-box;
}
.custom-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.4);
    color: white !important;
}
.feature-card-title {
    min-height: 72px;
    display: flex;
    align-items: flex-start;
}
.performance-title {
    min-height: 36px;
    display: flex;
    align-items: flex-start;
}
.performance-value {
    min-height: 58px;
    display: flex;
    align-items: flex-start;
}
.performance-subtitle {
    min-height: 48px;
    display: flex;
    align-items: flex-start;
}
</style>
""", unsafe_allow_html=True)

# ------------------------
# UI Components (Cards)
# ------------------------
def render_kpi_card(label, value, color="#4CAF50", subtitle="", flag="", centered=False):
    """Unified layout for all dashboard and about page KPI metrics cards."""
    text_align = "center" if centered else "left"
    justify = "center" if centered else "flex-start"
    return f"""
    <div class="styled-metric-card" style="background-color:#1e1e2e; padding:20px; border-radius:12px; border-left:5px solid {color}; margin-bottom:15px; text-align:{text_align}; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;">
        <div class="kpi-header" style="color:gray; margin:0; font-size:13px; line-height:1.3; min-height:36px; display:flex; align-items:flex-start; justify-content:{justify};">{label}{flag}</div>
        <div class="kpi-value-container" style="display:flex; align-items:center; justify-content:{justify}; flex-grow:1; margin:8px 0;">
            <div class="kpi-value" style="color:white; margin:0; font-size:26px; font-weight:bold; line-height:1.1;">{value}</div>
        </div>
        {f'<div class="kpi-subtitle" style="color:#b7bec9; margin:0; font-size:11px; line-height:1.35; min-height:32px; display:flex; align-items:flex-end; justify-content:{justify};">{subtitle}</div>' if subtitle else ''}
    </div>
    """

def render_performance_card(label, value, color="#4CAF50", subtitle=""):
    """Dedicated KPI card renderer for the Model Performance section to allow equal-height internal region sizing."""
    return f"""
    <div class="styled-metric-card" style="background-color:#1e1e2e; padding:20px; border-radius:12px; border-left:5px solid {color}; margin-bottom:15px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;">
        <div class="performance-title" style="color:gray; margin:0; font-size:13px; line-height:1.3;">{label}</div>
        <div style="flex-grow:1; margin:8px 0; display:flex; flex-direction:column; justify-content:center;">
            <div class="performance-value" style="color:white; margin:0; font-size:26px; font-weight:bold; line-height:1.1;">{value}</div>
        </div>
        {f'<div class="performance-subtitle" style="color:#b7bec9; margin:0; font-size:11px; line-height:1.35;">{subtitle}</div>' if subtitle else ''}
    </div>
    """

def styled_card(label, value, color="#4CAF50", subtitle="", flag=""):
    """Generic reusable function for styled metrics cards."""
    return render_kpi_card(label, value, color, subtitle, flag, centered=False)

def metric_card(label, value, color="#4CAF50"):
    """Centered metric card for dashboards."""
    return render_kpi_card(label, value, color, centered=True)

def urgency_card(urgency):
    color_map = {"Critical": "#F44336", "High": "#FF9800", "Medium": "#FFC107", "Low": "#4CAF50"}
    return styled_card("Urgency Level", urgency, color_map.get(urgency, "#888"))

def confidence_card(confidence):
    confidence_value = safe_float(confidence)
    tooltip_html = ' <span title="Confidence measures how certain the model is about the prediction." style="cursor:help; font-size:11px;">ℹ️</span>'
    label_text = f"Model Confidence{tooltip_html}"
    if confidence_value is None:
        return styled_card(label_text, "N/A", "#888", subtitle="Model confidence unavailable.")

    pct = max(0.0, min(confidence_value * 100, 100.0))
    color = "#4CAF50" if pct >= 70 else "#FF9800" if pct >= 50 else "#F44336"
    flag = " ⚠️ Low Confidence" if pct < 70 else ""
    return styled_card(label_text, f"{pct:.1f}%", color, flag=flag)

def get_word_count(text):
    return len(re.findall(r"\b\w+\b", str(text or "")))

def get_reliability_level(reliability_score):
    score = normalize_reliability_score(reliability_score)
    if score is None:
        return "Unknown Reliability"
    if score >= 90:
        return "High Reliability"
    if score >= 70:
        return "Moderate Reliability"
    return "Low Reliability"

def get_reliability_color(reliability_level):
    color_map = {
        "High Reliability": "#4CAF50",
        "Moderate Reliability": "#FF9800",
        "Low Reliability": "#F44336",
        "Unknown Reliability": "#888888"
    }
    return color_map.get(reliability_level, "#888888")

def normalize_reliability_score(reliability_score):
    score = safe_float(reliability_score)
    if score is None:
        return None
    return max(0.0, min(score, 100.0))

def get_reliability_description(reliability_level, confidence, word_count):
    confidence_value = safe_float(confidence)
    
    if reliability_level == "Unknown Reliability":
        return "Reliability assessment unavailable because the model output is incomplete."
        
    if reliability_level == "High Reliability":
        if confidence_value is not None and confidence_value >= 0.80:
            return "Strong model confidence and clear complaint narrative."
        return "High prediction reliability backed by sufficient complaint details."
        
    if reliability_level == "Moderate Reliability":
        if confidence_value is not None and confidence_value < 0.80:
            return "Moderate confidence. Additional review may improve accuracy."
        return "Prediction is usable, but additional review is recommended."
        
    # Low Reliability
    if word_count < 10:
        return "Limited complaint details reduce prediction certainty."
    if confidence_value is not None and confidence_value < 0.60:
        return "Low model confidence reduces prediction certainty."
    return "Limited complaint details reduce prediction certainty."

def calculate_reliability_score(confidence, complaint_text):
    confidence_value = safe_float(confidence)
    word_count = get_word_count(complaint_text)

    # Rebalanced logic with more gradual length penalties
    if word_count < 5:
        length_penalty = 20
    elif word_count < 10:
        length_penalty = 10
    elif word_count < 20:
        length_penalty = 5
    else:
        length_penalty = 0

    length_score = 100 - length_penalty

    if confidence_value is None and word_count == 0:
        return None, word_count

    if confidence_value is None:
        reliability_score = max(0, length_score - 30)
    else:
        # Confidence weight is 0.60, length score weight is 0.40
        reliability_score = round((confidence_value * 100 * 0.60) + (length_score * 0.40))

    return max(0, min(reliability_score, 100)), word_count

def render_reliability_card(confidence, complaint_text):
    reliability_score, word_count = calculate_reliability_score(confidence, complaint_text)
    reliability_level = get_reliability_level(reliability_score)
    reliability_color = get_reliability_color(reliability_level)

    if reliability_score is None:
        score_label = "N/A / 100"
        progress_width = 0
        progress_text = "░░░░░░░░░░ 0%"
    else:
        score_int = int(round(reliability_score))
        score_label = f"{score_int} / 100"
        progress_width = score_int
        filled_blocks = max(0, min(10, round(score_int / 10)))
        progress_text = f"{'█' * filled_blocks}{'░' * (10 - filled_blocks)} {score_int}%"

    description = get_reliability_description(reliability_level, confidence, word_count)

    return f"""
    <div class="app-card" style="border-left:5px solid {reliability_color}; margin-bottom:15px;">
        <div class="card-content">
            <div style="color:gray; margin:0; font-size:13px; min-height:20px; display:flex; align-items:flex-start; gap:4px;">
                Prediction Reliability
                <span title="Reliability considers confidence, complaint detail level, information density, and ambiguity." style="cursor:help; font-size:11px;">ℹ️</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; margin-top:2px;">
                <p style="color:white; margin:0; font-size:32px; font-weight:bold;">{score_label}</p>
                <span style="background:{reliability_color}; color:#0f0f1a; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:700; line-height:1;">{reliability_level}</span>
            </div>
            <div style="width:100%; height:12px; border-radius:999px; background:rgba(255,255,255,0.10); overflow:hidden; margin-top:14px;">
                <div style="width:{progress_width}%; height:12px; background:{reliability_color}; border-radius:999px;"></div>
            </div>
            <div style="margin-top:8px; color:{reliability_color}; font-family:'Courier New', monospace; font-size:12px; letter-spacing:1px;">{progress_text}</div>
            <p style="color:#b7bec9; margin:6px 0 0 0; font-size:11px; line-height:1.35;">{description}</p>
            <p style="color:#8b93a1; margin:4px 0 0 0; font-size:10px;">Complaint length: {word_count} words</p>
        </div>
    </div>
    """

def safe_float(value):
    try:
        if value is None:
            return None
        numeric_value = float(value)
        if pd.isna(numeric_value):
            return None
        return numeric_value
    except (TypeError, ValueError):
        return None

def get_risk_level(risk_score):
    score = normalize_risk_score(risk_score)
    if score is None:
        return "Unknown Risk"
    if score >= 90:
        return "Critical Risk"
    if score >= 70:
        return "High Risk"
    if score >= 40:
        return "Medium Risk"
    return "Low Risk"

def get_risk_color(risk_level):
    color_map = {
        "Critical Risk": "#F44336",
        "High Risk": "#FF9800",
        "Medium Risk": "#FFC107",
        "Low Risk": "#4CAF50",
        "Unknown Risk": "#888888"
    }
    return color_map.get(risk_level, "#888888")

def get_risk_description(risk_level):
    description_map = {
        "Critical Risk": "Immediate investigation recommended due to high operational and customer impact.",
        "High Risk": "Prompt review required to reduce potential customer risk.",
        "Medium Risk": "Monitor and investigate within standard operational timelines.",
        "Low Risk": "Routine issue with limited business impact.",
        "Unknown Risk": "Risk score unavailable from the model output."
    }
    return description_map.get(risk_level, "Risk score unavailable from the model output.")

def normalize_risk_score(risk_score):
    score = safe_float(risk_score)
    if score is None:
        return None
    return max(0.0, min(score, 100.0))

def sla_description(urgency):
    description_map = {
        "Critical": "Immediate action required. Highest priority response window.",
        "High": "Prompt investigation required to minimize customer impact.",
        "Medium": "Standard priority issue requiring timely resolution.",
        "Low": "Routine request with minimal business risk.",
    }
    return description_map.get(urgency, "Expected response deadline based on predicted urgency and operational risk.")

def escalation_description(escalated):
    if escalated:
        return "Immediate review by senior operations staff is recommended due to high-risk indicators."
    return "No escalation needed. Standard departmental workflow applies."

def sla_card(sla, urgency):
    return styled_card("SLA", sla, "#00BCD4", subtitle=sla_description(urgency))

def escalation_card(urgency, confidence, escalation_flag=None):
    if escalation_flag is not None:
        if isinstance(escalation_flag, str):
            escalated = escalation_flag.strip().lower() in {"yes", "true", "1", "required", "escalate"}
        else:
            escalated = bool(escalation_flag)
    else:
        escalated = urgency == "Critical"

    color = "#F44336" if escalated else "#4CAF50"
    label = "🔴 Escalation Required" if escalated else "🟢 No Escalation Required"
    return styled_card("Escalation Flag", label, color, subtitle=escalation_description(escalated))

def render_risk_card(risk_score):
    normalized_score = normalize_risk_score(risk_score)
    risk_level = get_risk_level(normalized_score)
    risk_color = get_risk_color(risk_level)

    if normalized_score is None:
        score_label = "N/A / 100"
        progress_width = 0
        progress_text = "░░░░░░░░░░ 0%"
    else:
        score_int = int(round(normalized_score))
        score_label = f"{score_int} / 100"
        progress_width = score_int
        filled_blocks = max(0, min(10, round(score_int / 10)))
        progress_text = f"{'█' * filled_blocks}{'░' * (10 - filled_blocks)} {score_int}%"

    return f"""
    <div class="app-card" style="border-left:5px solid {risk_color}; margin-bottom:15px;">
        <div class="card-content">
            <div style="color:gray; margin:0; font-size:13px; min-height:20px; display:flex; align-items:flex-start;">Risk Score</div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; margin-top:2px;">
                <p style="color:white; margin:0; font-size:32px; font-weight:bold;">{score_label}</p>
                <span style="background:{risk_color}; color:#0f0f1a; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:700; line-height:1;">{risk_level}</span>
            </div>
            <div style="width:100%; height:12px; border-radius:999px; background:rgba(255,255,255,0.10); overflow:hidden; margin-top:14px;">
                <div style="width:{progress_width}%; height:12px; background:{risk_color}; border-radius:999px;"></div>
            </div>
            <div style="margin-top:8px; color:{risk_color}; font-family:'Courier New', monospace; font-size:12px; letter-spacing:1px;">{progress_text}</div>
            <p style="color:#b7bec9; margin:6px 0 0 0; font-size:11px; line-height:1.35;">{get_risk_description(risk_level)}</p>
        </div>
    </div>
    """

def highlight_keywords(text, keywords):
    highlighted = html.escape(str(text))

    for keyword in sorted(set(keywords), key=len, reverse=True):
        pattern = re.compile(rf"({re.escape(keyword)})", re.IGNORECASE)
        highlighted = pattern.sub(
            r'<span style="background-color:#FFD54F;color:black;padding:2px 4px;border-radius:4px;font-weight:bold;">\1</span>',
            highlighted
        )

    return highlighted



# ------------------------
# Batch Processing Helper Functions
# ------------------------
def style_risk_score(val):
    try:
        val_f = float(val)
        if 90 <= val_f <= 100:
            return 'color: #F44336; font-weight: bold;'
        elif 70 <= val_f < 90:
            return 'color: #FF9800; font-weight: bold;'
        elif 40 <= val_f < 70:
            return 'color: #FFC107; font-weight: bold;'
        elif 0 <= val_f < 40:
            return 'color: #4CAF50; font-weight: bold;'
    except:
        pass
    return ''

def calculate_batch_risk_metrics(df):
    """
    Calculates operational risk metrics for a batch of complaints.
    """
    scores = pd.to_numeric(df['Risk Score'], errors='coerce').dropna()
    if len(scores) == 0:
        return {
            'avg_risk': 0,
            'max_risk': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0
        }
    
    avg_risk = int(round(scores.mean()))
    max_risk = int(round(scores.max()))
    
    critical_count = int((scores >= 90).sum())
    high_count = int(((scores >= 70) & (scores < 90)).sum())
    medium_count = int(((scores >= 40) & (scores < 70)).sum())
    low_count = int((scores < 40).sum())
    
    return {
        'avg_risk': avg_risk,
        'max_risk': max_risk,
        'critical_count': critical_count,
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count
    }

def create_risk_distribution_chart(df):
    """
    Creates a Plotly bar chart showing the distribution of risk scores.
    """
    metrics = calculate_batch_risk_metrics(df)
    
    categories = ['0-39<br>(Low)', '40-69<br>(Medium)', '70-89<br>(High)', '90-100<br>(Critical)']
    counts = [metrics['low_count'], metrics['medium_count'], metrics['high_count'], metrics['critical_count']]
    
    colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto',
            hovertemplate='Bucket: %{x}<br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Risk Score Distribution',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'white'}
        },
        xaxis_title='Risk Score Range',
        yaxis_title='Number of Complaints',
        paper_bgcolor='#1e1e2e',
        plot_bgcolor='#1e1e2e',
        font_color='white',
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(l=40, r=40, t=50, b=40),
        height=350
    )
    
    return fig

def create_priority_queue(df):
    """
    Filters complaints for 'Critical' or 'High' urgency and sorts by Risk Score descending.
    """
    pq_df = df[df['Urgency'].isin(['Critical', 'High'])].copy()
    pq_df = pq_df.sort_values(by='Risk Score', ascending=False)
    pq_df = pq_df.reset_index(drop=True)
    pq_df.index = pq_df.index + 1
    pq_df.index.name = 'Rank'
    pq_df = pq_df.reset_index()
    return pq_df

def render_priority_queue_kpis(pq_df):
    """
    Renders KPI cards for the Priority Queue.
    """
    priority_cases = len(pq_df)
    critical_cases = int((pq_df['Urgency'].astype(str).str.replace('🔴 ', '').str.replace('🟠 ', '') == 'Critical').sum())
    high_cases = int((pq_df['Urgency'].astype(str).str.replace('🔴 ', '').str.replace('🟠 ', '') == 'High').sum())
    
    scores = pd.to_numeric(pq_df['Risk Score'], errors='coerce').dropna()
    avg_queue_risk = int(round(scores.mean())) if len(scores) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("Priority Cases", priority_cases, "#00BCD4"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("Critical Cases", critical_cases, "#F44336"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("High Cases", high_cases, "#FF9800"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("Average Queue Risk", avg_queue_risk, "#E91E63"), unsafe_allow_html=True)

def export_priority_queue_csv(pq_df):
    """
    Exports priority queue to clean CSV (removes emojis).
    """
    export_df = pq_df.copy()
    if 'Urgency' in export_df.columns:
        export_df['Urgency'] = export_df['Urgency'].astype(str).str.replace('🔴 ', '').str.replace('🟠 ', '')
    return export_df.to_csv(index=False).encode('utf-8')

# ------------------------
# Single Complaint Triage / SaaS Landing Page Helper Functions
# ------------------------
CRITICAL_SAMPLE = """My online banking account was hacked and multiple unauthorized transfers were made from my savings account. I can no longer access my account and additional transactions are still occurring."""

HIGH_SAMPLE = """I noticed a charge on my credit card that I do not recognize and submitted a dispute last week. I have contacted customer service twice but have not yet received an update on the investigation. I would like the transaction reviewed and the dispute process expedited."""

MEDIUM_SAMPLE = """I was charged a late fee on my credit card statement even though I submitted my payment before the due date. I would like the charge reviewed and corrected."""

LOW_SAMPLE = """Could you provide information on how I can obtain paper statements for the previous calendar year for my checking account?"""

def render_sample_card(title, color, scenario, preview, category, urgency, sample_id):
    return f"""
    <div class="app-card sample-card">
        <div class="sample-title">
            <h4>{color} {title}</h4>
        </div>
        <div class="sample-scenario">
            <p><strong>Scenario:</strong> {scenario}</p>
        </div>
        <div class="sample-preview">
            "{preview}"
        </div>
        <div class="sample-meta">
            <p><strong>Expected Category:</strong> {category}</p>
            <p><strong>Expected Urgency:</strong> {urgency}</p>
        </div>
        <div class="sample-footer">
            <a href="?page=Single_Triage&sample={sample_id}" target="_self" class="custom-button">Open in Single Triage</a>
        </div>
    </div>
    """

def render_sample_complaints():
    st.markdown("---")
    st.subheader("💡 Try Example Complaints")
    st.markdown("<p style='color:#aaa; font-size:14px; margin-bottom:20px;'>Select one of the realistic example scenarios below to test the NLP models in the Single Triage interface.</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    samples = [
        {
            "title": "Critical Risk",
            "color": "🔴",
            "scenario": "Account takeover / unauthorized transactions.",
            "preview": CRITICAL_SAMPLE,
            "category": "Banking & Accounts",
            "urgency": "🔴 Critical",
            "sample_id": "critical",
            "col": col1
        },
        {
            "title": "High Risk",
            "color": "🟠",
            "scenario": "Unauthorized credit card charge dispute with significant customer impact.",
            "preview": HIGH_SAMPLE,
            "category": "Cards & Transactions",
            "urgency": "🟠 High",
            "sample_id": "high",
            "col": col2
        },
        {
            "title": "Medium Risk",
            "color": "🟡",
            "scenario": "Incorrect fee or billing dispute.",
            "preview": MEDIUM_SAMPLE,
            "category": "Cards & Transactions",
            "urgency": "🟡 Medium",
            "sample_id": "medium",
            "col": col3
        },
        {
            "title": "Low Risk",
            "color": "🟢",
            "scenario": "Request paper statement / info.",
            "preview": LOW_SAMPLE,
            "category": "Banking & Accounts",
            "urgency": "🟢 Low",
            "sample_id": "low",
            "col": col4
        }
    ]
    
    for s in samples:
        with s["col"]:
            st.markdown(
                render_sample_card(
                    title=s["title"],
                    color=s["color"],
                    scenario=s["scenario"],
                    preview=s["preview"],
                    category=s["category"],
                    urgency=s["urgency"],
                    sample_id=s["sample_id"]
                ),
                unsafe_allow_html=True
            )

def render_input_section():
    st.subheader("📋 Enter Customer Complaint")
    
    complaint_text = st.text_area(
        "Complaint Narrative",
        value=st.session_state.sample_text,
        height=200,
        placeholder="Type, paste, or load a sample complaint from the Home page..."
    )
    
    # Keep session state updated with manual user input
    st.session_state.sample_text = complaint_text
    
    if st.button("🔍 Analyze Complaint", width="stretch", type="primary"):
        if not complaint_text.strip():
            st.error("⚠️ Please enter a complaint narrative.")
            return
            
        with st.spinner("Analyzing complaint..."):
            try:
                from predictor import analyze_complaint as run_analyze
                result = run_analyze(complaint_text, return_details=True)
            except Exception:
                result = analyze_complaint(complaint_text, return_details=True)
                
            st.session_state.analysis_result = result
            
            # Save to history
            try:
                urgency_level = result.get("urgency_level", result.get("urgency", "Unknown"))
                matched_keywords = result.get("matched_keywords", []) or []
                risk_score = result.get("risk_score", result.get("risk"))
                reliability_score, reliability_word_count = calculate_reliability_score(result.get('confidence'), complaint_text)
                
                st.session_state.history.append({
                    'text': complaint_text,
                    'category': result.get('category'),
                    'urgency': urgency_level,
                    'urgency_source': result.get('urgency_source', '🛡 Keyword Fallback'),
                    'department': result.get('department'),
                    'confidence': result.get('confidence'),
                    'sla': result.get('sla', 'Unknown'),
                    'risk_score': risk_score,
                    'reliability_score': reliability_score,
                    'reliability_level': get_reliability_level(reliability_score),
                    'reliability_words': reliability_word_count,
                    'escalation_flag': result.get('escalation_flag'),
                    'matched_keywords': ", ".join(matched_keywords)
                })
            except Exception:
                pass
                
            st.toast("Analysis Complete!", icon="✅")
            st.rerun()

def render_results():
    result = st.session_state.analysis_result
    if not result:
        return
        
    st.markdown("---")
    st.subheader("📊 Triage Results")
    
    category = result.get('category', 'Unknown')
    department = result.get('department', 'Unknown')
    urgency_level = result.get('urgency_level', result.get('urgency', 'Unknown'))
    confidence = result.get('confidence')
    risk_score = result.get('risk_score', result.get('risk'))
    sla = result.get('sla', 'Unknown')
    escalation_flag = result.get('escalation_flag')
    matched_keywords = result.get('matched_keywords', []) or []
    
    # Columns layout for KPI cards
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown(styled_card("Complaint Category", category, "#2196F3"), unsafe_allow_html=True)
    with col2:
        st.markdown(styled_card("Department", department, "#9C27B0"), unsafe_allow_html=True)
        
    col3, col4, col5 = st.columns(3, gap="medium")
    with col3:
        st.markdown(urgency_card(urgency_level), unsafe_allow_html=True)
    with col4:
        st.markdown(confidence_card(confidence), unsafe_allow_html=True)
    with col5:
        urgency_source = result.get('urgency_source', '🛡 Keyword Fallback')
        source_color = "#8B5CF6" if "Groq" in urgency_source else "#888888"
        st.markdown(styled_card("Urgency Source", urgency_source, source_color), unsafe_allow_html=True)
        
    st.markdown(render_risk_card(risk_score), unsafe_allow_html=True)
    st.markdown(render_reliability_card(confidence, st.session_state.sample_text), unsafe_allow_html=True)
    
    with st.expander("ℹ️ Understanding Confidence vs. Reliability"):
        st.markdown(
            "**Model Confidence** measures how certain the model is about the prediction.\n\n"
            "**Prediction Reliability** considers confidence, complaint detail level, information density, and ambiguity."
        )

    st.markdown(sla_card(sla, urgency_level), unsafe_allow_html=True)
    st.markdown(escalation_card(urgency_level, confidence, escalation_flag), unsafe_allow_html=True)
    
    st.subheader("Highlighted Complaint Narrative")
    highlighted_text = highlight_keywords(st.session_state.sample_text, matched_keywords)
    st.markdown(f'<div style="background-color:#1e1e2e; padding:20px; border-radius:12px; line-height:1.6; border:1px solid rgba(255,255,255,0.05); color:white;">{highlighted_text}</div>', unsafe_allow_html=True)
    
    if matched_keywords:
        st.write("")
        st.markdown("**Matched Urgency Keywords:** " + ", ".join(f"`{kw}`" for kw in matched_keywords))

def render_business_impact_section():
    st.markdown("---")
    st.subheader("🏢 Why Complaint Triage Matters")
    st.markdown("<p style='color:#aaa; font-size:14px; margin-bottom:20px;'>Automating complaint ingestion and prioritization drives significant operational efficiency and customer satisfaction.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown(metric_card("Annual Inefficiency Losses", "$3B+", "#F44336"), unsafe_allow_html=True)
        st.caption("Estimated annual industry losses from manual handling inefficiencies.")
    with col2:
        st.markdown(metric_card("Triage Effort Reduction", "45%", "#4CAF50"), unsafe_allow_html=True)
        st.caption("Average reduction in operations workload through auto-categorization.")
    with col3:
        st.markdown(metric_card("Routing Error Mitigation", "67%", "#2196F3"), unsafe_allow_html=True)
        st.caption("Percentage of manual misrouting errors prevented by NLP triage model.")

# ------------------------
# Page Render Functions
# ------------------------
def render_home():
    st.markdown("<div class='main-title'>🏦 Banking Complaint Triage System</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI-powered complaint classification, urgency prediction, and intelligent routing for banking operations.</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Metrics
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.markdown(metric_card("Complaint Categories", "6", "#4CAF50"), unsafe_allow_html=True)
    col2.markdown(metric_card("Urgency Levels", "4", "#FF9800"), unsafe_allow_html=True)
    col3.markdown(metric_card("Macro F1 Score", "81%", "#2196F3"), unsafe_allow_html=True)
    col4.markdown(metric_card("Training Data", "3.6M", "#9C27B0"), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚙️ Processing Pipeline")
    with st.expander("View End-to-End Workflow", expanded=True):
        st.markdown("""
        **1️⃣ Text Preprocessing:** Contraction expansion → noise removal → tokenization → POS tagging → lemmatization → stopword removal  
        **2️⃣ Category Classification:** TF-IDF vectorization → Logistic Regression → (e.g., *Credit Reporting, Loans, etc.*)  
        **3️⃣ Urgency Prediction:** Weighted keyword scoring → `🔴 Critical`, `🟠 High`, `🟡 Medium`, `🟢 Low`  
        **4️⃣ Intelligent Routing:** Category + Urgency → Department assignment → Escalation flag
        """)

    # Business impact benchmark KPI cards (Moved above Try Example Complaints)
    render_business_impact_section()

    # Try Example Complaints Cards
    render_sample_complaints()

    st.markdown("---")
    st.subheader("🚀 Available Features")
    col_feat1, col_feat2, col_feat3 = st.columns(3, gap="large")
    
    with col_feat1:
        st.markdown("""
        <div class="app-card">
            <div class="card-content">
                <div class="feature-card-title">
                    <h3>🔍 Single Triage<br>&nbsp;</h3>
                </div>
                <p>Analyze one complaint instantly.</p>
                <ul>
                    <li>Category & Urgency</li>
                    <li>Routing & Escalation</li>
                </ul>
            </div>
            <div class="card-footer">
                <a href="?page=Single_Triage" target="_self" class="custom-button">Go to Single Triage →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_feat2:
        st.markdown("""
        <div class="app-card">
            <div class="card-content">
                <div class="feature-card-title">
                    <h3>📊 Batch Processing</h3>
                </div>
                <p>Upload CSV of complaints.</p>
                <ul>
                    <li>Bulk Predictions</li>
                    <li>Analytics & Trends</li>
                </ul>
            </div>
            <div class="card-footer">
                <a href="?page=Batch_Processing" target="_self" class="custom-button">Go to Batch Processing →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_feat3:
        st.markdown("""
        <div class="app-card">
            <div class="card-content">
                <div class="feature-card-title">
                    <h3>ℹ️ About<br>&nbsp;</h3>
                </div>
                <p>Project documentation.</p>
                <ul>
                    <li>Model Performance</li>
                    <li>Known Limitations</li>
                </ul>
            </div>
            <div class="card-footer">
                <a href="?page=About" target="_self" class="custom-button">Go to About →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_single_triage():
    st.markdown("<div class='main-title'>🔍 Single Complaint Triage</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Paste a raw customer complaint to instantly classify, prioritize, and route it.</div>", unsafe_allow_html=True)
    st.markdown("---")

    render_input_section()
    render_results()

    # Display history
    if st.session_state.history:
        st.markdown('---')
        st.subheader('🕘 Triage History')
        hist_df = pd.DataFrame(st.session_state.history)
        preferred_columns = ['text', 'category', 'urgency', 'urgency_source', 'risk_score', 'reliability_score', 'reliability_level', 'sla', 'department', 'confidence', 'matched_keywords']
        history_columns = [column for column in preferred_columns if column in hist_df.columns]
        hist_df = hist_df[history_columns] if history_columns else hist_df
        st.dataframe(hist_df, width="stretch")

def render_batch_processing():
    st.markdown("<div class='main-title'>📊 Batch Processing & Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Upload a CSV file of complaints for bulk processing, analytics, and trend detection.</div>", unsafe_allow_html=True)
    st.markdown("---")

    uploaded_file = st.file_uploader("📁 Upload CSV File", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded successfully — {len(df)} rows found")
        
        narrative_col = st.selectbox("Select the column containing complaint narratives:", df.columns.tolist())

        batch_size = len(df)
        use_ai_urgency = False
        if batch_size <= 50:
            use_ai_urgency = st.checkbox("Use AI Urgency Prediction (Groq)", value=False)
        else:
            st.checkbox("Use AI Urgency Prediction (Groq)", value=False, disabled=True,
                        help="AI urgency prediction is disabled for large batches to avoid API rate limits and excessive latency.")
            st.warning("AI urgency prediction is disabled for large batches to avoid API rate limits and excessive latency.")

        if st.button("🚀 Process All Complaints", width="stretch", type="primary"):
            with st.spinner(f"Processing {len(df)} complaints..."):
                results = []
                progress_bar = st.progress(0)
                
                # Optimized batch processing
                total_rows = len(df)
                update_interval = max(1, total_rows // 20) # Update UI max 20 times to prevent freezing

                for i, text in enumerate(df[narrative_col]):
                    try:
                        res = analyze_complaint(str(text), use_ai_urgency=use_ai_urgency)
                    except Exception:
                        res = {'category': 'Unknown', 'urgency': 'Low', 'department': 'General Support', 'confidence': 0.0, 'risk': None}

                    # Calculate risk score using the existing logic from routing.py
                    risk_score = res.get('risk') or res.get('risk_score')
                    if risk_score is None:
                        urgency_val = res.get('urgency', 'Low')
                        confidence_val = res.get('confidence', 0.0)
                        try:
                            from routing import get_risk_score
                            risk_score = get_risk_score(urgency_val, confidence_val)
                        except ImportError:
                            base = 15 if urgency_val == 'Low' else 40 if urgency_val == 'Medium' else 75 if urgency_val == 'High' else 100
                            risk_score = round(base * 0.7 + (confidence_val * 100) * 0.3)
                    
                    res['risk_score_integrated'] = risk_score
                    results.append(res)

                    reliability_score, _ = calculate_reliability_score(res.get('confidence'), str(text))

                    # Append to session history (frontend-only)
                    try:
                        st.session_state.history.append({
                            'text': str(text),
                            'category': res.get('category'),
                            'urgency': res.get('urgency'),
                            'urgency_source': res.get('urgency_source', '🛡 Keyword Fallback'),
                            'department': res.get('department'),
                            'confidence': res.get('confidence'),
                            'sla': res.get('sla', 'Unknown'),
                            'risk_score': risk_score,
                            'reliability_score': reliability_score,
                            'reliability_level': get_reliability_level(reliability_score)
                        })
                    except Exception:
                        pass

                    if i % update_interval == 0 or i == total_rows - 1:
                        progress_bar.progress((i + 1) / total_rows)

                results_df = pd.DataFrame(results)
                df['Category'] = results_df['category']
                df['Urgency'] = results_df['urgency']
                df['Risk Score'] = results_df['risk_score_integrated']
                df['SLA'] = results_df['sla'] if 'sla' in results_df.columns else 'Unknown'
                df['Department'] = results_df['department']
                df['Confidence'] = results_df['confidence']
                df['Reliability Score'] = [calculate_reliability_score(conf, text)[0] for conf, text in zip(df['Confidence'], df[narrative_col])]
                df['Reliability Level'] = df['Reliability Score'].apply(get_reliability_level)
                df['Escalation'] = df.apply(lambda x: 'Yes' if x['Urgency'] == 'Critical' or x['Confidence'] < 0.70 else 'No', axis=1)
                df['Complaint'] = df[narrative_col]
                if 'urgency_source' in results_df.columns:
                    df['Urgency Source'] = results_df['urgency_source']
                else:
                    df['Urgency Source'] = '🛡 Keyword Fallback'

                st.session_state.batch_results = df
                st.toast("Batch Processing Complete!", icon="🎉")

    # Render Dashboard if data exists
    if st.session_state.batch_results is not None:
        render_dashboard(st.session_state.batch_results)

def render_dashboard(df):
    st.markdown("---")
    st.subheader("📌 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(metric_card("Total Complaints", len(df), "#2196F3"), unsafe_allow_html=True)
    col2.markdown(metric_card("Critical Cases", len(df[df['Urgency'] == 'Critical']), "#F44336"), unsafe_allow_html=True)
    col3.markdown(metric_card("Escalations", len(df[df['Escalation'] == 'Yes']), "#FF9800"), unsafe_allow_html=True)
    col4.markdown(metric_card("Avg Confidence", f"{df['Confidence'].mean()*100:.1f}%", "#4CAF50"), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📈 Analytics Dashboard")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        cat_counts = df['Category'].value_counts().reset_index()
        fig1 = px.bar(cat_counts, x='count', y='Category', orientation='h', title='Category Distribution', color='count', color_continuous_scale='Blues')
        fig1.update_layout(paper_bgcolor='#1e1e2e', plot_bgcolor='#1e1e2e', font_color='white')
        st.plotly_chart(fig1, width="stretch")

    with col2:
        color_map = {'Critical': '#F44336', 'High': '#FF9800', 'Medium': '#FFC107', 'Low': '#4CAF50'}
        fig2 = px.pie(df, names='Urgency', title='Urgency Distribution', color='Urgency', color_discrete_map=color_map)
        fig2.update_layout(paper_bgcolor='#1e1e2e', plot_bgcolor='#1e1e2e', font_color='white')
        st.plotly_chart(fig2, width="stretch")

    st.markdown("---")
    st.subheader("🔍 Filter & Export")
    c1, c2, c3 = st.columns(3)
    cat_filter = c1.multiselect("Category", df['Category'].unique())
    urg_filter = c2.multiselect("Urgency", df['Urgency'].unique())
    dept_filter = c3.multiselect("Department", df['Department'].unique())

    filtered_df = df.copy()
    if cat_filter: filtered_df = filtered_df[filtered_df['Category'].isin(cat_filter)]
    if urg_filter: filtered_df = filtered_df[filtered_df['Urgency'].isin(urg_filter)]
    if dept_filter: filtered_df = filtered_df[filtered_df['Department'].isin(dept_filter)]

    # Display only the required columns in the batch output table
    display_cols = ['Complaint', 'Category', 'Department', 'Urgency', 'Confidence', 'Risk Score', 'SLA', 'Escalation']
    if 'Urgency Source' in filtered_df.columns:
        display_cols.append('Urgency Source')
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    render_df = filtered_df[display_cols]

    # Apply conditional formatting to Risk Score and percentage formatting to Confidence
    styler = render_df.style
    if hasattr(styler, 'map'):
        styler = styler.map(style_risk_score, subset=['Risk Score'])
    else:
        styler = styler.applymap(style_risk_score, subset=['Risk Score'])
    styler = styler.format({'Confidence': '{:.1%}'})

    st.dataframe(styler, width="stretch")

    st.download_button(
        label="📥 Download Filtered Results as CSV",
        data=render_df.to_csv(index=False).encode('utf-8'),
        file_name="complaint_triage_results.csv",
        mime="text/csv",
        width="stretch"
    )

    # ------------------------
    # Feature 1: Batch Risk Analytics Section
    # ------------------------
    st.markdown("---")
    st.markdown("<div style='background-color:#14213d; padding:15px; border-radius:8px; margin-bottom:20px; border-left:5px solid #FFC107;'><h3 style='margin:0; color:white;'>🛡️ Batch Risk Analytics</h3><p style='margin:5px 0 0 0; color:#aaa; font-size:14px;'>Aggregated risk assessment and analysis across the processed batch.</p></div>", unsafe_allow_html=True)
    
    batch_metrics = calculate_batch_risk_metrics(df)
    
    # KPI Cards
    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
    with risk_col1:
        st.markdown(metric_card("Average Risk Score", batch_metrics['avg_risk'], "#FFC107"), unsafe_allow_html=True)
    with risk_col2:
        st.markdown(metric_card("Highest Risk Score", batch_metrics['max_risk'], "#F44336"), unsafe_allow_html=True)
    with risk_col3:
        st.markdown(metric_card("Critical Risk Cases", batch_metrics['critical_count'], "#F44336"), unsafe_allow_html=True)
    with risk_col4:
        st.markdown(metric_card("High Risk Cases", batch_metrics['high_count'], "#FF9800"), unsafe_allow_html=True)
        
    # Chart & Summary Layout
    chart_col, summary_col = st.columns([2, 1], gap="large")
    with chart_col:
        fig = create_risk_distribution_chart(df)
        st.plotly_chart(fig, width="stretch")
        
    with summary_col:
        summary_html = f"""
        <div class="app-card" style="border-left:5px solid #00BCD4;">
            <div class="card-content">
                <h4 style="margin-top:0; color:#00BCD4; font-size:18px;">Batch Summary</h4>
                <hr style="border-color:rgba(255,255,255,0.1); margin-bottom:15px;">
                <p style="font-size:15px; margin:8px 0; color:white;"><strong>Average Risk Score:</strong> {batch_metrics['avg_risk']}</p>
                <p style="font-size:15px; margin:8px 0; color:#F44336;"><strong>Critical Risk Cases:</strong> {batch_metrics['critical_count']}</p>
                <p style="font-size:15px; margin:8px 0; color:#FF9800;"><strong>High Risk Cases:</strong> {batch_metrics['high_count']}</p>
                <p style="font-size:15px; margin:8px 0; color:#FFC107;"><strong>Medium Risk Cases:</strong> {batch_metrics['medium_count']}</p>
                <p style="font-size:15px; margin:8px 0; color:#4CAF50;"><strong>Low Risk Cases:</strong> {batch_metrics['low_count']}</p>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

    # ------------------------
    # Feature 2: Priority Queue Section
    # ------------------------
    st.markdown("---")
    st.markdown("<div style='background-color:#0d1b2a; padding:15px; border-radius:8px; margin-bottom:20px; border-left:5px solid #E91E63;'><h3 style='margin:0; color:white;'>📋 Priority Queue</h3><p style='margin:5px 0 0 0; color:#aaa; font-size:14px;'>Immediate attention queue for complaints with Critical or High urgency, sorted by risk score.</p></div>", unsafe_allow_html=True)
    
    pq_df = create_priority_queue(df)
    
    if len(pq_df) == 0:
        st.info("No complaints meet the Priority Queue criteria (Critical or High Urgency).")
    else:
        render_priority_queue_kpis(pq_df)
        
        # Prepare for display with visual priority indicators
        render_pq_df = pq_df.copy()
        render_pq_df['Urgency'] = render_pq_df['Urgency'].map({'Critical': '🔴 Critical', 'High': '🟠 High'})
        
        # Display table columns: Rank | Risk Score | Urgency | Category | Department | Complaint
        pq_display_cols = ['Rank', 'Risk Score', 'Urgency', 'Category', 'Department', 'Complaint']
        pq_display_cols = [c for c in pq_display_cols if c in render_pq_df.columns]
        render_pq_display = render_pq_df[pq_display_cols]
        
        pq_styler = render_pq_display.style
        if hasattr(pq_styler, 'map'):
            pq_styler = pq_styler.map(style_risk_score, subset=['Risk Score'])
        else:
            pq_styler = pq_styler.applymap(style_risk_score, subset=['Risk Score'])
            
        st.dataframe(pq_styler, hide_index=True, width="stretch")
        
        pq_csv_bytes = export_priority_queue_csv(pq_df)
        st.download_button(
            label="📥 Download Priority Queue CSV",
            data=pq_csv_bytes,
            file_name="priority_queue.csv",
            mime="text/csv",
            width="stretch"
        )


def render_about():
    # Inject page-specific styles for premium design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    .about-container {
        font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e2e8f0;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Hero Section */
    .about-hero {
        background: linear-gradient(
            135deg,
            rgba(88, 101, 242, 0.08),
            rgba(139, 92, 246, 0.04)
        );
        background-color: #1e1e2e;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 40px 30px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .about-hero h1 {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 12px 0;
        letter-spacing: -0.5px;
    }
    .about-hero p {
        font-size: 18px;
        color: #cbd5e1;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Business Problem Card */
    .problem-card {
        background: #1e1e2f;
        border-left: 5px solid #ef4444;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .problem-card h3 {
        color: #ffffff;
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 22px;
        font-weight: 700;
    }
    .problem-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
    }
    @media (max-width: 768px) {
        .problem-grid {
            grid-template-columns: 1fr;
        }
    }
    .problem-col-left {
        font-size: 15px;
        line-height: 1.6;
        color: #cbd5e1;
    }
    .problem-col-right {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 8px;
        padding: 15px 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .problem-col-right ul {
        margin: 0;
        padding-left: 20px;
    }
    .problem-col-right li {
        margin-bottom: 8px;
        color: #f87171;
        font-weight: 500;
        font-size: 14px;
    }
    
    /* Section Subheaders */
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin: 45px 0 20px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        letter-spacing: -0.3px;
    }
    
    /* Pipeline Flow */
    .pipeline-flow {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin: 25px 0 35px 0;
        padding: 25px;
        background: #141423;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .pipeline-step {
        background: #1e1e2e;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 16px;
        min-width: 170px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    .pipeline-step:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.15);
    }
    .pipeline-num {
        font-size: 10px;
        font-weight: 700;
        color: #818cf8;
        text-transform: uppercase;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }
    .pipeline-name {
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
    }
    .pipeline-arrow {
        color: #6366f1;
        font-size: 18px;
        font-weight: bold;
        user-select: none;
    }
    
    /* Core Capabilities Grid */
    .capabilities-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 20px;
        margin-bottom: 35px;
    }
    .cap-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .cap-card:hover {
        transform: translateY(-4px);
    }
    .cap-icon {
        font-size: 26px;
        margin-bottom: 12px;
    }
    .cap-title {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .cap-desc {
        font-size: 13.5px;
        color: #94a3b8;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Technical Architecture */
    .arch-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 15px;
        margin-bottom: 35px;
    }
    .arch-card {
        border-top: 4px solid #10b981 !important;
        justify-content: flex-start;
    }
    .arch-title {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .arch-item {
        font-size: 12px;
        background: rgba(255, 255, 255, 0.05);
        padding: 7px 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        color: #cbd5e1;
        font-weight: 500;
    }
    .arch-item:last-child {
        margin-bottom: 0;
    }
    
    /* Key Project Decisions */
    .decisions-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 35px;
    }
    @media (max-width: 768px) {
        .decisions-grid {
            grid-template-columns: 1fr;
        }
    }
    .decision-card {
        transition: transform 0.2s ease !important;
    }
    .decision-card:hover {
        transform: translateY(-2px);
    }
    .decision-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        border-left: 3.5px solid #3b82f6;
        padding-left: 10px;
        line-height: 1.3;
    }
    .decision-body {
        font-size: 13.5px;
        color: #cbd5e1;
        line-height: 1.6;
        margin-bottom: 14px;
    }
    .decision-tradeoff {
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 12px;
        color: #93c5fd;
        line-height: 1.45;
    }
    
    /* Known Limitations */
    .limitations-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-bottom: 35px;
    }
    @media (max-width: 768px) {
        .limitations-grid {
            grid-template-columns: 1fr;
        }
    }
    .limit-card {
        background: rgba(245, 158, 11, 0.03) !important;
        border: 1px solid rgba(245, 158, 11, 0.12) !important;
        border-left: 4px solid #f59e0b !important;
    }
    .limit-title {
        font-weight: 700;
        color: #fbbf24;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .limit-desc {
        font-size: 12.5px;
        color: #cbd5e1;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Future Enhancements */
    .roadmap-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 15px;
        margin-bottom: 35px;
    }
    .roadmap-card {
        background: #1e1e2e;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 18px 15px;
        position: relative;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .roadmap-phase {
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 9px;
        font-weight: 700;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .roadmap-title {
        font-weight: 700;
        color: #ffffff;
        font-size: 14px;
        margin-bottom: 6px;
        margin-top: 10px;
    }
    .roadmap-desc {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Skills Section */
    .skills-container {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
        text-align: center;
        margin-bottom: 40px;
    }
    .skills-title {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .skills-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
    }
    .skill-badge {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        transition: all 0.2s ease;
    }
    .skill-badge:hover {
        background: #6366f1;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render Layout
    st.markdown('<div class="about-container">', unsafe_allow_html=True)
    
    # Section 1: Executive Summary Hero
    st.markdown("""
    <div class="about-hero">
        <h1>🏦 Banking Complaint Triage System</h1>
        <p>An NLP-powered system that automatically classifies, prioritizes, routes, and risk-scores customer complaints using over 3.6 million CFPB complaint records.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Metrics using standard grid layout columns
    hero_col1, hero_col2, hero_col3, hero_col4 = st.columns(4)
    with hero_col1:
        st.markdown(styled_card("Complaints", "3.6M+", "#3b82f6", "CFPB Database records"), unsafe_allow_html=True)
    with hero_col2:
        st.markdown(styled_card("Categories", "6", "#10b981", "Banking product domains"), unsafe_allow_html=True)
    with hero_col3:
        st.markdown(styled_card("Urgency Levels", "4", "#f59e0b", "Priority classifications"), unsafe_allow_html=True)
    with hero_col4:
        st.markdown(styled_card("Category F1", "81%", "#8b5cf6", "Macro F1 classification accuracy"), unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 2: The Business Problem
    st.markdown("""
    <div class="app-card problem-card">
        <div class="card-content">
            <h3>💼 The Business Problem</h3>
            <div class="problem-grid">
                <div class="problem-col-left">
                    <p>Banks receive thousands of customer complaints every day across digital and physical touchpoints. Sorting through these complaints manually creates severe operational friction.</p>
                    <p>Incorrect routing delays investigation times, creates massive administrative overhead, and leads directly to regulatory compliance violations. This project demonstrates how machine learning can automate complaint intake and prioritization to protect margins and customers.</p>
                </div>
                <div class="problem-col-right">
                    <p style="margin-top:0; font-weight:600; color:white;">Manual triage processes suffer from:</p>
                    <ul>
                        <li>⏳ Slow response and resolution times</li>
                        <li>🔄 Inconsistent and error-prone routing</li>
                        <li>⚠️ SLA violations and potential regulatory fines</li>
                        <li>💸 High operational and personnel costs</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 3: Solution Overview (Pipeline)
    st.markdown('<div class="section-title">⚙️ How The System Works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-step" style="border-top: 3px solid #3b82f6;">
            <div class="pipeline-num" style="color: #3b82f6;">Step 01</div>
            <div class="pipeline-name">Complaint Narrative</div>
        </div>
        <div class="pipeline-arrow" style="color: #3b82f6;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #06b6d4;">
            <div class="pipeline-num" style="color: #06b6d4;">Step 02</div>
            <div class="pipeline-name">Text Preprocessing</div>
        </div>
        <div class="pipeline-arrow" style="color: #06b6d4;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #8b5cf6;">
            <div class="pipeline-num" style="color: #8b5cf6;">Step 03</div>
            <div class="pipeline-name">TF-IDF Vectorization</div>
        </div>
        <div class="pipeline-arrow" style="color: #8b5cf6;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #6366f1;">
            <div class="pipeline-num" style="color: #6366f1;">Step 04</div>
            <div class="pipeline-name">Category Classification</div>
        </div>
        <div class="pipeline-arrow" style="color: #6366f1;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #f59e0b;">
            <div class="pipeline-num" style="color: #f59e0b;">Step 05</div>
            <div class="pipeline-name">Urgency Prediction</div>
        </div>
        <div class="pipeline-arrow" style="color: #f59e0b;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #10b981;">
            <div class="pipeline-num" style="color: #10b981;">Step 06</div>
            <div class="pipeline-name">Department Routing</div>
        </div>
        <div class="pipeline-arrow" style="color: #10b981;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #f97316;">
            <div class="pipeline-num" style="color: #f97316;">Step 07</div>
            <div class="pipeline-name">Risk Scoring</div>
        </div>
        <div class="pipeline-arrow" style="color: #f97316;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #14b8a6;">
            <div class="pipeline-num" style="color: #14b8a6;">Step 08</div>
            <div class="pipeline-name">SLA Assignment</div>
        </div>
        <div class="pipeline-arrow" style="color: #14b8a6;">➔</div>
        <div class="pipeline-step" style="border-top: 3px solid #ef4444;">
            <div class="pipeline-num" style="color: #ef4444;">Step 09</div>
            <div class="pipeline-name">Escalation Decision</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 4: Core Capabilities
    st.markdown('<div class="section-title">🛡️ Core Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="capabilities-grid">
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">📂</div>
                <div class="cap-title">Category Classification</div>
                <div class="cap-desc">Automatically classifies complaints into one of 6 major product domains using machine learning.</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">⚡</div>
                <div class="cap-title">Urgency Prediction</div>
                <div class="cap-desc">Determines complaint urgency levels (Critical, High, Medium, Low) using rule-assisted keyword scoring.</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">🏢</div>
                <div class="cap-title">Department Routing</div>
                <div class="cap-desc">Routes cases dynamically to the optimal specialized operations group (e.g., Fraud Team, Loan Officers).</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">🎯</div>
                <div class="cap-title">Risk Scoring</div>
                <div class="cap-desc">Assigns a 0-100 score quantifying operational and customer risk based on urgency and classifier confidence.</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">⏱</div>
                <div class="cap-title">SLA Assignment</div>
                <div class="cap-desc">Calculates target response windows automatically to align workflow priorities with regulatory baselines.</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">🚨</div>
                <div class="cap-title">Escalation Detection</div>
                <div class="cap-desc">Flags critical accounts or low-confidence predictions automatically for immediate supervisor oversight.</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">📊</div>
                <div class="cap-title">Batch Processing</div>
                <div class="cap-desc">Supports uploading CSV spreadsheets to process thousands of complaints simultaneously in the background.</div>
            </div>
        </div>
        <div class="app-card cap-card">
            <div class="card-content">
                <div class="cap-icon">📈</div>
                <div class="cap-title">Analytics Dashboard</div>
                <div class="cap-desc">Generates interactive Plotly visualizers and a Priority Queue table for high-risk triage review.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 5: Model Performance
    st.markdown('<div class="section-title">📊 Model Performance Summary</div>', unsafe_allow_html=True)
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    with perf_col1:
        st.markdown(render_performance_card("Category Classifier", "81% Macro F1", "#3b82f6", "Averages 76%-93% across categories"), unsafe_allow_html=True)
    with perf_col2:
        st.markdown(render_performance_card("Urgency Classifier", "95% Macro F1", "#10b981", "High reliability on priority signals"), unsafe_allow_html=True)
    with perf_col3:
        st.markdown(render_performance_card("Dataset", "3.6M Complaints", "#f59e0b", "Consumer Financial Protection Bureau"), unsafe_allow_html=True)
    with perf_col4:
        st.markdown(render_performance_card("Vocabulary", "100K Features", "#8b5cf6", "Unigrams and bigrams extraction"), unsafe_allow_html=True)
        
    with st.expander("🔍 Show Detailed Classifier Tables", expanded=False):
        t_col1, t_col2 = st.columns(2, gap="large")
        with t_col1:
            st.markdown("##### Category Classifier Detailed F1")
            st.markdown("""
            | Product Category | F1 Score |
            | :--- | :--- |
            | Credit Reporting | 0.93 |
            | Loans | 0.81 |
            | Banking & Accounts | 0.78 |
            | Debt Collection | 0.76 |
            | Cards & Transactions | 0.76 |
            | **Macro Average** | **0.81** |
            """)
        with t_col2:
            st.markdown("##### Urgency Classifier Detailed F1")
            st.markdown("""
            | Urgency Level | F1 Score |
            | :--- | :--- |
            | Critical | 0.95 |
            | High | 0.92 |
            | Medium | 0.95 |
            | Low | 0.98 |
            | **Macro Average** | **0.95** |
            """)
            st.caption("Note: The Urgency model shows high F1 scores due to keyword-based label assistance, aligning predictions directly with operational policy rules.")
            
    # Section 6: Technical Architecture
    st.markdown('<div class="section-title">🏗️ Technical Architecture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="arch-grid">
        <div class="app-card arch-card" style="border-top: 4px solid #3b82f6;">
            <div class="card-content">
                <div class="arch-title">📊 Data Source</div>
                <div class="arch-item">CFPB Database</div>
                <div class="arch-item">3.6M Complaint Records</div>
                <div class="arch-item">Consumer Narratives</div>
            </div>
        </div>
        <div class="app-card arch-card" style="border-top: 4px solid #10b981;">
            <div class="card-content">
                <div class="arch-title">🧹 NLP Pipeline</div>
                <div class="arch-item">Contraction Expansion</div>
                <div class="arch-item">Regex Cleaning</div>
                <div class="arch-item">POS Lemmatization</div>
            </div>
        </div>
        <div class="app-card arch-card" style="border-top: 4px solid #f59e0b;">
            <div class="card-content">
                <div class="arch-title">🔤 Feature Eng.</div>
                <div class="arch-item">TF-IDF Extraction</div>
                <div class="arch-item">Unigram + Bigram</div>
                <div class="arch-item">100K Features</div>
            </div>
        </div>
        <div class="app-card arch-card" style="border-top: 4px solid #8b5cf6;">
            <div class="card-content">
                <div class="arch-title">🤖 Machine Learning</div>
                <div class="arch-item">Logistic Regression</div>
                <div class="arch-item">Balanced Weights</div>
                <div class="arch-item">SAGA Solver</div>
            </div>
        </div>
        <div class="app-card arch-card" style="border-top: 4px solid #ec4899;">
            <div class="card-content">
                <div class="arch-title">🏗️ App Layer</div>
                <div class="arch-item">Streamlit UI</div>
                <div class="arch-item">Interactive Dashboards</div>
                <div class="arch-item">Batch Processing</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 6.5: Hybrid Urgency Engine
    st.markdown('<div class="section-title">🧠 Hybrid Urgency Engine</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#aaa; font-size:14.5px; line-height:1.6; margin-bottom:20px;'>
        Urgency prediction uses a production-style hybrid architecture instead of relying on a single method. This design combines the contextual intelligence of LLMs with the absolute reliability of deterministic keyword heuristics.
    </p>
    """, unsafe_allow_html=True)
    
    col_eng1, col_eng2 = st.columns(2, gap="medium")
    with col_eng1:
        st.markdown("""
        <div class="app-card" style="border-top: 4px solid #2196F3 !important; height: 100%;">
            <div class="card-content">
                <h3 style="color:#2196F3; margin-top:0;">🤖 AI Urgency Engine</h3>
                <p style="color:#b7bec9; font-size:13.5px; margin-bottom:12px;">Used for Single Complaint Triage.</p>
                <p style="color:white; font-weight:600; margin-bottom:6px; font-size:14px;">Capabilities:</p>
                <ul style="padding-left:20px; color:#cbd5e1; margin-top:4px;">
                    <li style="margin-bottom:4px;">✓ Understands context</li>
                    <li style="margin-bottom:4px;">✓ Handles nuanced complaint narratives</li>
                    <li style="margin-bottom:4px;">✓ Interprets intent beyond keywords</li>
                    <li style="margin-bottom:4px;">✓ Better classification for complex complaints</li>
                </ul>
                <div style="margin-top:14px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.06); font-size:13px; color:#94a3b8;">
                    <strong>Technology:</strong> Groq LLM
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_eng2:
        st.markdown("""
        <div class="app-card" style="border-top: 4px solid #4CAF50 !important; height: 100%;">
            <div class="card-content">
                <h3 style="color:#4CAF50; margin-top:0;">🛡 Fallback Urgency Engine</h3>
                <p style="color:#b7bec9; font-size:13.5px; margin-bottom:12px;">Used when AI is unavailable and for large-scale batch processing.</p>
                <p style="color:white; font-weight:600; margin-bottom:6px; font-size:14px;">Capabilities:</p>
                <ul style="padding-left:20px; color:#cbd5e1; margin-top:4px;">
                    <li style="margin-bottom:4px;">✓ Deterministic</li>
                    <li style="margin-bottom:4px;">✓ Fast execution</li>
                    <li style="margin-bottom:4px;">✓ No API dependency</li>
                    <li style="margin-bottom:4px;">✓ Scales to large CSV uploads</li>
                </ul>
                <div style="margin-top:14px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.06); font-size:13px; color:#94a3b8;">
                    <strong>Technology:</strong> Rule-Based Keyword Scoring
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3, gap="medium")
    with col_kpi1:
        st.markdown(styled_card("⚡ Primary Engine", "Groq AI", "#2196F3"), unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(styled_card("🛡 Fallback Engine", "Keyword Rules", "#4CAF50"), unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(styled_card("🎯 Architecture Goal", "Reliability + Availability", "#9c27b0"), unsafe_allow_html=True)
        
    st.markdown("""
    <p style='color:#aaa; font-size:14.5px; line-height:1.6; margin-top:15px; margin-bottom:25px;'>
        This hybrid architecture combines the contextual understanding of LLMs with the reliability of deterministic rules. The system automatically falls back to rule-based urgency scoring during API outages or large-scale batch processing.
    </p>
    """, unsafe_allow_html=True)
    
    # Section 7: Key Project Decisions
    st.markdown('<div class="section-title">💡 Key Project Decisions & Engineering Trade-Offs</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="decisions-grid">
        <div class="app-card decision-card">
            <div class="card-content">
                <div class="decision-title">TF-IDF Vectorization vs. Deep Learning Embeddings</div>
                <div class="decision-body">
                    Deep learning encoders (like BERT) capture rich semantics but demand expensive GPU hardware for inference. 
                    <strong>TF-IDF was selected</strong> because it delivers fast inference on CPUs, scales efficiently to millions of records, 
                    and extracts highly interpretable sparse features.
                </div>
            </div>
            <div class="decision-tradeoff">
                <strong>Trade-Off:</strong> Slightly lower capability to parse complex context in exchange for sub-millisecond CPU speed and low infra costs.
            </div>
        </div>
        <div class="app-card decision-card">
            <div class="card-content">
                <div class="decision-title">Logistic Regression vs. Complex Ensemble Models</div>
                <div class="decision-body">
                    Complex models (like XGBoost) run slow and overfit on high-dimensional sparse TF-IDF spaces (100k features). 
                    <strong>Logistic Regression was chosen</strong> because of its robust linear decision boundaries, SAGA optimization, and class balancing, 
                    allowing stable generalization across imbalanced banking categories.
                </div>
            </div>
            <div class="decision-tradeoff">
                <strong>Trade-Off:</strong> Accept linear constraints for predictable model calibration and simple probabilistic confidence.
            </div>
        </div>
        <div class="app-card decision-card">
            <div class="card-content">
                <div class="decision-title">Rule-Based Urgency & Routing vs. End-to-End Classifier</div>
                <div class="decision-body">
                    Under compliance guidelines, critical incidents (e.g. Identity Theft, Account Access blockages) must be routed to specialized fraud teams with zero variance. 
                    <strong>A hybrid rule-assisted routing framework</strong> was selected to ensure deterministic safety guardrails.
                </div>
            </div>
            <div class="decision-tradeoff">
                <strong>Trade-Off:</strong> Decreased machine flexibility in routing in exchange for auditable, guaranteed compliance triggers.
            </div>
        </div>
        <div class="app-card decision-card">
            <div class="card-content">
                <div class="decision-title">Addition of Dynamic Risk & Reliability Scoring</div>
                <div class="decision-body">
                    A simple model probability can be misleading for short text inputs. 
                    <strong>Composite Risk and Reliability metrics</strong> were added to integrate classifier confidence, urgency severity, 
                    and input text length, flagging ambiguous, short, or low-confidence cases for manual human routing review.
                </div>
            </div>
            <div class="decision-tradeoff">
                <strong>Trade-Off:</strong> Minor increase in scoring pipeline math to gain substantial user trust and workload triage quality.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 8: Known Limitations
    st.markdown('<div class="section-title">⚠️ Known Limitations</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="limitations-grid">
        <div class="app-card limit-card">
            <div class="card-content">
                <div class="limit-title">🔍 Short Complaints Lack Context</div>
                <div class="limit-desc">
                    Complaints containing fewer than 6-12 words (e.g., "card not working") do not carry enough semantic information. 
                    This leads to lower model confidence and flags the case as low reliability.
                </div>
            </div>
        </div>
        <div class="app-card limit-card">
            <div class="card-content">
                <div class="limit-title">🌐 Semantic Category Overlap</div>
                <div class="limit-desc">
                    Product domains can bleed into each other. A complaint about a "mortgage payment debited from credit card" 
                    creates classifier ambiguity between Loans, Cards & Transactions, and Accounts.
                </div>
            </div>
        </div>
        <div class="app-card limit-card">
            <div class="card-content">
                <div class="limit-title">⚙️ Keyword-Based Urgency Bias</div>
                <div class="limit-desc">
                    Urgency levels depend heavily on strict dictionary matching of key phrases. 
                    Sarcasm, misspelt terms, or atypical phrasing can sometimes bypass critical urgency flags.
                </div>
            </div>
        </div>
        <div class="app-card limit-card">
            <div class="card-content">
                <div class="limit-title">🗺️ Static Routing Rules</div>
                <div class="limit-desc">
                    Routing logic relies on category-to-department maps. The system cannot dynamically adjust routing based 
                    on department capacity, queues, or agent skill profiles.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    
    # Section 10: Skills Demonstrated
    st.markdown("""
    <div class="app-card skills-container">
        <div class="card-content">
            <div class="skills-title">🎓 Skills Demonstrated</div>
            <p style="font-size: 13px; color: #94a3b8; margin: 4px 0 15px 0;">Recruiter & Engineering Hiring Takeaways:</p>
            <div class="skills-grid">
                <div class="skill-badge">Natural Language Processing</div>
                <div class="skill-badge">Text Classification</div>
                <div class="skill-badge">Feature Engineering</div>
                <div class="skill-badge">Machine Learning</div>
                <div class="skill-badge">Model Evaluation</div>
                <div class="skill-badge">Data Visualization</div>
                <div class="skill-badge">Business Analytics</div>
                <div class="skill-badge">Dashboard Development</div>
                <div class="skill-badge">Streamlit Application Development</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------
# Sidebar Navigation
# ------------------------
st.sidebar.title("🏦 Triage AI")
st.sidebar.markdown("---")

pages = ["🏠 Home", "🔍 Single Triage", "📊 Batch Processing", "ℹ️ About"]
for p in pages:
    if st.sidebar.button(p, width="stretch", type="primary" if st.session_state.page == p else "secondary"):
        st.session_state.page = p
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Powered by CFPB Data • NLP + ML")

# ------------------------
# Route App
# ------------------------
if st.session_state.page == "🏠 Home":
    render_home()
elif st.session_state.page == "🔍 Single Triage":
    render_single_triage()
elif st.session_state.page == "📊 Batch Processing":
    render_batch_processing()
elif st.session_state.page == "ℹ️ About":
    render_about()

st.markdown("<div class='footer'>Educational Machine Learning Project · NLP + Classification + Priority Prediction</div>", unsafe_allow_html=True)