import json
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import ContractorProfile, Solicitation, SolicitationLink


CONTRACTOR_PROFILE_PATH = Path(__file__).resolve().parents[1] / "static_data" / "contractor_profile.json"


def get_solicitation_by_id(db: Session, solicitation_id: int) -> Optional[Solicitation]:
    return db.query(Solicitation).filter(Solicitation.id == solicitation_id).first()


def get_solicitation_by_url(db: Session, url: str) -> Optional[Solicitation]:
    return db.query(Solicitation).filter(Solicitation.url == url).first()


def create_solicitation(db: Session, url: str, raw_page_text: str = "") -> Solicitation:
    solicitation = Solicitation(url=url, raw_page_text=raw_page_text)
    db.add(solicitation)
    db.commit()
    # Refresh so callers immediately get the generated primary key.
    db.refresh(solicitation)
    return solicitation


def update_solicitation_extraction(
    db: Session,
    solicitation: Solicitation,
    solicitation_data: Dict,
    raw_page_text: Optional[str] = None,
) -> Solicitation:
    # This stores the normalized extraction fields plus the raw JSON payload for later inspection.
    solicitation.notice_id = solicitation_data.get("notice_id")
    solicitation.title = solicitation_data.get("title")
    solicitation.agency = solicitation_data.get("agency")
    solicitation.sub_agency = solicitation_data.get("sub_agency")
    solicitation.office = solicitation_data.get("office")
    solicitation.opportunity_type = solicitation_data.get("opportunity_type")
    solicitation.published_date = _parse_iso_date(solicitation_data.get("published_date"))
    solicitation.offers_due_date = _parse_iso_date(solicitation_data.get("offers_due_date"))
    solicitation.naics_code = solicitation_data.get("naics_code")
    solicitation.psc_code = solicitation_data.get("psc_code")
    solicitation.contract_type = solicitation_data.get("contract_type")
    solicitation.extracted_json = solicitation_data
    if raw_page_text is not None:
        solicitation.raw_page_text = raw_page_text

    db.add(solicitation)
    db.commit()
    db.refresh(solicitation)
    return solicitation


def update_solicitation_analysis(
    db: Session,
    solicitation: Solicitation,
    score_result: Dict,
    proposal_result: Optional[Dict] = None,
) -> Solicitation:
    solicitation.fit_score = score_result.get("fit_score")
    solicitation.fit_recommendation = score_result.get("recommendation")
    solicitation.fit_reasoning = "\n".join(score_result.get("reasoning", []))
    if proposal_result is not None:
        solicitation.proposal_draft = proposal_result

    db.add(solicitation)
    db.commit()
    db.refresh(solicitation)
    return solicitation


def replace_solicitation_links(db: Session, solicitation: Solicitation, links: List[Dict]) -> List[SolicitationLink]:
    # Replace all links in one shot so reruns do not keep appending duplicates.
    db.query(SolicitationLink).filter(SolicitationLink.solicitation_id == solicitation.id).delete()

    link_rows = []
    for link in links or []:
        row = SolicitationLink(
            solicitation_id=solicitation.id,
            link_text=link.get("text") or link.get("link_text"),
            url=link.get("url", ""),
            link_type=link.get("link_type") or "unknown",
            is_processed=bool(link.get("is_processed", False)),
        )
        db.add(row)
        link_rows.append(row)

    db.commit()
    for row in link_rows:
        db.refresh(row)
    return link_rows


def get_contractor_profile(db: Session, company_name: str) -> Optional[ContractorProfile]:
    return db.query(ContractorProfile).filter(ContractorProfile.company_name == company_name).first()


def create_contractor_profile(db: Session, profile_data: Dict) -> ContractorProfile:
    profile = ContractorProfile(
        company_name=profile_data["company_name"],
        capabilities_json=profile_data,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_or_create_default_contractor_profile(db: Session) -> ContractorProfile:
    with CONTRACTOR_PROFILE_PATH.open("r", encoding="utf-8") as file_obj:
        profile_data = json.load(file_obj)

    # The app currently assumes one default profile, so seed it lazily on first use.
    existing = get_contractor_profile(db, profile_data["company_name"])
    if existing:
        return existing
    return create_contractor_profile(db, profile_data)


def _parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
