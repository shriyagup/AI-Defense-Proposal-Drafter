from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SolicitationLinkSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(default="")
    url: str = Field(default="")
    link_type: str = Field(default="unknown")
    is_processed: bool = Field(default=False)


class LinkedOpportunitySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    link_text: str = Field(default="")
    url: str = Field(default="")
    relationship_type: str = Field(default="unknown")


class SolicitationInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: Optional[str] = Field(default=None)
    solicitation_text: Optional[str] = Field(default=None)


class SolicitationExtractionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    notice_id: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    agency: Optional[str] = Field(default=None)
    sub_agency: Optional[str] = Field(default=None)
    office: Optional[str] = Field(default=None)
    opportunity_type: Optional[str] = Field(default=None)
    published_date: Optional[str] = Field(default=None)
    offers_due_date: Optional[str] = Field(default=None)
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
    linked_opportunities: List[LinkedOpportunitySchema] = Field(default_factory=list)
