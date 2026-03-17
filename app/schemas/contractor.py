from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ContractorRiskToleranceSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferred_risk_keywords: List[str] = Field(default_factory=list)
    caution_risk_keywords: List[str] = Field(default_factory=list)
    high_concern_risk_keywords: List[str] = Field(default_factory=list)


class ContractorMatchTargetsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    naics_codes: List[str] = Field(default_factory=list)
    psc_codes: List[str] = Field(default_factory=list)
    opportunity_types: List[str] = Field(default_factory=list)
    contract_types: List[str] = Field(default_factory=list)


class ContractorProfileSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    company_name: str
    company_summary: str = Field(default="")
    domains: List[str] = Field(default_factory=list)
    domain_keywords: List[str] = Field(default_factory=list)
    core_capabilities: List[str] = Field(default_factory=list)
    technical_keywords: List[str] = Field(default_factory=list)
    platform_experience: List[str] = Field(default_factory=list)
    platform_keywords: List[str] = Field(default_factory=list)
    manufacturing_capabilities: List[str] = Field(default_factory=list)
    manufacturing_keywords: List[str] = Field(default_factory=list)
    compliance_capabilities: List[str] = Field(default_factory=list)
    compliance_keywords: List[str] = Field(default_factory=list)
    risk_tolerances: ContractorRiskToleranceSchema = Field(default_factory=ContractorRiskToleranceSchema)
    past_performance: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    match_targets: ContractorMatchTargetsSchema = Field(default_factory=ContractorMatchTargetsSchema)
