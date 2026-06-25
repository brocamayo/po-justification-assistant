# PO Justification Assistant

A Streamlit web app that turns a free-form description of a purchase into a clean, structured **purchase-order justification** — and delivers it straight to Microsoft Teams.

Built to remove the repetitive, blank-page work of writing PO justifications by hand, while keeping the output consistent and professional.

## What it does

1. You describe what you need to buy in plain language.
2. The app calls the **Claude API** using **forced tool use**, which guarantees the response comes back as structured JSON — never free-form text.
3. It produces a justification broken into four standard sections:
   - **What** — what is being purchased and its purpose
   - **Why** — the business need it addresses
   - **Why now** — the timing / urgency
   - **Why good value** — cost justification
4. With one click, the finished justification is posted to a **Microsoft Teams** channel via webhook.

## Tech stack

| Layer | Tool |
|-------|------|
| UI | Streamlit |
| AI | Anthropic Claude API (forced tool use → structured JSON) |
| Delivery | Microsoft Teams webhook |
| Packaging | Docker / docker-compose (Envoy reverse proxy) |
| Config | `.env` (see `.env.example`) |

## Why forced tool use?

Instead of parsing free-text and hoping the format holds, the app defines a `record_justification` tool with a strict input schema. Claude is required to call it, so every response is valid, predictable JSON with all four sections present — no post-processing or regex cleanup.

## Getting started

```bash
# 1. Configure
cp .env.example .env        # add your ANTHROPIC_API_KEY and Teams webhook URL

# 2. Run locally
pip install -r requirements.txt
streamlit run app.py

# — or with Docker —
docker-compose up
```

## Project structure

```
app.py            # Streamlit UI + entry point
generator.py      # Claude API integration (forced tool use)
teams_sender.py   # Posts the justification to Microsoft Teams
docker-compose.yaml
.env.example      # Required config keys
```

## Why I built it

As a Program Manager, I write and review purchase justifications regularly. This tool keeps them consistent, fast to produce, and easy to route to the right channel — a small workflow automation that compounds over hundreds of POs.
