from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.scorer import score_solicitation


def test_scorer_returns_bid_for_strong_fit():
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

    result = score_solicitation(solicitation_data)

    assert result["recommendation"] == "BID"
    assert result["fit_score"] >= 90
    assert result["score_breakdown"]["technical_capability_score"] == 40.0
    assert result["score_breakdown"]["platform_relevance_score"] == 25.0
    assert result["score_breakdown"]["compliance_readiness_score"] == 20.0
    assert result["score_breakdown"]["risk_score"] == 12.0
    assert result["score_breakdown"]["code_alignment_bonus"] == 5.0
    assert any("Technical capability aligns" in item for item in result["reasoning"])


def test_scorer_returns_no_bid_for_weak_fit():
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

    result = score_solicitation(solicitation_data)

    assert result["recommendation"] == "NO BID"
    assert result["fit_score"] < 50
    assert result["score_breakdown"]["technical_capability_score"] == 0.0
    assert result["score_breakdown"]["platform_relevance_score"] == 0.0
    assert result["score_breakdown"]["compliance_readiness_score"] == 0.0
    assert result["score_breakdown"]["risk_score"] == 0.0
    assert result["score_breakdown"]["code_alignment_bonus"] == 0.0
    assert any("Technical gaps remain" in item for item in result["reasoning"])
