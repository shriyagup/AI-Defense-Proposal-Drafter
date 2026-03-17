from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.proposal import ProposalResultSchema
from app.schemas.solicitation import SolicitationExtractionSchema, SolicitationLinkSchema


class KeywordMatchSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_keywords: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    available_keywords: List[str] = Field(default_factory=list)
    coverage_ratio: float = Field(default=0.0)


class RiskAssessmentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identified_risk_keywords: List[str] = Field(default_factory=list)
    preferred_risks: List[str] = Field(default_factory=list)
    caution_risks: List[str] = Field(default_factory=list)
    high_concern_risks: List[str] = Field(default_factory=list)
    unknown_risks: List[str] = Field(default_factory=list)


class CodeAlignmentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    naics_match: bool = Field(default=False)
    psc_match: bool = Field(default=False)
    opportunity_type_match: bool = Field(default=False)
    contract_type_match: bool = Field(default=False)
    solicitation_codes: Dict[str, Optional[str]] = Field(default_factory=dict)


class MatchResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contractor_name: Optional[str] = Field(default=None)
    technical_match: KeywordMatchSchema
    platform_match: KeywordMatchSchema
    compliance_match: KeywordMatchSchema
    risk_assessment: RiskAssessmentSchema
    code_alignment: CodeAlignmentSchema
    match_summary: List[str] = Field(default_factory=list)


class ScoreBreakdownSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    technical_capability_score: float = Field(default=0.0)
    platform_relevance_score: float = Field(default=0.0)
    compliance_readiness_score: float = Field(default=0.0)
    risk_score: float = Field(default=0.0)
    code_alignment_bonus: float = Field(default=0.0)


class ScoreResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fit_score: int = Field(default=0)
    recommendation: str = Field(default="NO BID")
    score_breakdown: ScoreBreakdownSchema
    reasoning: List[str] = Field(default_factory=list)
    match_result: MatchResultSchema
    contractor_name: Optional[str] = Field(default=None)


class AnalyzeResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    solicitation_id: Optional[int] = Field(default=None)
    preview_text: str = Field(default="")
    links: List[SolicitationLinkSchema] = Field(default_factory=list)
    extracted: Optional[SolicitationExtractionSchema] = Field(default=None)
    match_result: Optional[MatchResultSchema] = Field(default=None)
    score_result: Optional[ScoreResultSchema] = Field(default=None)
    proposal_result: Optional[ProposalResultSchema] = Field(default=None)
    error: Optional[str] = Field(default=None)
