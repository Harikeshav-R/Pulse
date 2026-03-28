"""Hardcoded MedDRA lookup table for hackathon prototype.

In production, this would query a proper MedDRA dictionary database.
"""

MEDDRA_TABLE = {
    "10019211": {"pt_term": "Headache", "soc": "Nervous system disorders"},
    "10028813": {"pt_term": "Nausea", "soc": "Gastrointestinal disorders"},
    "10047700": {"pt_term": "Vomiting", "soc": "Gastrointestinal disorders"},
    "10016256": {"pt_term": "Fatigue", "soc": "General disorders"},
    "10012735": {"pt_term": "Diarrhoea", "soc": "Gastrointestinal disorders"},
    "10003246": {"pt_term": "Arthralgia", "soc": "Musculoskeletal disorders"},
    "10037087": {"pt_term": "Pyrexia", "soc": "General disorders"},
    "10040785": {"pt_term": "Rash", "soc": "Skin disorders"},
    "10002272": {"pt_term": "Alopecia", "soc": "Skin disorders"},
    "10022437": {"pt_term": "Insomnia", "soc": "Psychiatric disorders"},
}

# Reverse lookup: term name → code
_TERM_TO_CODE = {v["pt_term"].lower(): k for k, v in MEDDRA_TABLE.items()}


def lookup_by_code(code: str) -> dict | None:
    """Look up a MedDRA entry by PT code."""
    return MEDDRA_TABLE.get(code)


def lookup_by_term(term: str) -> dict | None:
    """Look up a MedDRA entry by preferred term (case-insensitive)."""
    code = _TERM_TO_CODE.get(term.lower())
    if code:
        return {"code": code, **MEDDRA_TABLE[code]}
    return None
