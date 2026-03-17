from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Solicitation(Base):
    __tablename__ = "solicitations"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, unique=True, index=True)
    notice_id = Column(String(100), nullable=True)
    title = Column(String(500), nullable=True)
    agency = Column(String(255), nullable=True)
    sub_agency = Column(String(255), nullable=True)
    office = Column(String(255), nullable=True)
    opportunity_type = Column(String(100), nullable=True)
    published_date = Column(Date, nullable=True)
    offers_due_date = Column(Date, nullable=True)
    naics_code = Column(String(20), nullable=True)
    psc_code = Column(String(50), nullable=True)
    contract_type = Column(String(100), nullable=True)
    raw_page_text = Column(Text, nullable=True)
    extracted_json = Column(JSON, nullable=True)
    fit_score = Column(Float, nullable=True)
    fit_recommendation = Column(String(20), nullable=True)
    fit_reasoning = Column(Text, nullable=True)
    proposal_draft = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    links = relationship("SolicitationLink", back_populates="solicitation", cascade="all, delete-orphan")


class SolicitationLink(Base):
    __tablename__ = "solicitation_links"

    id = Column(Integer, primary_key=True, index=True)
    solicitation_id = Column(Integer, ForeignKey("solicitations.id"), nullable=False, index=True)
    link_text = Column(String(500), nullable=True)
    url = Column(String(2048), nullable=False)
    link_type = Column(String(50), nullable=True, default="unknown")
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    solicitation = relationship("Solicitation", back_populates="links")


class ContractorProfile(Base):
    __tablename__ = "contractor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, unique=True, index=True)
    capabilities_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
