from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

from app.services.matcher import load_contractor_profile


if load_dotenv is not None:
    load_dotenv()


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "proposal_prompt.txt"
TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "static_data" / "proposal_template.md"
DEFAULT_PROPOSAL_MODEL = "gpt-5"


class ProposalNarrative(BaseModel):
    model_config = ConfigDict(extra="forbid")

    offer_summary: str = Field(default="TBD")
    subcontracting_plan_summary: str = Field(default="TBD")
    corporate_experience: str = Field(default="TBD")
    organizational_controls: str = Field(default="TBD")
    personnel_resources: str = Field(default="TBD")
    marketing_strategy: str = Field(default="TBD")
    subcontractor_strategy: str = Field(default="TBD")
    client_1: str = Field(default="TBD")
    project_1: str = Field(default="TBD")
    value_1: str = Field(default="TBD")
    period_1: str = Field(default="TBD")
    client_2: str = Field(default="TBD")
    project_2: str = Field(default="TBD")
    value_2: str = Field(default="TBD")
    period_2: str = Field(default="TBD")
    past_performance_summary: str = Field(default="TBD")
    negative_feedback_response: str = Field(default="No material negative feedback was provided in the source data.")
    quality_review_procedures: str = Field(default="TBD")
    qc_leadership: str = Field(default="TBD")
    subcontractor_qc: str = Field(default="TBD")
    issue_resolution: str = Field(default="TBD")
    urgent_requirements: str = Field(default="TBD")
    multi_project_management: str = Field(default="TBD")
    project1_client: str = Field(default="TBD")
    project1_contract: str = Field(default="TBD")
    project1_period: str = Field(default="TBD")
    project1_value: str = Field(default="TBD")
    project1_summary: str = Field(default="TBD")
    project1_scope: str = Field(default="TBD")
    project1_tools: str = Field(default="TBD")
    project1_compliance: str = Field(default="TBD")
    project1_results: str = Field(default="TBD")
    project2_client: str = Field(default="TBD")
    project2_contract: str = Field(default="TBD")
    project2_period: str = Field(default="TBD")
    project2_value: str = Field(default="TBD")
    project2_summary: str = Field(default="TBD")
    project2_scope: str = Field(default="TBD")
    project2_tools: str = Field(default="TBD")
    project2_compliance: str = Field(default="TBD")
    project2_results: str = Field(default="TBD")
    pricing_summary: str = Field(default="TBD")
    economic_price_adjustment: str = Field(default="TBD")
    commercial_sales_practices: str = Field(default="TBD")
    capability_alignment: str = Field(default="TBD")
    compliance_alignment: str = Field(default="TBD")
    risk_analysis: str = Field(default="TBD")
    bid_recommendation: str = Field(default="TBD")


class ProposalGenerationError(RuntimeError):
    pass


class ProposalGenerator:
    def __init__(
        self,
        client: Optional[Any] = None,
        model: Optional[str] = None,
        prompt_path: Optional[Union[str, Path]] = None,
        template_path: Optional[Union[str, Path]] = None,
    ) -> None:
        if client is not None:
            self.client = client
        else:
            if OpenAI is None:
                raise ImportError(
                    "openai is required for live proposal generation. Install the package or pass a client."
                )
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_PROPOSAL_MODEL", DEFAULT_PROPOSAL_MODEL)
        self.prompt_path = Path(prompt_path) if prompt_path else PROMPT_PATH
        self.template_path = Path(template_path) if template_path else TEMPLATE_PATH
        self.instructions = self.prompt_path.read_text(encoding="utf-8").strip()
        self.template = self.template_path.read_text(encoding="utf-8")

    def generate(
        self,
        solicitation_data: Dict,
        score_result: Dict,
        match_result: Dict,
        contractor_profile: Optional[Dict] = None,
    ) -> Dict:
        profile = contractor_profile or load_contractor_profile()
        # First get the narrative blocks from the model, then drop them into the markdown template.
        narrative = self._generate_narrative(
            solicitation_data=solicitation_data,
            score_result=score_result,
            match_result=match_result,
            contractor_profile=profile,
        )
        context = self._build_template_context(
            solicitation_data=solicitation_data,
            score_result=score_result,
            match_result=match_result,
            contractor_profile=profile,
            narrative=narrative,
        )

        return {
            "proposal_sections": narrative.model_dump(),
            "template_context": context,
            "proposal_markdown": self._render_template(context),
            "model": self.model,
        }

    def _generate_narrative(
        self,
        solicitation_data: Dict,
        score_result: Dict,
        match_result: Dict,
        contractor_profile: Dict,
    ) -> ProposalNarrative:
        response = self.client.responses.parse(
            model=self.model,
            instructions=self.instructions,
            input=self._build_input(
                solicitation_data=solicitation_data,
                score_result=score_result,
                match_result=match_result,
                contractor_profile=contractor_profile,
            ),
            text_format=ProposalNarrative,
        )

        if response.output_parsed is not None:
            return response.output_parsed

        raise ProposalGenerationError(self._build_failure_message(response))

    def _build_input(
        self,
        solicitation_data: Dict,
        score_result: Dict,
        match_result: Dict,
        contractor_profile: Dict,
    ) -> str:
        # Give the model the same structured picture the rest of the app is using.
        payload = {
            "solicitation_data": solicitation_data,
            "score_result": score_result,
            "match_result": match_result,
            "contractor_profile": contractor_profile,
            "proposal_template": self.template,
        }
        return (
            "Use the following structured inputs to draft the proposal sections.\n\n"
            + json.dumps(payload, indent=2)
        )

    def _build_template_context(
        self,
        solicitation_data: Dict,
        score_result: Dict,
        match_result: Dict,
        contractor_profile: Dict,
        narrative: ProposalNarrative,
    ) -> Dict:
        context = narrative.model_dump()
        context.update(
            {
                "title": solicitation_data.get("title") or "TBD",
                "notice_id": solicitation_data.get("notice_id") or "TBD",
                "agency": solicitation_data.get("agency") or "TBD",
                "sub_agency": solicitation_data.get("sub_agency") or "TBD",
                "office": solicitation_data.get("office") or "TBD",
                "opportunity_type": solicitation_data.get("opportunity_type") or "TBD",
                "naics_code": solicitation_data.get("naics_code") or "TBD",
                "psc_code": solicitation_data.get("psc_code") or "TBD",
                "submission_date": solicitation_data.get("offers_due_date") or str(date.today()),
                "contractor_name": contractor_profile.get("company_name") or "TBD",
                "cage_code": contractor_profile.get("cage_code") or "TBD",
                "sam_status": contractor_profile.get("sam_status") or "Active - TBD Verification",
                "years_experience": contractor_profile.get("years_experience") or "TBD",
                "negotiator_name": contractor_profile.get("negotiator_name") or "TBD",
                "negotiator_contact": contractor_profile.get("negotiator_contact") or "TBD",
                "fit_score": score_result.get("fit_score", "TBD"),
                "compliance_requirements": self._bullet_list(
                    solicitation_data.get("compliance_requirements", [])
                ),
                "technical_keywords": self._bullet_list(
                    solicitation_data.get("technical_keywords", [])
                ),
                "risk_factors": self._bullet_list(solicitation_data.get("risk_keywords", [])),
            }
        )

        # Fill in a few sections from the deterministic match data if the model leaves them vague.
        if not context["capability_alignment"] or context["capability_alignment"] == "TBD":
            context["capability_alignment"] = self._bullet_list(
                match_result.get("technical_match", {}).get("matched_keywords", [])
                + match_result.get("platform_match", {}).get("matched_keywords", [])
            )
        if not context["compliance_alignment"] or context["compliance_alignment"] == "TBD":
            context["compliance_alignment"] = self._bullet_list(
                match_result.get("compliance_match", {}).get("matched_keywords", [])
            )
        if not context["risk_analysis"] or context["risk_analysis"] == "TBD":
            context["risk_analysis"] = self._bullet_list(
                match_result.get("risk_assessment", {}).get("identified_risk_keywords", [])
            )
        if not context["bid_recommendation"] or context["bid_recommendation"] == "TBD":
            context["bid_recommendation"] = self._format_bid_recommendation(score_result)

        return context

    def _render_template(self, context: Dict) -> str:
        rendered = self.template
        for key, value in context.items():
            rendered = rendered.replace("{{" + key + "}}", str(value))

        # Anything still unresolved in the template falls back to TBD instead of leaking placeholders.
        return re.sub(r"{{[^{}]+}}", "TBD", rendered)

    def _format_bid_recommendation(self, score_result: Dict) -> str:
        recommendation = score_result.get("recommendation", "TBD")
        reasoning = score_result.get("reasoning", [])
        if reasoning:
            return recommendation + "\n\n" + self._bullet_list(reasoning)
        return recommendation

    def _bullet_list(self, values) -> str:
        cleaned_values = [str(value).strip() for value in values or [] if str(value).strip()]
        if not cleaned_values:
            return "TBD"
        return "\n".join("- " + value for value in cleaned_values)

    def _build_failure_message(self, response: object) -> str:
        output_text = getattr(response, "output_text", "") or ""
        if output_text:
            return "OpenAI proposal generation did not return parsed structured data. Model output: " + output_text
        return "OpenAI proposal generation did not return parsed structured data."


def generate_proposal(
    solicitation_data: Dict,
    score_result: Dict,
    match_result: Dict,
    contractor_profile: Optional[Dict] = None,
) -> Dict:
    # Matching the extractor wrapper keeps the route code pretty small.
    generator = ProposalGenerator()
    return generator.generate(
        solicitation_data=solicitation_data,
        score_result=score_result,
        match_result=match_result,
        contractor_profile=contractor_profile,
    )
