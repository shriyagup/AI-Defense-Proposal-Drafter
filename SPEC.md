# AI Defense Solicitation Analysis & Proposal Drafting Agent

### MVP Technical Specification

---

# 1. Project Overview

This project implements an **AI-powered procurement analysis agent** that evaluates U.S. government contract solicitations and generates a **draft proposal package and bid recommendation** for a defense aerospace contractor.

The system ingests a **SAM.gov contract opportunity URL**, extracts solicitation data using an LLM, compares the opportunity against a **predefined contractor capability profile**, computes a **fit score**, and generates a **proposal draft aligned with the solicitation**.

The goal of the MVP is to demonstrate an **end-to-end AI agent workflow** that performs:

* data ingestion
* structured information extraction
* reasoning and capability comparison
* scoring and decision recommendation
* document generation

The MVP intentionally **limits scope to the main solicitation page** for speed and reliability. However, the system stores references to linked solicitations and attachments in the database for future expansion.

---

# 2. System Objectives

The system must:

1. Accept a **SAM.gov solicitation URL**
2. Scrape the visible page content
3. Use an LLM to extract **structured procurement fields**
4. Persist raw and structured data in a SQL database
5. Compare solicitation requirements with a **contractor capability profile**
6. Generate a **fit score and reasoning**
7. Produce a **draft proposal package**
8. Recommend **Bid / No-Bid**
9. Return results through a simple interface

---

# 3. High-Level Workflow

```
User Input (SAM.gov URL)
        ↓
Web Scraper retrieves page HTML
        ↓
Extract page text + hyperlinks
        ↓
Store raw page text in database
        ↓
LLM parses text into structured procurement data
        ↓
Structured fields stored in database
        ↓
Capability comparison against contractor profile
        ↓
Fit score generated
        ↓
LLM generates proposal draft package
        ↓
Bid / No-Bid recommendation generated
        ↓
Results returned to user
```

---

# 4. Functional Requirements

## 4.1 Input

The system must accept:

* A **single solicitation URL**
* Example format:

```
https://sam.gov/workspace/contract/opp/<ID>/view
```

The system will not follow external links during MVP execution.

---

## 4.2 Web Scraping

The scraper must:

* Fetch HTML content of the page
* Extract:

  * visible page text
  * hyperlink text
  * hyperlink URLs

The scraper will output:

```
raw_page_text
list_of_links[]
```

---

## 4.3 LLM Extraction

The system sends the scraped page text to the LLM to extract structured fields.

### Required extracted fields

```
notice_id
title
agency
sub_agency
office
opportunity_type
published_date
offers_due_date
naics_code
psc_code
contract_type
platforms
work_scope
compliance_requirements
key_risks
linked_opportunities
```

### Expected LLM Output Format

JSON object.

Example:

```
{
  "notice_id": "N0038325RT088",
  "agency": "DEPT OF DEFENSE",
  "office": "NAVSUP WSS",
  "naics_code": "336413",
  "psc_code": "1560",
  "platforms": ["F/A-18E/F", "EA-18G"],
  "work_scope": [
    "repair aircraft structural components",
    "inspect leading edge flaps"
  ],
  "compliance_requirements": [
    "Buy American requirements",
    "Small business subcontracting plan"
  ]
}
```

---

# 5. Database Schema

The MVP uses a SQL database with three primary tables.

---

# 5.1 Table: solicitations

Stores all opportunity information and analysis results.

Fields:

```
id (PK)

url
notice_id
title
agency
sub_agency
office
opportunity_type

published_date
offers_due_date

naics_code
psc_code
contract_type

raw_page_text

extracted_json
fit_score
fit_recommendation
fit_reasoning

proposal_draft

created_at
```

---

# 5.2 Table: solicitation_links

Stores links referenced in the solicitation page.

Links are **stored but not processed** in MVP.

Fields:

```
id (PK)

solicitation_id (FK)

link_text
url
link_type

is_processed (default false)

created_at
```

Example link types:

```
amendment
solicitation_version
attachment
unknown
```

---

# 5.3 Table: contractor_profiles

Stores contractor capability profiles.

Fields:

```
id (PK)

company_name
capabilities_json

created_at
```

The MVP will use **one predefined contractor profile**.

---

# 6. Contractor Capability Profile

The system loads a predefined JSON file representing the contractor.

Example:

```
{
  "company_name": "AeroShield Defense Systems",

  "domains": [
    "defense",
    "aerospace",
    "aircraft sustainment"
  ],

  "core_capabilities": [
    "airframe structural repair",
    "military aircraft component overhaul",
    "inspection and maintenance"
  ],

  "platform_experience": [
    "fighter aircraft structures",
    "naval aviation sustainment"
  ],

  "manufacturing_capabilities": [
    "composite repair",
    "metal structure repair"
  ],

  "compliance_capabilities": [
    "Buy American familiarity",
    "defense supply chain processes"
  ],

  "past_performance": [
    "military aircraft maintenance support",
    "structural repair programs"
  ]
}
```

---

# 7. Capability Matching Logic

The system compares solicitation requirements against contractor capabilities.

### Matching categories

```
technical capability match
platform/domain alignment
compliance readiness
risk penalty
```

### Scoring weights

```
technical capability match: 40%
platform relevance: 25%
compliance readiness: 20%
risk penalty: 15%
```

### Example result

```
Score: 78

Recommendation: BID

Reasoning:
- strong alignment with aircraft structural repair scope
- contractor platform experience relevant
- moderate compliance complexity
```

If score < threshold (example: 50):

```
Recommendation: NO BID
```

---

# 8. Proposal Generation

The system generates a **draft proposal package** using an LLM and a template.

This proposal is a **first draft**, not a final submission.

---

## Proposal Sections

The generated proposal includes:

```
Executive Summary

Opportunity Understanding

Technical Approach

Management / Execution Approach

Compliance Alignment

Risks and Assumptions

Conclusion
```

The proposal is stored in the database as structured text or JSON.

---

# 9. Bid Decision Logic

After scoring:

```
if score >= threshold:
    recommendation = BID
else:
    recommendation = NO_BID
```

The output must include:

```
fit_score
recommendation
reasoning
```

---

# 10. API Design (Example)

## POST /analyze

Input:

```
{
  "url": "<solicitation_url>"
}
```

Output:

```
{
  "solicitation_summary": {},
  "fit_score": 78,
  "recommendation": "BID",
  "reasoning": [],
  "proposal_draft": {}
}
```

---

# 11. User Interface (Minimal)

Single-page interface.

### Input

```
Soliciation URL field
Analyze button
```

### Output

Sections displayed:

```
Solicitation Summary
Extracted Fields
Contractor Fit Score
Bid / No-Bid Recommendation
Reasoning
Proposal Draft
Stored Link References
```

---

# 12. Non-Goals for MVP

The following are intentionally **out of scope**:

* parsing attachments or amendments
* retrieving additional documents
* automated pricing generation
* submission of proposals
* contractor authentication systems
* multi-company support

However, the schema supports future expansion.

---

# 13. Future Extensions

Potential future enhancements:

* parse amendment PDFs
* retrieve statement of work attachments
* multi-document analysis
* proposal compliance matrix
* FAR/DFARS clause interpretation
* contractor capability learning
* historical award comparison
* pricing estimation

---

# 14. Success Criteria

The MVP is considered successful if:

1. A SAM.gov opportunity URL can be ingested
2. Page text is scraped and stored
3. LLM extracts structured procurement data
4. Contractor capabilities are compared
5. A fit score is produced
6. A proposal draft is generated
7. The system returns a **bid/no-bid recommendation**

---

# 15. Deliverables

The completed project must include:

```
source code
database schema
contractor capability profile
LLM extraction prompt
proposal generation prompt
documentation (this spec)
```

---

# End of Specification
