import os
import re
import requests
import logging

# Ensure basic logging configuration so that messages are recorded in app.log and stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("urgency")

try:
    import streamlit as st
    cache_decorator = st.cache_data(show_spinner=False)
except Exception:
    def cache_decorator(func):
        return func

severity_keywords = {
    "Critical": [
        "identity theft",
        "identity theft report",
        "eviction",
        "evicted",
        "eviction notice",
        "nsf",
        "account closed without",
        "facing eviction",
        "late fees accumulating",
        "account hacked",
        "hacked",
        "account takeover",
        "takeover",
        "unauthorized access",
        "unauthorized withdrawal",
        "unauthorized transaction",
        "frozen account",
        "frozen",
        "data breach",
        "breach",
        "compromised",
        "legal action",
        "foreclosure",
        "drained",
        "emptied",
        "stolen",
        "medical emergency",
        "emergency",
        "cannot pay rent",
        "unable to buy food",
        "utility shutoff",
        "fraudulent",
        "cannot access",
        "rent due",
        "no other way to pay",
        "due tomorrow",
        "funds locked",
        "not access",
        "no way pay",
        "fund lock"
    ],

    "High": [
        "fraud",
        "theft",
        "victim",
        "unauthorized charge",
        "credit report error",
        "credit damage",
        "score dropped",
        "payment dispute",
        "account restriction",
        "restriction",
        "financial loss",
        "loss",
        "refused refund",
        "refund",
        "unresolved dispute",
        "harassment",
        "multiple calls",
        "supervisor",
        "escalate",
        "repeatedly ignored",
        "ignored",
        "repossession",
        "overdraft",
        "charged-off",
        "credit denied",
        "loan denied",
        "mortgage denied",
        "wage garnishment",
        "being targeted",
        "unknown creditor",
        "do not know who",
        "collection scam",
        "suspicious email",
        "not authorized",
        "without my consent",
        "not approve",
        "blocked and removed",
        "did not approve",
        "reported as delinquent",
        "credit score dropped",
        "applied to wrong account",
        "on time payment",
        "misapplied",
        "report delinquent",
        "apply wrong account",
        "misapply",
        "money disappeared",
        "money lost",
        "money missing",
        "never arrived",
        "never received",
        "lost money",

    ],

    "Medium": [
        "incorrect information",
        "billing confusion",
        "confusion",
        "customer service",
        "long wait",
        "delayed response",
        "statement error",
        "technical issue",
        "technical",
        "service interruption",
        "interruption",
        "communication problem",
        "communication",
        "verification issue",
        "verification",
        "validate",
        "validation",
        "do not owe",
        "billing error",
        "billing",
        "wrong charge",
        "app not working",
        "login issue",
        "login",
        "incorrect charge",
        "delayed",
        "not received",
        "website",
        "processing",
        "remove from credit report",
        "remove from my report",
        "remove account",
        "second request",
        "second time",
        "fcra",
        "violation",
        "without my knowledge",
        "without consent",
        "did not authorize",
        "unauthorized entries",
        "not give written permission",
        "already paid",
        "have receipt",
        "paid in full",
        "collections notice",
        "paid two years ago",
        "proof of payment",
        "already pay",
        "collection notice",
        "receipt",
        "pay full",
        "proof payment",
        "late fee"
    ],

    "Low": [
        "address update",
        "document request",
        "status inquiry",
        "inquiry",
        "general inquiry",
        "information request",
        "account maintenance",
        "maintenance",
        "profile update",
        "profile",
        "password reset",
        "reset",
        "application status",
        "account verification",
        "please confirm",
        "requesting statement",
        "account setup",
        "setup",
        "how do i",
        "would like to know",
        "clarification",
        "assistance",
        "question",
        "hard inquiry",
        "hard inquiries"
    ]
}

severity_weights = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}


def urgency_level(text, return_details=False):

    text = str(text).lower()

    scores = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    matched_keywords = []

    for level, keywords in severity_keywords.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                scores[level] += severity_weights[level]
                matched_keywords.append(keyword)

    # No keyword matched
    if sum(scores.values()) == 0:
        severity = "Low"

    # Critical events should dominate
    elif scores["Critical"] >= 8:
        severity = "Critical"

    # Strong High signal
    elif scores["High"] >= 6:
        severity = "High"

    # Medium signal
    elif scores["Medium"] >= 4:
        severity = "Medium"

    # Fallback to highest score
    else:
        priority = ["Critical", "High", "Medium", "Low"]

        max_score = max(scores.values())

        for level in priority:
            if scores[level] == max_score:
                severity = level
                break

    if return_details:
        return {
            "urgency_level": severity,
            "matched_keywords": matched_keywords
        }

    return severity


def get_groq_api_key():
    """
    Retrieves the Groq API key from streamlit secrets, environment variables,
    or manually parses .env and .streamlit/secrets.toml if available.
    """
    # 1. Try streamlit secrets
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    # 2. Try environment variables
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
        
    # 3. Try to read from .env file manually
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2 and parts[0].strip() == "GROQ_API_KEY":
                            val = parts[1].strip().strip("'\"")
                            return val
        except Exception as e:
            logger.debug(f"Failed to parse .env file: {e}")
            
    # 4. Try to read from .streamlit/secrets.toml manually
    if os.path.exists(".streamlit/secrets.toml"):
        try:
            with open(".streamlit/secrets.toml", "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2 and parts[0].strip() == "GROQ_API_KEY":
                            val = parts[1].strip().strip("'\"")
                            return val
        except Exception as e:
            logger.debug(f"Failed to parse secrets.toml: {e}")
            
    return None


@cache_decorator
def _call_groq_api(text, api_key):
    import json # Imported here to ensure it's available
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {
                "role": "system",
                "content": "You are a banking complaint triage classifier. Extract the urgency level from the user's complaint."
            },
            {
                "role": "user",
                "content": str(text).strip() or "No complaint provided."
            }
        ],
        "temperature": 0.0,
        "max_completion_tokens": 2048, # Updated from the deprecated max_tokens
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "urgency_classification",
                "strict": True, # Enforces strict schema compliance
                "schema": {
                    "type": "object",
                    "properties": {
                        "urgency": {
                            "type": "string",
                            "enum": ["Critical", "High", "Medium", "Low"]
                        }
                    },
                    "required": ["urgency"],
                    "additionalProperties": False
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    
    if response.status_code == 200:
        res_json = response.json()
        raw_response = res_json["choices"][0]["message"]["content"]
        
        try:
            # Parse the guaranteed JSON output
            parsed_data = json.loads(raw_response)
            cleaned_response = parsed_data.get("urgency", "").strip()
        except Exception:
            cleaned_response = ""
            
        VALID_URGENCY = {"Critical", "High", "Medium", "Low"}
        
        if cleaned_response in VALID_URGENCY:
            return cleaned_response
        else:
            raise ValueError(f"Invalid urgency level response: '{raw_response}'")
    else:
        raise Exception(f"HTTP error {response.status_code}: {response.text}")

def predict_urgency_groq(text, return_source=False):
    """
    Predicts complaint urgency using Groq API.
    Falls back to the keyword-based urgency engine (urgency_level) in case of any failures.
    """
    api_key = get_groq_api_key()
    if not api_key:
        logger.warning("Groq API key is missing. Falling back to keyword urgency.")
        fallback_val = urgency_level(text)
        if return_source:
            return fallback_val, "🛡 Keyword Fallback"
        return fallback_val

    try:
        cleaned_response = _call_groq_api(text, api_key)
        logger.info(f"Groq API success: predicted '{cleaned_response}' urgency.")
        if return_source:
            return cleaned_response, "🤖 Groq AI"
        return cleaned_response
            
    except Exception as e:
        logger.error(f"Groq API call failed: {e}. Falling back to keyword urgency.")
        fallback_val = urgency_level(text)
        if return_source:
            return fallback_val, "🛡 Keyword Fallback"
        return fallback_val



