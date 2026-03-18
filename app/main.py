from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.db.database import init_db

app = FastAPI(title="Defense Solicitation Agent")
# Make sure the local tables exist as soon as the app boots.
init_db()

app.include_router(router)

app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")

templates = Jinja2Templates(directory="app/frontend/templates")
