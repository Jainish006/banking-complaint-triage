routing_map = {
    "Credit Reporting": {
        "Critical": "Fraud & Identity Protection",
        "High": "Fraud & Identity Protection",
        "Medium": "Credit Reporting Support",
        "Low": "Credit Reporting Support"
    },
    "Loans": {
        "Critical": "Emergency Loan Services",
        "High": "Loan Resolution Team",
        "Medium": "Standard Loan Servicing",
        "Low": "Standard Loan Servicing"
    },
    "Cards & Transactions": {
        "Critical": "Card Fraud Team",
        "High": "Card Disputes Team",
        "Medium": "Card Services Support",
        "Low": "Card Services Support"
    },
    "Banking & Accounts": {
        "Critical": "Account Security Team",
        "High": "Account Resolution Team",
        "Medium": "Account Services Support",
        "Low": "Account Services Support"
    },
    "Debt Collection": {
        "Critical": "Legal & Collections Team",
        "High": "Legal & Collections Team",
        "Medium": "Collections Support",
        "Low": "Collections Support"
    },
    "Money Transfer & Payments": {
        "Critical": "Payment Fraud Team",
        "High": "Payment Investigation Team",
        "Medium": "Payment Services Support",
        "Low": "Payment Services Support"
    }
}


def get_department(category,urgency):

    return routing_map[category][urgency]


sla_map = {
    'Critical': '2 Hours',
    'High': '24 Hours',
    'Medium': '72 Hours',
    'Low': '7 Days'
}

def get_sla(urgency_level):
    return sla_map.get(urgency_level, 'Unknown')


urgency_score = {
    'Critical': 100,
    'High': 75,
    'Medium': 40,
    'Low': 15
}

def get_risk_score(urgency, confidence):
    base = urgency_score[urgency]
    confidence_weight = confidence * 100
    risk = (base * 0.7) + (confidence_weight * 0.3)
    return round(risk)

