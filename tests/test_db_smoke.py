from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import SessionLocal, init_db
from app.db.crud import (
    create_solicitation,
    get_or_create_default_contractor_profile,
    get_solicitation_by_url,
    replace_solicitation_links,
    update_solicitation_analysis,
    update_solicitation_extraction,
)
from app.db.models import Solicitation, SolicitationLink


def test_db_smoke():
    init_db()

    db = SessionLocal()
    try:
        profile = get_or_create_default_contractor_profile(db)
        assert profile.company_name == "AeroShield Defense Systems"

        smoke_url = "https://sam.gov/workspace/contract/opp/test-smoke/view"
        existing = get_solicitation_by_url(db, smoke_url)
        if existing is not None:
            db.query(SolicitationLink).filter(SolicitationLink.solicitation_id == existing.id).delete()
            db.delete(existing)
            db.commit()

        solicitation = create_solicitation(
            db=db,
            url=smoke_url,
            raw_page_text="Smoke test solicitation body",
        )
        assert solicitation.id is not None

        solicitation = update_solicitation_extraction(
            db=db,
            solicitation=solicitation,
            raw_page_text="Updated smoke test solicitation body",
            solicitation_data={
                "notice_id": "SMOKE-001",
                "title": "Smoke Test Solicitation",
                "agency": "DEPT OF DEFENSE",
                "sub_agency": "DEPT OF THE NAVY",
                "office": "NAVSUP WSS",
                "opportunity_type": "Solicitation",
                "published_date": "2026-03-14",
                "offers_due_date": "2026-03-28",
                "naics_code": "336413",
                "psc_code": "1560",
                "contract_type": "Firm Fixed Price",
                "technical_keywords": ["airframe_repair"],
                "compliance_keywords": ["as9100"],
                "risk_keywords": ["schedule_risk"],
            },
        )
        assert solicitation.notice_id == "SMOKE-001"
        assert solicitation.title == "Smoke Test Solicitation"

        links = replace_solicitation_links(
            db=db,
            solicitation=solicitation,
            links=[
                {
                    "text": "Amendment 0001",
                    "url": "https://sam.gov/amendment-0001",
                    "link_type": "amendment",
                }
            ],
        )
        assert len(links) == 1
        assert links[0].link_type == "amendment"

        solicitation = update_solicitation_analysis(
            db=db,
            solicitation=solicitation,
            score_result={
                "fit_score": 78,
                "recommendation": "BID",
                "reasoning": ["Strong technical alignment", "Moderate schedule risk"],
            },
            proposal_result={
                "proposal_markdown": "# Smoke Test Proposal",
            },
        )
        assert solicitation.fit_score == 78
        assert solicitation.fit_recommendation == "BID"
        assert "Strong technical alignment" in solicitation.fit_reasoning

        loaded = get_solicitation_by_url(db, smoke_url)
        assert loaded is not None
        assert loaded.notice_id == "SMOKE-001"
        assert len(loaded.links) == 1
        assert loaded.links[0].url == "https://sam.gov/amendment-0001"
    finally:
        db.close()


if __name__ == "__main__":
    test_db_smoke()
    print("test_db_smoke passed")
