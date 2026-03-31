NEC_KEYWORDS = [
    "nec",
    "electrical",
    "grounding",
    "conductor",
    "code",
    "safety",
    "breaker",
    "circuit",
    "compliance",
    "wiring",
    "panel",
    "overcurrent"
]

WATTMONK_KEYWORDS = [
    "wattmonk",
    "company",
    "services",
    "solar",
    "team",
    "internship",
    "role",
    "policy",
    "organization",
    "company info",
    "your company",
    "business"
]

FOLLOWUP_PHRASES = [
    "explain more",
    "tell me more",
    "elaborate",
    "simplify",
    "more detail",
    "what about that",
    "and that",
    "continue",
    "expand",
    "aur",
    "uska",
    "usme",
    "iske",
    "detail me",
    "batao aur"
]


def normalize_query(query: str) -> str:
    return query.lower().strip()


def calculate_score(query: str, keywords: list) -> int:
    score = 0
    for keyword in keywords:
        if keyword in query:
            score += 1
    return score


def is_followup_query(query: str) -> bool:
    for phrase in FOLLOWUP_PHRASES:
        if phrase in query:
            return True
    return False


def detect_intent(query: str, last_context: str = None) -> dict:
    query = normalize_query(query)

    nec_score = calculate_score(query, NEC_KEYWORDS)
    wattmonk_score = calculate_score(query, WATTMONK_KEYWORDS)
    followup = is_followup_query(query)

    if followup and last_context in ["nec", "wattmonk"]:
        return {
            "intent": last_context,
            "reason": f"Follow-up detected, continuing previous context: {last_context}",
            "is_followup": True
        }

    if nec_score > wattmonk_score and nec_score > 0:
        return {
            "intent": "nec",
            "reason": f"Matched NEC keywords, score={nec_score}",
            "is_followup": False
        }

    if wattmonk_score > nec_score and wattmonk_score > 0:
        return {
            "intent": "wattmonk",
            "reason": f"Matched Wattmonk keywords, score={wattmonk_score}",
            "is_followup": False
        }

    return {
        "intent": "general",
        "reason": "No strong domain match found, defaulting to general",
        "is_followup": False
    }
