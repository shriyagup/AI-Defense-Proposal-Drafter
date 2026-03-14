from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field


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

    notice_id: str | None = Field(default=None)
    title: str | None = Field(default=None)
    agency: str | None = Field(default=None)
    sub_agency: str | None = Field(default=None)
    office: str | None = Field(default=None)
    opportunity_type: str | None = Field(default=None)
    published_date: str | None = Field(default=None, description="ISO date YYYY-MM-DD when known.")
    offers_due_date: str | None = Field(default=None, description="ISO date YYYY-MM-DD when known.")
    naics_code: str | None = Field(default=None)
    psc_code: str | None = Field(default=None)
    contract_type: str | None = Field(default=None)
    platforms: list[str] = Field(default_factory=list)
    platform_keywords: list[str] = Field(default_factory=list)
    work_scope: list[str] = Field(default_factory=list)
    technical_keywords: list[str] = Field(default_factory=list)
    compliance_requirements: list[str] = Field(default_factory=list)
    compliance_keywords: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    risk_keywords: list[str] = Field(default_factory=list)
    linked_opportunities: list[LinkedOpportunity] = Field(default_factory=list)


class ExtractionError(RuntimeError):
    pass


class SolicitationExtractor:
    def __init__(
        self,
        client: OpenAI | None = None,
        model: str | None = None,
        prompt_path: str | Path | None = None,
    ) -> None:
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_EXTRACTION_MODEL", DEFAULT_EXTRACTION_MODEL)
        self.prompt_path = Path(prompt_path) if prompt_path else PROMPT_PATH
        self.instructions = self.prompt_path.read_text(encoding="utf-8").strip()

    def extract(self, solicitation_text: str, source_url: str | None = None) -> SolicitationExtraction:
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

    def extract_to_dict(self, solicitation_text: str, source_url: str | None = None) -> dict:
        return self.extract(solicitation_text=solicitation_text, source_url=source_url).model_dump()

    def _build_input(self, solicitation_text: str, source_url: str | None) -> list[dict]:
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
