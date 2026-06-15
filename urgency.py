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
            if keyword in text:
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


