from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.scraper import scrape_solicitation

router = APIRouter()
templates = Jinja2Templates(directory="app/frontend/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "url": "",
            "solicitation_text": ""
        }
    )


@router.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    url: str = Form(""),
    solicitation_text: str = Form("")
):
    used_text = ""
    links = []
    error = None

    if solicitation_text.strip():
        used_text = solicitation_text.strip()
    elif url.strip():
        scrape_result = scrape_solicitation(url.strip())
        used_text = scrape_result.get("preview_text", "")
        links = scrape_result.get("links", [])
        error = scrape_result.get("error")
    else:
        error = "Please provide either a URL or pasted solicitation text."

    result = {
        "preview_text": used_text[:12000],
        "links": links,
        "error": error
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "url": url,
            "solicitation_text": solicitation_text
        }
    )