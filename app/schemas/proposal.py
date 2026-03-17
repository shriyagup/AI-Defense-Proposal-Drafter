from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, ConfigDict, Field


class ProposalNarrativeSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    negative_feedback_response: str = Field(default="TBD")
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


class ProposalResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_sections: ProposalNarrativeSchema
    template_context: Dict = Field(default_factory=dict)
    proposal_markdown: str = Field(default="")
    model: str = Field(default="")
