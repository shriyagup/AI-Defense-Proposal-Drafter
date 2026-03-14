from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set


PROFILE_PATH = Path(__file__).resolve().parents[1] / "static_data" / "contractor_profile.json"


def load_contractor_profile(profile_path: Optional[str] = None) -> Dict:
    path = Path(profile_path) if profile_path else PROFILE_PATH
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def match_solicitation_to_profile(
    solicitation_data: Dict,
    contractor_profile: Optional[Dict] = None,
) -> Dict:
    profile = contractor_profile or load_contractor_profile()

    solicitation_platforms = _keyword_set(solicitation_data.get("platform_keywords", []))
    solicitation_technical = _keyword_set(solicitation_data.get("technical_keywords", []))
    solicitation_compliance = _keyword_set(solicitation_data.get("compliance_keywords", []))
    solicitation_risks = _keyword_set(solicitation_data.get("risk_keywords", []))

    profile_platforms = _keyword_set(profile.get("platform_keywords", []))
    profile_technical = _keyword_set(profile.get("technical_keywords", [])) | _keyword_set(
        profile.get("manufacturing_keywords", [])
    )
    profile_compliance = _keyword_set(profile.get("compliance_keywords", []))

    technical_match = _build_overlap_result(solicitation_technical, profile_technical)
    platform_match = _build_overlap_result(solicitation_platforms, profile_platforms)
    compliance_match = _build_overlap_result(solicitation_compliance, profile_compliance)
    risk_assessment = _build_risk_result(solicitation_risks, profile.get("risk_tolerances", {}))
    code_alignment = _build_code_alignment(solicitation_data, profile.get("match_targets", {}))

    return {
        "contractor_name": profile.get("company_name"),
        "technical_match": technical_match,
        "platform_match": platform_match,
        "compliance_match": compliance_match,
        "risk_assessment": risk_assessment,
        "code_alignment": code_alignment,
        "match_summary": _build_summary(
            technical_match=technical_match,
            platform_match=platform_match,
            compliance_match=compliance_match,
            risk_assessment=risk_assessment,
            code_alignment=code_alignment,
        ),
    }


def _keyword_set(values: List[str]) -> Set[str]:
    normalized = set()
    for value in values or []:
        if not value:
            continue
        normalized.add(str(value).strip().lower())
    return normalized


def _build_overlap_result(required: Set[str], available: Set[str]) -> Dict:
    matched = sorted(required & available)
    missing = sorted(required - available)
    available_sorted = sorted(available)
    coverage_ratio = 1.0 if not required else round(len(matched) / len(required), 4)

    return {
        "required_keywords": sorted(required),
        "matched_keywords": matched,
        "missing_keywords": missing,
        "available_keywords": available_sorted,
        "coverage_ratio": coverage_ratio,
    }


def _build_risk_result(risk_keywords: Set[str], risk_tolerances: Dict) -> Dict:
    preferred = _keyword_set(risk_tolerances.get("preferred_risk_keywords", []))
    caution = _keyword_set(risk_tolerances.get("caution_risk_keywords", []))
    high_concern = _keyword_set(risk_tolerances.get("high_concern_risk_keywords", []))

    return {
        "identified_risk_keywords": sorted(risk_keywords),
        "preferred_risks": sorted(risk_keywords & preferred),
        "caution_risks": sorted(risk_keywords & caution),
        "high_concern_risks": sorted(risk_keywords & high_concern),
        "unknown_risks": sorted(risk_keywords - preferred - caution - high_concern),
    }


def _build_code_alignment(solicitation_data: Dict, match_targets: Dict) -> Dict:
    naics_code = (solicitation_data.get("naics_code") or "").strip()
    psc_code = _normalize_psc_code(solicitation_data.get("psc_code"))
    opportunity_type = (solicitation_data.get("opportunity_type") or "").strip()
    contract_type = (solicitation_data.get("contract_type") or "").strip()

    profile_naics = {str(value).strip() for value in match_targets.get("naics_codes", [])}
    profile_psc = {_normalize_psc_code(value) for value in match_targets.get("psc_codes", [])}
    profile_opportunity_types = {str(value).strip().lower() for value in match_targets.get("opportunity_types", [])}
    profile_contract_types = {str(value).strip().lower() for value in match_targets.get("contract_types", [])}

    return {
        "naics_match": bool(naics_code and naics_code in profile_naics),
        "psc_match": bool(psc_code and psc_code in profile_psc),
        "opportunity_type_match": bool(
            opportunity_type and opportunity_type.strip().lower() in profile_opportunity_types
        ),
        "contract_type_match": bool(contract_type and contract_type.strip().lower() in profile_contract_types),
        "solicitation_codes": {
            "naics_code": naics_code or None,
            "psc_code": psc_code or None,
            "opportunity_type": opportunity_type or None,
            "contract_type": contract_type or None,
        },
    }


def _normalize_psc_code(value: Optional[str]) -> str:
    if not value:
        return ""
    cleaned = str(value).strip().upper()
    return cleaned.split(" - ", 1)[0].strip()


def _build_summary(
    technical_match: Dict,
    platform_match: Dict,
    compliance_match: Dict,
    risk_assessment: Dict,
    code_alignment: Dict,
) -> List[str]:
    summary = []

    if technical_match["matched_keywords"]:
        summary.append(
            "Technical overlap found in: " + ", ".join(technical_match["matched_keywords"][:5])
        )
    if technical_match["missing_keywords"]:
        summary.append(
            "Technical gaps detected in: " + ", ".join(technical_match["missing_keywords"][:5])
        )
    if platform_match["matched_keywords"]:
        summary.append(
            "Platform alignment found in: " + ", ".join(platform_match["matched_keywords"][:5])
        )
    if compliance_match["matched_keywords"]:
        summary.append(
            "Compliance readiness aligns with: " + ", ".join(compliance_match["matched_keywords"][:5])
        )
    if risk_assessment["high_concern_risks"]:
        summary.append(
            "High-concern risks identified: " + ", ".join(risk_assessment["high_concern_risks"][:5])
        )
    if risk_assessment["caution_risks"]:
        summary.append(
            "Caution risks identified: " + ", ".join(risk_assessment["caution_risks"][:5])
        )
    if code_alignment["naics_match"] or code_alignment["psc_match"]:
        summary.append("Core NAICS/PSC codes align with contractor targets.")

    return summary
