from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from app.main import app


class _FakeSolicitationRecord:
    def __init__(self, record_id=101):
        self.id = record_id


class _FakeContractorProfileRecord:
    def __init__(self):
        self.capabilities_json = {
            "company_name": "AeroShield Defense Systems",
            "technical_keywords": ["airframe_repair", "inspection"],
            "platform_keywords": ["fighter_aircraft", "naval_aviation"],
            "manufacturing_keywords": ["composite_repair"],
            "compliance_keywords": ["as9100", "small_business_plan"],
        }


class _FakeDbSession:
    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc, tb):
        return False


class AnalyzeRouteTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.routes.update_solicitation_analysis")
    @patch("app.api.routes.generate_proposal")
    @patch("app.api.routes.score_solicitation")
    @patch("app.api.routes.match_solicitation_to_profile")
    @patch("app.api.routes.replace_solicitation_links")
    @patch("app.api.routes.update_solicitation_extraction")
    @patch("app.api.routes.create_solicitation")
    @patch("app.api.routes.get_solicitation_by_url")
    @patch("app.api.routes.get_or_create_default_contractor_profile")
    @patch("app.api.routes.db_session")
    @patch("app.api.routes.extract_solicitation_data")
    def test_analyze_route_renders_pipeline_output(
        self,
        mock_extract,
        mock_db_session,
        mock_get_profile,
        mock_get_solicitation,
        mock_create_solicitation,
        mock_update_extraction,
        mock_replace_links,
        mock_match,
        mock_score,
        mock_generate_proposal,
        mock_update_analysis,
    ):
        mock_extract.return_value = {
            "notice_id": "N0038325RT088",
            "title": "Repair of Aircraft Structural Components",
            "agency": "DEPT OF DEFENSE",
            "sub_agency": "DEPT OF THE NAVY",
            "office": "NAVSUP WSS",
            "opportunity_type": "Solicitation",
            "published_date": "2026-03-14",
            "offers_due_date": "2026-04-01",
            "naics_code": "336413",
            "psc_code": "1560",
            "contract_type": "Firm Fixed Price",
            "platforms": ["F/A-18E/F"],
            "platform_keywords": ["fighter_aircraft", "naval_aviation"],
            "work_scope": ["repair aircraft structural components"],
            "technical_keywords": ["airframe_repair", "inspection"],
            "compliance_requirements": ["AS9100 quality compliance"],
            "compliance_keywords": ["as9100"],
            "key_risks": ["schedule pressure"],
            "risk_keywords": ["schedule_risk"],
            "linked_opportunities": [],
        }
        mock_db_session.return_value = _FakeDbSession()
        mock_get_profile.return_value = _FakeContractorProfileRecord()
        mock_get_solicitation.return_value = None
        mock_create_solicitation.return_value = _FakeSolicitationRecord(101)
        mock_update_extraction.return_value = _FakeSolicitationRecord(101)
        mock_match.return_value = {
            "contractor_name": "AeroShield Defense Systems",
            "technical_match": {
                "required_keywords": ["airframe_repair", "inspection"],
                "matched_keywords": ["airframe_repair", "inspection"],
                "missing_keywords": [],
                "available_keywords": ["airframe_repair", "inspection"],
                "coverage_ratio": 1.0,
            },
            "platform_match": {
                "required_keywords": ["fighter_aircraft", "naval_aviation"],
                "matched_keywords": ["fighter_aircraft", "naval_aviation"],
                "missing_keywords": [],
                "available_keywords": ["fighter_aircraft", "naval_aviation"],
                "coverage_ratio": 1.0,
            },
            "compliance_match": {
                "required_keywords": ["as9100"],
                "matched_keywords": ["as9100"],
                "missing_keywords": [],
                "available_keywords": ["as9100"],
                "coverage_ratio": 1.0,
            },
            "risk_assessment": {
                "identified_risk_keywords": ["schedule_risk"],
                "preferred_risks": [],
                "caution_risks": ["schedule_risk"],
                "high_concern_risks": [],
                "unknown_risks": [],
            },
            "code_alignment": {
                "naics_match": True,
                "psc_match": True,
                "opportunity_type_match": True,
                "contract_type_match": True,
                "solicitation_codes": {
                    "naics_code": "336413",
                    "psc_code": "1560",
                    "opportunity_type": "Solicitation",
                    "contract_type": "Firm Fixed Price",
                },
            },
            "match_summary": ["Technical overlap found in: airframe_repair, inspection"],
        }
        mock_score.return_value = {
            "fit_score": 92,
            "recommendation": "BID",
            "score_breakdown": {
                "technical_capability_score": 40.0,
                "platform_relevance_score": 25.0,
                "compliance_readiness_score": 20.0,
                "risk_score": 12.0,
                "code_alignment_bonus": 5.0,
            },
            "reasoning": ["Technical capability aligns with airframe_repair, inspection."],
            "match_result": mock_match.return_value,
            "contractor_name": "AeroShield Defense Systems",
        }
        mock_generate_proposal.return_value = {
            "proposal_sections": {},
            "template_context": {},
            "proposal_markdown": "# Draft Proposal\n\nBID",
            "model": "gpt-5",
        }
        mock_update_analysis.return_value = _FakeSolicitationRecord(101)

        response = self.client.post(
            "/analyze",
            data={"solicitation_text": "Repair of F/A-18 airframe components with AS9100 compliance requirements."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Repair of Aircraft Structural Components", response.text)
        self.assertIn("AeroShield Defense Systems", response.text)
        self.assertIn("BID", response.text)
        self.assertIn("Draft Proposal", response.text)
        mock_extract.assert_called_once()
        mock_match.assert_called_once()
        mock_score.assert_called_once()
        mock_generate_proposal.assert_called_once()


if __name__ == "__main__":
    unittest.main()
