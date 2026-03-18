from __future__ import annotations

from typing import Dict, List


TECHNICAL_WEIGHT = 40
PLATFORM_WEIGHT = 25
COMPLIANCE_WEIGHT = 20
RISK_WEIGHT = 15
DEFAULT_BID_THRESHOLD = 50


def score_solicitation(
    match_result: Dict,
    bid_threshold: int = DEFAULT_BID_THRESHOLD,
) -> Dict:
    # Each bucket stays separate so the UI can show where the score came from.
    technical_score = _weighted_score(match_result["technical_match"]["coverage_ratio"], TECHNICAL_WEIGHT)
    platform_score = _weighted_score(match_result["platform_match"]["coverage_ratio"], PLATFORM_WEIGHT)
    compliance_score = _weighted_score(match_result["compliance_match"]["coverage_ratio"], COMPLIANCE_WEIGHT)
    risk_score = _risk_score(match_result["risk_assessment"])
    bonus_score = _code_alignment_bonus(match_result["code_alignment"])

    raw_score = technical_score + platform_score + compliance_score + risk_score + bonus_score
    fit_score = max(0, min(100, round(raw_score)))
    recommendation = "BID" if fit_score >= bid_threshold else "NO BID"

    return {
        "fit_score": fit_score,
        "recommendation": recommendation,
        "score_breakdown": {
            "technical_capability_score": round(technical_score, 2),
            "platform_relevance_score": round(platform_score, 2),
            "compliance_readiness_score": round(compliance_score, 2),
            "risk_score": round(risk_score, 2),
            "code_alignment_bonus": round(bonus_score, 2),
        },
        "reasoning": _build_reasoning(match_result, recommendation),
        "match_result": match_result,
        "contractor_name": match_result.get("contractor_name"),
    }


def _weighted_score(coverage_ratio: float, weight: int) -> float:
    bounded_ratio = max(0.0, min(1.0, coverage_ratio))
    return bounded_ratio * weight


def _risk_score(risk_assessment: Dict) -> float:
    base = float(RISK_WEIGHT)
    caution_penalty = 3.0 * len(risk_assessment.get("caution_risks", []))
    high_concern_penalty = 7.0 * len(risk_assessment.get("high_concern_risks", []))
    unknown_penalty = 2.0 * len(risk_assessment.get("unknown_risks", []))
    preferred_bonus = 1.5 * len(risk_assessment.get("preferred_risks", []))

    # Keep the risk bucket between 0 and the max weight even if the penalties stack up.
    return max(0.0, min(float(RISK_WEIGHT), base - caution_penalty - high_concern_penalty - unknown_penalty + preferred_bonus))


def _code_alignment_bonus(code_alignment: Dict) -> float:
    bonus = 0.0
    if code_alignment.get("naics_match"):
        bonus += 3.0
    if code_alignment.get("psc_match"):
        bonus += 2.0
    if code_alignment.get("opportunity_type_match"):
        bonus += 1.0
    if code_alignment.get("contract_type_match"):
        bonus += 1.0
    return min(5.0, bonus)


def _build_reasoning(match_result: Dict, recommendation: str) -> List[str]:
    reasoning = []

    technical = match_result["technical_match"]
    platform = match_result["platform_match"]
    compliance = match_result["compliance_match"]
    risk = match_result["risk_assessment"]
    code_alignment = match_result["code_alignment"]

    if technical["matched_keywords"]:
        reasoning.append(
            "Technical capability aligns with " + ", ".join(technical["matched_keywords"][:5]) + "."
        )
    if technical["missing_keywords"]:
        reasoning.append(
            "Technical gaps remain in " + ", ".join(technical["missing_keywords"][:5]) + "."
        )

    if platform["matched_keywords"]:
        reasoning.append(
            "Platform relevance is supported by " + ", ".join(platform["matched_keywords"][:5]) + "."
        )
    elif platform["required_keywords"]:
        reasoning.append("Platform alignment is limited for this solicitation.")

    if compliance["matched_keywords"]:
        reasoning.append(
            "Compliance readiness covers " + ", ".join(compliance["matched_keywords"][:5]) + "."
        )
    elif compliance["required_keywords"]:
        reasoning.append("Compliance requirements exceed currently matched profile evidence.")

    if risk["high_concern_risks"]:
        reasoning.append(
            "High-concern risks include " + ", ".join(risk["high_concern_risks"][:5]) + "."
        )
    elif risk["caution_risks"]:
        reasoning.append(
            "Moderate risks include " + ", ".join(risk["caution_risks"][:5]) + "."
        )

    if code_alignment["naics_match"] or code_alignment["psc_match"]:
        reasoning.append("Solicitation codes align with targeted contractor market segments.")

    if recommendation == "NO BID" and not reasoning:
        reasoning.append("Overall alignment is too weak to support a bid recommendation.")
    if recommendation == "BID" and not reasoning:
        reasoning.append("Overall capability and risk profile support bidding this opportunity.")

    return reasoning
