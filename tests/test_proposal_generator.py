from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.proposal_generator import ProposalGenerator, ProposalNarrative


class FakeResponse:
    def __init__(self):
        self.output_parsed = ProposalNarrative(
            offer_summary="AeroShield offers a sustainment-focused repair capability aligned to the solicitation.",
            subcontracting_plan_summary="Subcontracting will be limited to specialized overflow machining and surge support.",
            corporate_experience="The contractor has relevant aircraft repair and component overhaul experience.",
            organizational_controls="Work will be managed under documented planning, quality, and review controls.",
            personnel_resources="A cross-functional maintenance, quality, and program management team will support execution.",
            marketing_strategy="The capture approach will focus on responsiveness, sustainment expertise, and compliance discipline.",
            subcontractor_strategy="Subcontractors will be used only for niche capacity or specialized support where justified.",
            past_performance_summary="Past performance themes align with sustainment, repair, and aerospace manufacturing support.",
            quality_review_procedures="Internal reviews will validate scope, compliance, and deliverable readiness before submission.",
            qc_leadership="Quality oversight will be led by trained personnel operating under aerospace quality procedures.",
            subcontractor_qc="Subcontracted work will be monitored through flow-down requirements and acceptance checkpoints.",
            issue_resolution="Issues will be triaged, root-caused, and closed with documented corrective action.",
            urgent_requirements="Urgent requirements will be handled through priority scheduling and management escalation.",
            multi_project_management="Program controls will track schedule, quality, and dependencies across concurrent work.",
            pricing_summary="Pricing will be developed from labor, material, and risk assumptions consistent with the draft scope.",
            economic_price_adjustment="Any economic adjustment would be tied to defined material or market triggers if permitted.",
            commercial_sales_practices="Commercial sales practice details will be confirmed during final pricing development.",
            capability_alignment="The contractor aligns with airframe_repair and fighter_aircraft requirements.",
            compliance_alignment="The contractor shows alignment with as9100 and small_business_plan requirements.",
            risk_analysis="The primary identified risk is schedule_risk, which appears manageable with planning discipline.",
            bid_recommendation="BID. The opportunity aligns with core repair capabilities and manageable risk.",
        )
        self.output_text = ""


class FakeResponses:
    def parse(self, **kwargs):
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_proposal_generator_renders_markdown():
    solicitation_data = {
        "title": "Repair of Aircraft Structural Components",
        "notice_id": "N0038325RT088",
        "agency": "DEPT OF DEFENSE",
        "sub_agency": "DEPT OF THE NAVY",
        "office": "NAVSUP WSS",
        "opportunity_type": "Solicitation",
        "naics_code": "336413",
        "psc_code": "1560",
        "offers_due_date": "2026-04-01",
        "compliance_requirements": ["Buy American requirements", "Small business subcontracting plan"],
        "technical_keywords": ["airframe_repair", "composite_repair"],
        "risk_keywords": ["schedule_risk"],
    }
    score_result = {
        "fit_score": 78,
        "recommendation": "BID",
        "reasoning": [
            "Technical capability aligns with airframe_repair.",
            "Moderate risks include schedule_risk.",
        ],
    }
    match_result = {
        "technical_match": {"matched_keywords": ["airframe_repair"], "missing_keywords": [], "coverage_ratio": 1.0},
        "platform_match": {
            "matched_keywords": ["fighter_aircraft"],
            "missing_keywords": [],
            "required_keywords": ["fighter_aircraft"],
        },
        "compliance_match": {
            "matched_keywords": ["small_business_plan"],
            "missing_keywords": [],
            "required_keywords": ["small_business_plan"],
        },
        "risk_assessment": {"identified_risk_keywords": ["schedule_risk"]},
    }

    generator = ProposalGenerator(client=FakeClient())
    result = generator.generate(solicitation_data, score_result, match_result)

    assert result["model"] == "gpt-5"
    assert "Repair of Aircraft Structural Components" in result["proposal_markdown"]
    assert "AeroShield Defense Systems" in result["proposal_markdown"]
    assert "**Score:** 78 / 100" in result["proposal_markdown"]
    assert "BID. The opportunity aligns with core repair capabilities and manageable risk." in result[
        "proposal_markdown"
    ]
    assert "{{" not in result["proposal_markdown"]


if __name__ == "__main__":
    test_proposal_generator_renders_markdown()
    print("test_proposal_generator_renders_markdown passed")
