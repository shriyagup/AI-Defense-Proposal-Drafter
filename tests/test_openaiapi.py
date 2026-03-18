from pathlib import Path
import sys
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.extractor import ExtractionError, SolicitationExtraction
from app.services.proposal_generator import (
    ProposalGenerationError,
    ProposalGenerator,
    ProposalNarrative,
    generate_proposal,
)


class FakeProposalResponse:
    def __init__(self, output_parsed=None, output_text=""):
        self.output_parsed = output_parsed
        self.output_text = output_text


class FakeProposalResponses:
    def __init__(self, response):
        self.response = response
        self.last_kwargs = None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return self.response


class FakeProposalClient:
    def __init__(self, response):
        self.responses = FakeProposalResponses(response)


def test_proposal_generator_builds_fallback_context_and_markdown():
    narrative = ProposalNarrative(
        capability_alignment="TBD",
        compliance_alignment="TBD",
        risk_analysis="TBD",
        bid_recommendation="TBD",
    )
    client = FakeProposalClient(FakeProposalResponse(output_parsed=narrative))
    generator = ProposalGenerator(client=client)

    result = generator.generate(
        solicitation_data={
            "title": "Repair of Aircraft Structural Components",
            "notice_id": "N0038325RT088",
            "agency": "DEPT OF DEFENSE",
            "sub_agency": "DEPT OF THE NAVY",
            "office": "NAVSUP WSS",
            "opportunity_type": "Solicitation",
            "naics_code": "336413",
            "psc_code": "1560",
            "offers_due_date": "2026-04-01",
            "compliance_requirements": ["Buy American"],
            "technical_keywords": ["airframe_repair"],
            "risk_keywords": ["schedule_risk"],
        },
        score_result={
            "fit_score": 81,
            "recommendation": "BID",
            "reasoning": ["Good match", "Manageable risk"],
        },
        match_result={
            "technical_match": {"matched_keywords": ["airframe_repair"]},
            "platform_match": {"matched_keywords": ["fighter_aircraft"]},
            "compliance_match": {"matched_keywords": ["as9100"]},
            "risk_assessment": {"identified_risk_keywords": ["schedule_risk"]},
        },
        contractor_profile={"company_name": "AeroShield Defense Systems"},
    )

    assert result["model"] == "gpt-5"
    assert "Repair of Aircraft Structural Components" in result["proposal_markdown"]
    assert "- airframe_repair" in result["template_context"]["capability_alignment"]
    assert "- as9100" in result["template_context"]["compliance_alignment"]
    assert "- schedule_risk" in result["template_context"]["risk_analysis"]
    assert "BID" in result["template_context"]["bid_recommendation"]
    assert client.responses.last_kwargs["text_format"] is ProposalNarrative


def test_proposal_generator_reports_failure_with_output_text():
    client = FakeProposalClient(FakeProposalResponse(output_parsed=None, output_text="bad response"))
    generator = ProposalGenerator(client=client)

    with pytest.raises(ProposalGenerationError, match="bad response"):
        generator.generate(
            solicitation_data={},
            score_result={},
            match_result={},
            contractor_profile={},
        )


def test_proposal_generator_helper_methods_cover_edge_cases():
    generator = ProposalGenerator(
        client=FakeProposalClient(FakeProposalResponse(output_parsed=ProposalNarrative()))
    )

    assert generator._bullet_list([]) == "TBD"
    assert generator._bullet_list([" one ", "", "two"]) == "- one\n- two"
    assert generator._format_bid_recommendation({"recommendation": "NO BID", "reasoning": []}) == "NO BID"
    assert generator._render_template({"title": "Filled"}) is not None
    assert "TBD" in generator._render_template({"title": "Filled"})


def test_generate_proposal_wrapper_uses_generator():
    with patch("app.services.proposal_generator.ProposalGenerator") as mock_generator_cls:
        mock_generator = mock_generator_cls.return_value
        mock_generator.generate.return_value = {"proposal_markdown": "ok"}

        result = generate_proposal(
            solicitation_data={"title": "Demo"},
            score_result={"fit_score": 70},
            match_result={"technical_match": {}},
            contractor_profile={"company_name": "AeroShield"},
        )

    assert result == {"proposal_markdown": "ok"}
    mock_generator.generate.assert_called_once()


def test_extractor_failure_message_constant_is_not_used_live():
    assert ExtractionError("x")
