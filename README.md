# AI-Defense-Proposal-Drafter

FastAPI backend scaffold for the AI defense solicitation analysis MVP.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run the API

```bash
uvicorn app.main:app --reload
```

## Run migrations

```bash
alembic upgrade head
```
