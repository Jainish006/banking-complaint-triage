from preprocessing import clean_preprocessed_text
from routing import get_department, get_sla,get_risk_score
from urgency import urgency_level, predict_urgency_groq
from config import CATEGORY_MODEL_PATH, CATEGORY_VECTORIZER_PATH
import joblib
import warnings
warnings.filterwarnings('ignore')

lr_full = joblib.load(CATEGORY_MODEL_PATH)
vectorizer_full = joblib.load(CATEGORY_VECTORIZER_PATH)   
def analyze_complaint(text, use_ai_urgency=True, return_details=False):

    if use_ai_urgency:
        urgency, urgency_source = predict_urgency_groq(text, return_source=True)
    else:
        urgency = urgency_level(text)
        urgency_source = "🛡 Keyword Fallback"

    if return_details:
        urgency_result = urgency_level(text, return_details=True)
        matched_keywords = urgency_result["matched_keywords"]
    else:
        matched_keywords = []

    sla = get_sla(urgency)

    cleaned_text = clean_preprocessed_text(text)

    transformed_text = vectorizer_full.transform([cleaned_text])

    predicted_category = lr_full.predict(transformed_text)[0]

    department = get_department(predicted_category, urgency)

    model_confidence = lr_full.predict_proba(transformed_text)[0].max()

    risk = get_risk_score(urgency, model_confidence)
    escalation_flag = urgency == "Critical"

    result = {
        'category': predicted_category,
        'urgency': urgency,
        'department': department,
        'risk': risk,
        'escalation_flag': escalation_flag,
        'confidence': model_confidence,
        'sla': sla,
        'urgency_source': urgency_source
    }

    if return_details:
        result['urgency_level'] = urgency
        result['matched_keywords'] = matched_keywords

    return result