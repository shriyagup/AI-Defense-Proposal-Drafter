from pathlib import Path
import sys
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.extractor import (
    ExtractionError,
    LinkedOpportunity,
    SolicitationExtraction,
    SolicitationExtractor,
    extract_solicitation_data,
)


class FakeParseResponse:
    def __init__(self, output_parsed=None, output_text=""):
        self.output_parsed = output_parsed
        self.output_text = output_text


class FakeResponses:
    def __init__(self, response):
        self.response = response
        self.last_kwargs = None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return self.response


class FakeClient:
    def __init__(self, response):
        self.responses = FakeResponses(response)


def test_extractor_returns_parsed_model_and_builds_input():
    parsed = SolicitationExtraction(
        title="Valve Repair",
        linked_opportunities=[
            LinkedOpportunity(
                link_text="Amendment 1",
                url="https://example.com/amendment1",
                relationship_type="amendment",
            )
        ],
    )
    client = FakeClient(FakeParseResponse(output_parsed=parsed))
    extractor = SolicitationExtractor(client=client, prompt_path="app/prompts/extraction_prompt.txt")

    result = extractor.extract("  Solicitation body  ", source_url="https://sam.gov/opp/123")

    assert result.title == "Valve Repair"
    assert client.responses.last_kwargs["model"] == "gpt-5-mini"
    assert "Source URL: https://sam.gov/opp/123" in client.responses.last_kwargs["input"][0]["content"]
    assert "Solicitation body" in client.responses.last_kwargs["input"][0]["content"]


def test_extractor_rejects_empty_text():
    extractor = SolicitationExtractor(
        client=FakeClient(FakeParseResponse()),
        prompt_path="app/prompts/extraction_prompt.txt",
    )

    with pytest.raises(ValueError, match="solicitation_text must not be empty"):
        extractor.extract("   ")


def test_extractor_raises_extraction_error_with_model_output():
    client = FakeClient(FakeParseResponse(output_parsed=None, output_text="not-structured"))
    extractor = SolicitationExtractor(client=client, prompt_path="app/prompts/extraction_prompt.txt")

    with pytest.raises(ExtractionError, match="not-structured"):
        extractor.extract("Solicitation body")


def test_extract_solicitation_data_wrapper_uses_extractor():
    with patch("app.services.extractor.SolicitationExtractor") as mock_extractor_cls:
        mock_extractor = mock_extractor_cls.return_value
        mock_extractor.extract_to_dict.return_value = {"title": "Wrapped"}

        result = extract_solicitation_data("body", source_url="https://example.com")

    assert result == {"title": "Wrapped"}
    mock_extractor.extract_to_dict.assert_called_once_with(
        solicitation_text="body",
        source_url="https://example.com",
    )
