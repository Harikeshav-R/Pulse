# Pulse

AI-powered clinical trial patient safety and engagement platform.

## Inspiration

Trial safety often depends on sparse site visits and delayed paper trails, while patients experience symptoms and behavior changes every day. We wanted a **continuous signal**—not to replace regulated workflows, but to help sites and sponsors **see risk earlier**, keep patients engaged, and reduce the gap between what happens in real life and what makes it into a safety narrative.

## What it does

**Pulse (TrialPulse)** connects **patients**, **wearables**, and **study teams** in one loop:

- **Mobile app** — Daily check-ins, structured capture of how patients feel, and pathways for voice/chat-style support (e.g. LiveKit-backed flows in the stack).
- **Backend** — FastAPI services for auth, patients, check-ins, wearables, alerts, voice, and analytics; **AI-assisted** classification and check-in reasoning (LangGraph-style flows); **risk scoring** and **alert** generation when patterns worsen.
- **CRC dashboard** — Trial overview, **patient list**, **alert queue**, **visit calendar**, and **cohort analytics** (risk distribution, AE-style views, wearable trends) so coordinators can prioritize who needs attention.

The goal: **one place** to monitor engagement, symptoms, and device-derived trends so escalations are **timely and explainable**.

## How we built it

- **Monorepo** with a **Python/FastAPI** backend (async SQLAlchemy, Pydantic), **PostgreSQL** for trial/patient/alert data, **Redis** for events and coordination, **MinIO** for object storage, and **Docker Compose** for a reproducible dev stack.
- **AI layer** — LLM access via **OpenRouter** (and Gemini-related paths for voice/agent experiments), with **graphs/agents** for check-in and classification workflows.
- **Real-time / voice** — **LiveKit** in the compose stack for future or demo-grade realtime/voice paths.
- **Dashboard** — **React + Vite**, TanStack Query, Recharts, and a proxy to the API for local development.
- **Mobile** — **Expo / React Native** app for the patient experience, wired to the same API concepts.

## Challenges we ran into

- **Glueing clinical nuance to engineering** — Balancing realistic CRC workflows (triaging alerts, audit-friendly language) with hackathon scope.
- **End-to-end environments** — Coordinating Postgres, Redis, LiveKit, and backend ports across laptops and Docker (e.g. host port conflicts, env parity between dashboard proxy and API).
- **Native + web + AI** — Keeping mobile, dashboard, and LLM pipelines aligned on the same domain models (patients, trials, symptoms, wearables) without over-building schema migrations mid-hack.

## Accomplishments that we're proud of

- A **credible vertical slice**: patient-facing app, API with multiple modules, and a **researcher dashboard** that tells a coherent safety story.
- **Risk and alerts** tied to **symptoms + wearable logic**, not just static mock UI.
- **Dockerized stack** others can actually run: DB seed paths, health checks, and a Makefile for common tasks.
- **Unified patient narrative** on the dashboard (e.g. combining check-in severity, HR trends, and fatigue context) to show how Pulse **summarizes** signal for busy CRCs.

## What we learned

- **Safety UX is product work** — Clear copy, alert wording, and “unified clinical picture” views matter as much as the model.
- **Async FastAPI + event bus patterns** scale better for **notifications and future realtime** than a purely CRUD API.
- **DevEx details** (Vite proxy to correct API port, `.env` parity) save hours when judges or teammates try to run the demo.

## What's next for Pulse

- Deeper **EDC / CTMS** integration hooks (exports, reference IDs) without storing PHI beyond policy.
- **Prospective validation** of risk scores with study statisticians; calibration per indication and arm.
- **Patient** — richer adherence nudges and localized content; **Site** — workload views and SLA-style alert routing.
- Hardening **voice** flows for regulated use (consent, retention, redaction) and expanding **wearable** normative baselines per protocol.
