"""Alert rules per TECHNICAL_DOC §9.1."""

ALERT_RULES = [
    {
        "id": "severe_symptom",
        "condition": "severity_grade >= 3",
        "alert_type": "symptom_severe",
        "severity_map": {3: "high", 4: "critical", 5: "critical"},
        "title_template": "Grade {grade} {symptom} reported",
        "description_template": (
            "Patient reported {symptom} (Grade {grade}) during check-in. "
            "AI confidence: {confidence:.0%}."
        ),
    },
    {
        "id": "sae_keywords",
        "condition": "is_sae == True",
        "alert_type": "sae_reported",
        "severity": "critical",
        "title_template": "Possible SAE: {symptom}",
        "description_template": (
            "Patient reported a symptom flagged as a potential Serious Adverse Event: {symptom}."
        ),
    },
    {
        "id": "wearable_anomaly",
        "condition": "anomaly.detected",
        "alert_type": "wearable_anomaly",
        "severity_map": {"medium": "medium", "high": "high"},
        "title_template": "{metric} {anomaly_type} detected",
        "description_template": (
            "{metric} {anomaly_type}: current value {value}, "
            "baseline {baseline_mean}. Z-score: {z_score}."
        ),
    },
    {
        "id": "missed_checkin",
        "condition": "consecutive_missed >= 2",
        "alert_type": "missed_checkin",
        "severity": "medium",
        "title_template": "Missed check-in ({count} consecutive)",
        "description_template": (
            "Patient did not complete their scheduled check-in. "
            "Last completed check-in: {last_checkin}."
        ),
    },
    {
        "id": "risk_score_elevated",
        "condition": "tier changed to HIGH",
        "alert_type": "risk_score_elevated",
        "severity": "high",
        "title_template": "Patient risk score elevated to {tier}",
        "description_template": (
            "Risk score increased from {old_score} to {new_score}. "
            "Contributing factors: {factors}."
        ),
    },
]
