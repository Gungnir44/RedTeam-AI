"""Basic CVSS v3.1 score calculator."""
from __future__ import annotations
import math


# CVSS v3.1 metric weights
_AV  = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
_AC  = {"L": 0.77, "H": 0.44}
_PR  = {
    "N": {"N": 0.85, "L": 0.62, "H": 0.27},  # scope unchanged
    "C": {"N": 0.85, "L": 0.68, "H": 0.50},  # scope changed
}
_UI  = {"N": 0.85, "R": 0.62}
_CIA = {"N": 0.00, "L": 0.22, "H": 0.56}


def calculate_cvss3(
    attack_vector: str = "N",        # N/A/L/P
    attack_complexity: str = "L",    # L/H
    privileges_required: str = "N",  # N/L/H
    user_interaction: str = "N",     # N/R
    scope: str = "U",               # U/C  (Unchanged/Changed)
    confidentiality: str = "N",     # N/L/H
    integrity: str = "N",           # N/L/H
    availability: str = "N",        # N/L/H
) -> dict:
    """Calculate CVSS v3.1 base score and return result dict."""
    av = _AV.get(attack_vector, 0.85)
    ac = _AC.get(attack_complexity, 0.77)
    scope_key = "C" if scope == "C" else "N"
    pr = _PR[scope_key].get(privileges_required, 0.85)
    ui = _UI.get(user_interaction, 0.85)

    iss = 1 - (1 - _CIA.get(confidentiality, 0)) * (1 - _CIA.get(integrity, 0)) * (1 - _CIA.get(availability, 0))

    if scope == "U":
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15

    exploitability = 8.22 * av * ac * pr * ui

    if impact <= 0:
        base_score = 0.0
    else:
        if scope == "U":
            raw = min(impact + exploitability, 10)
        else:
            raw = min(1.08 * (impact + exploitability), 10)
        # Round up to 1 decimal
        base_score = math.ceil(raw * 10) / 10

    severity = score_to_severity(base_score)
    return {
        "score": round(base_score, 1),
        "severity": severity,
        "vector": f"CVSS:3.1/AV:{attack_vector}/AC:{attack_complexity}/PR:{privileges_required}/UI:{user_interaction}/S:{scope}/C:{confidentiality}/I:{integrity}/A:{availability}",
    }


def score_to_severity(score: float) -> str:
    if score == 0.0:
        return "none"
    elif score < 4.0:
        return "low"
    elif score < 7.0:
        return "medium"
    elif score < 9.0:
        return "high"
    else:
        return "critical"
