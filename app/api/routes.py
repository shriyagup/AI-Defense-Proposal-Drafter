from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.crud import (
    create_solicitation,
    get_or_create_default_contractor_profile,
    get_solicitation_by_url,
    replace_solicitation_links,
    update_solicitation_analysis,
    update_solicitation_extraction,
)
from app.db.database import db_session
from app.schemas.analysis import AnalyzeResponseSchema, MatchResultSchema, ScoreResultSchema
from app.schemas.proposal import ProposalResultSchema
from app.schemas.solicitation import SolicitationExtractionSchema
from app.services.extractor import extract_solicitation_data
from app.services.matcher import match_solicitation_to_profile
from app.services.proposal_generator import generate_proposal
from app.services.scorer import score_solicitation

router = APIRouter()
templates = Jinja2Templates(directory="app/frontend/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "solicitation_text": ""
        }
    )


@router.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    solicitation_text: str = Form("")
):
    # Keep these separate so the template can still render partial output on failures.
    used_text = ""
    links = []
    error = None
    extracted = None
    match_result = None
    score_result = None
    proposal_result = None
    solicitation_record = None
    solicitation_id = None

    if solicitation_text.strip():
        used_text = solicitation_text.strip()
    else:
        error = "Please paste solicitation text to analyze."

    if not error and used_text.strip():
        try:
            source_url = "manual://submission/" + datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            extracted = SolicitationExtractionSchema.model_validate(
                extract_solicitation_data(used_text, source_url=None)
            )

            with db_session() as db:
                contractor_profile = get_or_create_default_contractor_profile(db).capabilities_json
                solicitation_record = get_solicitation_by_url(db, source_url)
                if solicitation_record is None:
                    solicitation_record = create_solicitation(db, url=source_url, raw_page_text=used_text)

                # Save the structured extraction before scoring so the database has the raw analysis trail.
                solicitation_record = update_solicitation_extraction(
                    db=db,
                    solicitation=solicitation_record,
                    solicitation_data=extracted.model_dump(),
                    raw_page_text=used_text,
                )

                # These come from the extraction output now that scraping is gone.
                stored_links = links or [
                    {
                        "link_text": item.link_text,
                        "url": item.url,
                        "link_type": item.relationship_type or "unknown",
                    }
                    for item in extracted.linked_opportunities
                ]
                replace_solicitation_links(db, solicitation_record, stored_links)

                # The rest of the pipeline is just match -> score -> proposal in order.
                match_result = MatchResultSchema.model_validate(match_solicitation_to_profile(
                    solicitation_data=extracted.model_dump(),
                    contractor_profile=contractor_profile,
                ))
                score_result = ScoreResultSchema.model_validate(
                    score_solicitation(
                        match_result=match_result.model_dump(),
                    )
                )
                proposal_result = ProposalResultSchema.model_validate(generate_proposal(
                    solicitation_data=extracted.model_dump(),
                    score_result=score_result.model_dump(),
                    match_result=match_result.model_dump(),
                    contractor_profile=contractor_profile,
                ))
                solicitation_record = update_solicitation_analysis(
                    db=db,
                    solicitation=solicitation_record,
                    score_result=score_result.model_dump(),
                    proposal_result=proposal_result.model_dump(),
                )
                solicitation_id = solicitation_record.id
        except Exception as exc:
            # Surface the message in the UI for now instead of hiding it behind a generic 500.
            error = str(exc)

    result = AnalyzeResponseSchema(
        preview_text=used_text[:12000],
        links=links,
        error=error,
        extracted=extracted.model_dump() if extracted is not None else None,
        match_result=match_result.model_dump() if match_result is not None else None,
        score_result=score_result.model_dump() if score_result is not None else None,
        proposal_result=proposal_result.model_dump() if proposal_result is not None else None,
        solicitation_id=solicitation_id,
    ).model_dump()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "solicitation_text": solicitation_text
        }
    )
