from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.matcher import match_solicitation_to_profile


def test_matcher_detects_keyword_overlap_and_code_alignment():
    solicitation_data = {
        "naics_code": "336413",
        "psc_code": "1560 - AIRFRAME STRUCTURAL COMPONENTS",
        "opportunity_type": "Solicitation",
        "contract_type": "Firm Fixed Price",
        "platform_keywords": ["fighter_aircraft", "naval_aviation"],
        "technical_keywords": ["airframe_repair", "inspection", "composite_repair"],
        "compliance_keywords": ["as9100", "small_business_plan"],
        "risk_keywords": ["schedule_risk"],
    }

    result = match_solicitation_to_profile(solicitation_data)

    assert result["contractor_name"] == "AeroShield Defense Systems"
    assert result["technical_match"]["matched_keywords"] == [
        "airframe_repair",
        "composite_repair",
        "inspection",
    ]
    assert result["technical_match"]["missing_keywords"] == []
    assert result["platform_match"]["matched_keywords"] == [
        "fighter_aircraft",
        "naval_aviation",
    ]
    assert result["compliance_match"]["matched_keywords"] == [
        "as9100",
        "small_business_plan",
    ]
    assert result["risk_assessment"]["caution_risks"] == ["schedule_risk"]
    assert result["risk_assessment"]["high_concern_risks"] == []
    assert result["code_alignment"]["naics_match"] is True
    assert result["code_alignment"]["psc_match"] is True
    assert result["code_alignment"]["opportunity_type_match"] is True
    assert result["code_alignment"]["contract_type_match"] is True
    assert any("Technical overlap found" in item for item in result["match_summary"])


def test_matcher_detects_missing_keywords_and_high_concern_risks():
    solicitation_data = {
        "naics_code": "541330",
        "psc_code": "AC13 - R&D",
        "opportunity_type": "Presolicitation",
        "contract_type": "Cost Plus Fixed Fee",
        "platform_keywords": ["missile_systems"],
        "technical_keywords": ["systems_integration", "software_development"],
        "compliance_keywords": ["cmmc", "dod_security"],
        "risk_keywords": ["extreme_schedule_pressure", "major_compliance_burden", "unknown_custom_risk"],
    }

    result = match_solicitation_to_profile(solicitation_data)

    assert result["technical_match"]["matched_keywords"] == []
    assert result["technical_match"]["missing_keywords"] == [
        "software_development",
        "systems_integration",
    ]
    assert result["platform_match"]["missing_keywords"] == ["missile_systems"]
    assert result["compliance_match"]["missing_keywords"] == ["cmmc", "dod_security"]
    assert result["risk_assessment"]["high_concern_risks"] == [
        "extreme_schedule_pressure",
        "major_compliance_burden",
    ]
    assert result["risk_assessment"]["unknown_risks"] == ["unknown_custom_risk"]
    assert result["code_alignment"]["naics_match"] is False
    assert result["code_alignment"]["psc_match"] is False
