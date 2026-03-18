# AI Defense Proposal Drafter

AI Defense Proposal Drafter is a FastAPI web application that helps a contractor review a defense solicitation, assess fit against a contractor profile, and generate a proposal draft from pasted solicitation text.

The app is designed to reduce the first-pass manual review work involved in government contracting opportunities. A user pastes solicitation text into the interface, and the application:

- extracts structured opportunity details
- compares the opportunity to a stored contractor profile
- scores the opportunity as a bid or no-bid fit
- generates a draft proposal response
- stores the analysis result in SQLite for later review

## What The App Does

At a high level, the app runs a simple analysis pipeline:

1. A user pastes solicitation text into the frontend form.
2. The backend sends that text to an OpenAI-powered extraction step.
3. Extracted fields are matched against the contractor profile in `app/static_data/contractor_profile.json`.
4. The app computes a fit score and recommendation.
5. A proposal draft is generated using the extracted data, match result, and score.
6. The solicitation record and generated outputs are stored in the local SQLite database.

## Current Scope

This version of the project is text-only.

- Supported: pasted solicitation text
- Not currently supported: live URL scraping

The scraping flow was intentionally removed to keep the app faster and simpler while the core analysis workflow is being developed.

## Tech Stack

- FastAPI
- Jinja2 templates
- SQLAlchemy
- SQLite
- Pydantic
- OpenAI API

## Project Structure

```text
app/
  api/
    routes.py                # FastAPI routes and request orchestration
  db/
    database.py              # SQLAlchemy engine/session setup
    models.py                # ORM table definitions
    crud.py                  # Database read/write helpers
  frontend/
    templates/index.html     # Main UI
    static/styles.css        # Frontend styling
  prompts/
    extraction_prompt.txt    # Prompt used for structured extraction
    proposal_prompt.txt      # Prompt used for proposal generation
  schemas/
    analysis.py              # Response and analysis schemas
    proposal.py              # Proposal output schemas
    solicitation.py          # Solicitation extraction schemas
  services/
    extractor.py             # OpenAI extraction logic
    matcher.py               # Contractor-profile matching logic
    scorer.py                # Bid/no-bid scoring logic
    proposal_generator.py    # Proposal draft generation logic
  static_data/
    contractor_profile.json  # Default contractor profile
    proposal_template.md     # Template used for proposal drafting

run.py                       # Local app entry point
requirements.txt             # Python dependencies
tests/                       # Test suite
```

## Requirements

You need:

- Python 3.9+
- an OpenAI API key

The project in this workspace has been run using the Miniconda Python at `/opt/miniconda3/bin/python`.

## Environment Variables

Create a local `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

Optional:

```env
DATABASE_URL=sqlite:////absolute/path/to/app.db
OPENAI_EXTRACTION_MODEL=gpt-5-mini
OPENAI_PROPOSAL_MODEL=gpt-5
```

If `DATABASE_URL` is not set, the app defaults to:

```text
sqlite:///app.db
```

relative to the project root, as configured in [app/config.py](/Users/shriyagupta/AIDefenseProposalDrafter/AI-Defense-Proposal-Drafter/app/config.py).

## Installation

Install dependencies:

```bash
cd /Users/shriyagupta/AIDefenseProposalDrafter/AI-Defense-Proposal-Drafter
/opt/miniconda3/bin/python -m pip install -r requirements.txt
```

If you prefer a virtual environment, create and activate one first, then install the same requirements file.

## Running The App

From the project root:

```bash
/opt/miniconda3/bin/python run.py
```

Then open:

```text
http://127.0.0.1:8000
```

You can also run it directly with Uvicorn:

```bash
/opt/miniconda3/bin/python -m uvicorn app.main:app --reload
```

## How To Use It

1. Start the app.
2. Open the local web page.
3. Paste solicitation text into the text area.
4. Click `Analyze Text`.
5. Review:
   - extracted opportunity details
   - fit score and recommendation
   - capability and compliance alignment
   - risk indicators
   - generated proposal draft

## Database

The app uses SQLite and creates the database automatically on startup through `init_db()` in [app/main.py](/Users/shriyagupta/AIDefenseProposalDrafter/AI-Defense-Proposal-Drafter/app/main.py).

To inspect the database manually:

```bash
sqlite3 app.db
```

Useful SQLite commands:

```sql
.tables
.schema solicitations
.schema solicitation_links
.schema contractor_profiles
SELECT id, title, fit_score, fit_recommendation, created_at FROM solicitations;
```

## Testing

The repository contains route, service, and database smoke tests.

Example:

```bash
/opt/miniconda3/bin/python tests/test_analyze_route.py
```

```bash
/opt/miniconda3/bin/python tests/test_db_smoke.py
```

### Coverage

In this environment, the most reliable way to run coverage has been a direct Python/coverage runner instead of a plain `pytest --cov` invocation.

```bash
PYTHONPYCACHEPREFIX=/tmp/pythoncache /opt/miniconda3/bin/python - <<'PY'
import coverage
cov = coverage.Coverage(source=['app'])
cov.start()

import unittest
from tests import test_analyze_route, test_db_smoke, test_extractor, test_matcher, test_openaiapi, test_proposal_generator, test_scorer

suite = unittest.defaultTestLoader.loadTestsFromModule(test_analyze_route)
result = unittest.TextTestRunner(verbosity=0).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)

for test in [
    test_db_smoke.test_db_smoke,
    test_extractor.test_extractor_returns_parsed_model_and_builds_input,
    test_extractor.test_extractor_rejects_empty_text,
    test_extractor.test_extractor_raises_extraction_error_with_model_output,
    test_extractor.test_extract_solicitation_data_wrapper_uses_extractor,
    test_matcher.test_matcher_detects_keyword_overlap_and_code_alignment,
    test_matcher.test_matcher_detects_missing_keywords_and_high_concern_risks,
    test_openaiapi.test_proposal_generator_builds_fallback_context_and_markdown,
    test_openaiapi.test_proposal_generator_reports_failure_with_output_text,
    test_openaiapi.test_proposal_generator_helper_methods_cover_edge_cases,
    test_openaiapi.test_generate_proposal_wrapper_uses_generator,
    test_openaiapi.test_extractor_failure_message_constant_is_not_used_live,
    test_proposal_generator.test_proposal_generator_renders_markdown,
    test_scorer.test_scorer_returns_bid_for_strong_fit,
    test_scorer.test_scorer_returns_no_bid_for_weak_fit,
]:
    test()

cov.stop()
cov.save()
cov.report(show_missing=True)
PY
```

## Notes

- The app currently uses a default contractor profile from `app/static_data/contractor_profile.json`.
- Analysis results are persisted locally.
- OpenAI-backed extraction and proposal generation require a valid API key.
- The frontend is intentionally lightweight and server-rendered with Jinja templates.

## Future Improvements

Potential next steps for the project:

- restore optional URL scraping as a separate flow
- add asynchronous/background proposal generation
- improve markdown rendering for proposal output
- add export options for proposal drafts
- support multiple contractor profiles
- add authentication and multi-user access

## License

Add the license you want to use for this repository here.
