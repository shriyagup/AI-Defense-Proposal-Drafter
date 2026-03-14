from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "extraction_prompt.txt"
DEFAULT_EXTRACTION_MODEL = "gpt-5-mini"


class LinkedOpportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    link_text: str = Field(
        default="",
        description="Visible text for the referenced solicitation link, if present.",
    )
    url: str = Field(
        default="",
        description="Referenced URL when the solicitation text includes one.",
    )
    relationship_type: str = Field(
        default="unknown",
        description="Short label such as amendment, attachment, solicitation_version, or unknown.",
    )


class SolicitationExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    notice_id: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    agency: Optional[str] = Field(default=None)
    sub_agency: Optional[str] = Field(default=None)
    office: Optional[str] = Field(default=None)
    opportunity_type: Optional[str] = Field(default=None)
    published_date: Optional[str] = Field(default=None, description="ISO date YYYY-MM-DD when known.")
    offers_due_date: Optional[str] = Field(default=None, description="ISO date YYYY-MM-DD when known.")
    naics_code: Optional[str] = Field(default=None)
    psc_code: Optional[str] = Field(default=None)
    contract_type: Optional[str] = Field(default=None)
    platforms: List[str] = Field(default_factory=list)
    platform_keywords: List[str] = Field(default_factory=list)
    work_scope: List[str] = Field(default_factory=list)
    technical_keywords: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    compliance_keywords: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    risk_keywords: List[str] = Field(default_factory=list)
    linked_opportunities: List[LinkedOpportunity] = Field(default_factory=list)


class ExtractionError(RuntimeError):
    pass


class SolicitationExtractor:
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
        prompt_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_EXTRACTION_MODEL", DEFAULT_EXTRACTION_MODEL)
        self.prompt_path = Path(prompt_path) if prompt_path else PROMPT_PATH
        self.instructions = self.prompt_path.read_text(encoding="utf-8").strip()

    def extract(self, solicitation_text: str, source_url: Optional[str] = None) -> SolicitationExtraction:
        cleaned_text = solicitation_text.strip()
        if not cleaned_text:
            raise ValueError("solicitation_text must not be empty")

        response = self.client.responses.parse(
            model=self.model,
            instructions=self.instructions,
            input=self._build_input(cleaned_text, source_url),
            text_format=SolicitationExtraction,
        )

        if response.output_parsed is not None:
            return response.output_parsed

        raise ExtractionError(self._build_failure_message(response))

    def extract_to_dict(self, solicitation_text: str, source_url: Optional[str] = None) -> Dict:
        return self.extract(solicitation_text=solicitation_text, source_url=source_url).model_dump()

    def _build_input(self, solicitation_text: str, source_url: Optional[str]) -> List[Dict[str, str]]:
        user_message = ["Extract structured solicitation data from the text below."]
        if source_url:
            user_message.append(f"Source URL: {source_url}")
        user_message.append("Messy solicitation text:")
        user_message.append(solicitation_text)
        return [{"role": "user", "content": "\n\n".join(user_message)}]

    def _build_failure_message(self, response: object) -> str:
        output_text = getattr(response, "output_text", "") or ""
        if output_text:
            return f"OpenAI extraction did not return parsed structured data. Model output: {output_text}"
        return "OpenAI extraction did not return parsed structured data."


def extract_solicitation_data(solicitation_text: str, source_url: Optional[str] = None) -> Dict:
    extractor = SolicitationExtractor()
    return extractor.extract_to_dict(solicitation_text=solicitation_text, source_url=source_url)
