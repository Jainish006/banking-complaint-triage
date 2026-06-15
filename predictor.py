from preprocessing import clean_preprocessed_text
from routing import get_department, get_sla,get_risk_score
from urgency import urgency_level
from config import CATEGORY_MODEL_PATH, CATEGORY_VECTORIZER_PATH
import joblib
import warnings
warnings.filterwarnings('ignore')

lr_full = joblib.load(CATEGORY_MODEL_PATH)
vectorizer_full = joblib.load(CATEGORY_VECTORIZER_PATH)   
def analyze_complaint(text, return_details=False):

    urgency_result = urgency_level(text, return_details=return_details)
    if return_details:
        urgency = urgency_result["urgency_level"]
        matched_keywords = urgency_result["matched_keywords"]
    else:
        urgency = urgency_result
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
        'sla': sla
    }

    if return_details:
        result['urgency_level'] = urgency
        result['matched_keywords'] = matched_keywords

    return result