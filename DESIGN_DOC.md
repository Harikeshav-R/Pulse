# TRIALPULSE

## AI-Powered Patient Safety & Engagement Platform

### Design Document

**Medpace Hackathon 2025**

Version 2.0 | March 2026

**CONFIDENTIAL**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Proposed Solution](#proposed-solution)
4. [System Architecture](#system-architecture)
5. [AI and Machine Learning Components](#ai-and-machine-learning-components)
6. [User Experience Design](#user-experience-design)
7. [Data Privacy and Regulatory Compliance](#data-privacy-and-regulatory-compliance)
8. [Integration and Interoperability](#integration-and-interoperability)
9. [Development Roadmap](#development-roadmap)
10. [Competitive Differentiation](#competitive-differentiation)
11. [Success Metrics and KPIs](#success-metrics-and-kpis)
12. [Risks and Mitigations](#risks-and-mitigations)
13. [Hackathon Demo Setup and Mock Data Guide](#hackathon-demo-setup-and-mock-data-guide)
14. [Conclusion](#conclusion)

---

## Executive Summary

TrialPulse is an AI-powered patient safety and engagement platform designed to transform how clinical trial participants interact with research teams and how researchers monitor patient well-being. The platform addresses critical inefficiencies in the current clinical trial process: delayed adverse event detection, poor patient engagement between scheduled visits, fragmented data collection, and the burden of manual safety monitoring.

By combining a conversational AI symptom journal (with both text chat and real-time voice interaction), passive wearable health monitoring, and a real-time researcher safety dashboard, TrialPulse closes the gap between scheduled clinical visits and provides continuous, intelligent oversight of patient health throughout the trial lifecycle.

The platform targets three primary stakeholders: trial patients who need an intuitive way to report symptoms (via their phone, in text or voice), clinical research coordinators (CRCs) who manage day-to-day patient interactions, and principal investigators (PIs) who must ensure participant safety and data integrity.

The hackathon prototype is built as a fully local, Dockerized stack — a Python/FastAPI async monolith backend with LangChain/LangGraph for vendor-agnostic LLM orchestration, a React Native mobile app for patients, a React web dashboard for researchers, and a self-hosted LiveKit server for real-time voice check-ins. No cloud services are required; everything runs on a single machine via Docker Compose.

---

## Problem Statement

### Current Pain Points

Clinical trials today suffer from several interconnected problems that reduce both patient safety and data quality:

**Delayed adverse event detection:** Patients typically see their clinical team only at scheduled visits, which may be weeks or months apart. Symptoms that arise between visits often go unreported until the next appointment, delaying critical safety signals.

**Low patient engagement and retention:** Trial participants frequently feel disconnected from their care team. Paper diaries and periodic phone calls are inconvenient and impersonal, contributing to high dropout rates that can reach 30% in some therapeutic areas.

**Manual, fragmented data collection:** CRCs spend significant time transcribing patient-reported outcomes from paper forms, reconciling data from multiple sources, and chasing missing entries. This manual process is error-prone and time-intensive.

**Reactive safety monitoring:** Current safety workflows are largely reactive. Researchers review adverse events after they are reported, rather than proactively identifying patients at risk based on trending data.

### Impact

These issues collectively result in delayed safety signals that can endanger patients, inflated trial costs due to site monitoring overhead and patient attrition, reduced data quality that complicates regulatory submissions, and slower time-to-market for potentially life-saving therapeutics.

---

## Proposed Solution

### Solution Overview

TrialPulse is a three-component platform that provides continuous, intelligent patient monitoring and engagement throughout the clinical trial lifecycle:

### Component 1: AI Symptom Journal

A mobile-first conversational interface (React Native) that replaces traditional paper diaries. The AI adapts its questions based on the specific trial protocol, therapeutic area, and the patient's individual history. Patients can interact via text chat or real-time voice conversation. Instead of generic questionnaires, patients engage in natural-language conversations that feel more like a check-in with a nurse than filling out a form.

- Adaptive questioning tailored to the trial's therapeutic area and specific drug safety profile, orchestrated by a LangGraph state machine
- Natural language processing via LangChain's vendor-agnostic LLM abstraction to interpret free-text symptom descriptions and map them to MedDRA-coded adverse event terms — swap between Anthropic, OpenAI, or local models with zero code changes
- Real-time voice check-in powered by LiveKit (self-hosted), where patients speak naturally to the AI agent and see a live transcript on screen; the same LangGraph conversation flow drives both text and voice modalities
- Configurable reminder schedules aligned with the trial protocol's visit windows
- Demoed on a real mobile device via React Native + Expo

### Component 2: Wearable Health Integration

A data ingestion layer that connects to consumer wearable devices and passively collects objective health metrics without requiring active patient input. An anomaly detection engine continuously analyzes incoming data to flag clinically meaningful deviations.

- Integration with Apple HealthKit, Google Health Connect, and Fitbit Web API
- Continuous collection of heart rate, heart rate variability, resting heart rate trends, sleep duration and quality, step count and activity levels, and blood oxygen saturation (SpO2)
- Statistical anomaly detection using patient-specific baselines rather than population averages
- Configurable alert thresholds that can be tuned per-protocol by the medical monitor
- For the hackathon, pre-generated mock wearable data with baked-in anomaly patterns replaces real device integration

### Component 3: Researcher Safety Dashboard

A web-based React dashboard that aggregates all patient-reported and wearable data into a unified view for clinical research coordinators and investigators. AI-generated risk scores help teams prioritize which patients need immediate attention. Real-time WebSocket updates ensure the dashboard reflects new check-ins and alerts within seconds.

- Per-patient timelines combining symptom reports, wearable trends, and scheduled visit data
- Cohort-level visualizations for identifying safety signals across treatment groups
- AI-generated risk scores that rank patients by urgency, factoring in symptom severity, trend direction, and wearable anomalies
- Automated alert routing based on severity: low-priority items queue for the next visit, medium-priority items trigger CRC outreach, and high-priority items escalate to the medical monitor
- Export capabilities for regulatory reporting in ICH E2B format

---

## System Architecture

### High-Level Architecture

TrialPulse is built as a **Python/FastAPI asynchronous monolith** backend with clear module boundaries, fronted by two presentation layers (React Native mobile app, React web dashboard). All services run locally in Docker containers orchestrated by Docker Compose. There are no cloud dependencies — the entire stack is self-contained for hackathon development and demoing.

| Layer | Components | Technology |
|-------|-----------|-----------|
| Presentation | Patient mobile app, Researcher web dashboard | React Native + Expo (mobile), React + TypeScript (web) |
| Reverse Proxy | Request routing, CORS, rate limiting | Nginx (Docker) |
| Application (Monolith) | Symptom Journal Module, Wearable Ingestion Module, Alert Engine, Analytics Module, Voice Agent Module | Python 3.12 + FastAPI (fully async), native WebSockets |
| LLM Orchestration | Conversational check-in agent, symptom classifier, vendor-agnostic LLM abstraction | LangChain + LangGraph (swap Anthropic / OpenAI / local via env var) |
| Real-Time Voice | STT → LangGraph Agent → TTS pipeline for voice check-ins | LiveKit Server (self-hosted Docker) + LiveKit Agents SDK (Python) + Deepgram STT |
| Data | Patient records, wearable time-series, alerts, risk scores | PostgreSQL 16 (Docker) |
| Cache & Events | Async event bus (pub/sub), caching, session state | Redis 7 (Docker) |
| Object Storage | Exported reports, voice recordings | MinIO (Docker, S3-compatible) |

### Monolith Design Rationale

The backend is a single FastAPI application organized into logical modules rather than separate microservices. This is a deliberate hackathon decision:

- A monolith avoids inter-service network complexity, simplifies debugging, and allows shared in-process access to database connections, the Redis event bus, and LangGraph agent state.
- All backend code is Python — no Node.js or JavaScript/TypeScript on the backend. JS/TS is reserved exclusively for the frontend (React Native mobile app and React web dashboard).
- The monolith is fully asynchronous end-to-end: `asyncpg` for PostgreSQL, `redis.asyncio` for Redis, `async def` on every endpoint and handler, native FastAPI WebSockets for real-time dashboard updates.

### Data Flow

The system processes data through three primary pipelines:

**Patient-Reported Data Pipeline:** Patient opens the React Native app and engages with the AI symptom journal (via text or voice). The LangGraph check-in agent processes responses in real time, guiding the conversation through a state machine (greeting → overall feeling → symptom screening → deep dive → summary → closing). When the session completes, the full conversation is sent to a separate LangGraph classifier that extracts and classifies symptoms against MedDRA terminology. Structured symptom data is stored in PostgreSQL and an event is published to the Redis event bus. The Alert Engine (an in-process subscriber) evaluates the event against rules and generates alerts if thresholds are exceeded. The WebSocket manager pushes updates to connected dashboard clients in real time.

**Wearable Data Pipeline:** Wearable devices sync health metrics to the phone's native health platform (HealthKit or Health Connect). The React Native app reads from these platforms at configurable intervals and transmits data to the Wearable Ingestion Module via REST API. For the hackathon, mock data is pre-seeded. Time-series data is stored in PostgreSQL (with timestamped rows and JSONB fields — InfluxDB is omitted for hackathon simplicity). The anomaly detection engine compares current values against the patient's rolling baseline using z-score analysis and sliding-window linear regression. Anomalies are published to the Redis event bus and flow through the same alert pipeline.

**Alert and Notification Pipeline:** The Alert Engine evaluates incoming events from both pipelines against protocol-specific rules (severe symptom, SAE keywords, wearable anomaly, missed check-in, risk score elevation). Alerts are classified by severity and routed to the researcher dashboard via WebSocket push. All alert decisions are logged. For the hackathon, notifications are dashboard-only (no email/SMS).

---

## AI and Machine Learning Components

### LLM Orchestration (LangChain + LangGraph)

All LLM interactions are orchestrated through **LangChain** (for vendor-agnostic model abstraction) and **LangGraph** (for stateful multi-step agent workflows). This ensures zero vendor lock-in — the LLM provider and model are configured via environment variables and can be swapped without any code changes.

```
# .env configuration — change provider with zero code changes
LLM_PROVIDER=anthropic          # or "openai", "ollama" (local)
LLM_MODEL=claude-sonnet-4-20250514  # or "gpt-4o", "llama3:8b"
LLM_API_KEY=sk-ant-...
```

**Supported providers:** Anthropic (Claude), OpenAI (GPT-4o), local models via Ollama — all through the same LangChain interface.

### Conversational Check-In Agent (LangGraph State Machine)

The core AI component of the symptom journal is a LangGraph state machine that orchestrates the check-in conversation. The graph defines the conversation flow as a series of nodes (greeting, overall feeling, symptom screening, symptom deep dive, protocol-specific questions, summary, closing) with conditional edges that route based on patient responses. The same graph serves both text and voice modalities — the only difference is the input source (typed text vs. speech transcript from LiveKit STT).

| Aspect | Details |
|--------|---------|
| Orchestration | LangGraph state machine with typed state (Pydantic models) |
| LLM Provider | Configurable via LangChain abstraction — Anthropic, OpenAI, or local |
| Output | Structured JSON with MedDRA preferred term, severity grade (CTCAE v5), onset date, and relationship to treatment |
| Guardrails | Cannot provide medical advice; escalates to clinical team for urgent symptoms; all outputs reviewed by CRC before entering the trial database |
| Accuracy Target | > 90% concordance with physician-coded AEs on held-out test set |

### Symptom Classification Pipeline (LangGraph)

When a check-in session completes, the full conversation is sent to a separate LangGraph that extracts and classifies symptoms. The graph has two nodes: (1) extract — the LLM reads the conversation and produces structured symptom classifications, and (2) validate — each classification is validated against known MedDRA codes, severity ranges, and confidence thresholds. Invalid classifications are filtered out.

### Real-Time Voice Agent (LiveKit)

The voice check-in feature uses a self-hosted LiveKit server (running in Docker) with the LiveKit Agents SDK integrated into the Python backend. The pipeline is: patient speaks → WebRTC audio stream to LiveKit → STT (Deepgram or Whisper) → transcript fed to the same LangGraph check-in agent → response text → TTS (Deepgram or Coqui) → audio streamed back to patient. A live transcript is displayed on the mobile app during the conversation, and all transcribed messages are stored as `checkin_messages` with `message_type = 'voice_transcript'`.

### Wearable Anomaly Detection

The anomaly detection engine uses statistical methods to identify clinically meaningful deviations in wearable data:

1. **Baseline Establishment:** During the first 7–14 days of enrollment, the system collects baseline metrics for each patient, calculating personalized means, standard deviations, and normal ranges. Outliers are removed using IQR filtering.

2. **Real-Time Comparison:** Incoming data points are compared against the patient's personal baseline using z-score analysis. Points exceeding configurable thresholds (default: 2.5 standard deviations) are flagged as point anomalies.

3. **Trend Detection:** A sliding-window linear regression detects gradual trends that might not trigger point-based anomalies but indicate a meaningful shift (e.g., resting heart rate increasing by 0.5 BPM/day over two weeks = +7 BPM total).

4. **Contextual Filtering:** The engine cross-references anomalies with patient-reported activity data to reduce false positives (e.g., elevated heart rate during reported exercise is suppressed).

### Risk Scoring Model

A composite risk score (0–100) is calculated for each patient after every new data point and recalculated daily via a scheduled background task (APScheduler). The score combines multiple signal sources:

| Signal Source | Weight | Factors |
|--------------|--------|---------|
| Symptom Reports | 40% | Severity grade, number of concurrent symptoms, trajectory (worsening vs. stable) |
| Wearable Anomalies | 30% | Number of flagged metrics, magnitude of deviation, persistence |
| Engagement | 15% | Missed check-ins, declining response length, delayed responses |
| Protocol Compliance | 15% | Missed visits, medication adherence signals, out-of-window data submissions |

Patients are categorized into three risk tiers: Low (score 0–30, routine monitoring), Medium (score 31–70, CRC outreach recommended), and High (score 71–100, immediate escalation to medical monitor).

---

## User Experience Design

### Patient Mobile App (React Native + Expo)

The patient experience is designed around three principles: minimal friction, emotional warmth, and clinical rigor. Patients should feel cared for, not surveilled. The app is built with React Native and Expo for cross-platform support, and is demoed on a real mobile device during the hackathon presentation.

#### Onboarding Flow (Simplified for Hackathon)

1. Patient opens the app and selects from pre-loaded demo accounts (no enrollment code entry needed for the demo).
2. The app auto-configures based on the trial protocol: therapeutic area, expected side effects, check-in frequency, and wearable status.
3. A brief guided tutorial shows the patient the text check-in and voice check-in options.

#### Daily Check-In Experience (Text)

The AI symptom journal presents as a chat interface. A typical interaction begins with a gentle prompt ("Hi David, how are you feeling today?") and adapts based on the response. If the patient reports a headache, the AI follows up with questions about severity, onset, duration, and whether they took any medication. If the patient reports feeling fine, the check-in is brief.

Key design decisions: a warm, empathetic tone that avoids clinical jargon while still collecting clinically precise data. Quick-reply buttons for common responses reduce typing burden. A progress indicator shows the patient how much of the check-in remains. Historical entries are visible in a personal health timeline, giving patients a sense of agency over their data.

#### Daily Check-In Experience (Voice)

Patients can alternatively tap "Start Voice Check-In" to enter a real-time voice session powered by LiveKit. The AI agent speaks the same questions it would type, and the patient responds naturally by speaking. The experience includes an animated avatar that pulses when the AI is speaking, a live transcript panel showing both patient speech and AI responses in real time, voice activity indicators, and the ability to switch to text mid-session. Quick-reply chips remain available for structured inputs (severity ratings, yes/no) even during voice mode.

#### Mobile App Screens

- **Home:** Greeting, check-in status, two CTAs ("Start Text Check-In" / "Start Voice Check-In"), health summary strip with latest wearable metrics, timeline preview
- **Chat (Text Check-In):** Chat bubbles, quick reply bar, severity slider, date picker, progress indicator
- **Voice Check-In:** Agent avatar, live transcript, voice activity indicator, mute/unmute, switch-to-text button
- **Health Timeline:** Chronological events with filter chips (All, Symptoms, Wearable Alerts, Visits)
- **Wearable Dashboard:** Connection status, metric cards with sparklines and baseline bands, anomaly banners
- **Profile:** Trial info, notification preferences, wearable management

### Researcher Dashboard (React + TypeScript)

The dashboard is designed for CRCs and PIs who manage multiple patients across multiple trials. The default view is a patient priority list sorted by risk score, with color-coded indicators. Real-time WebSocket updates ensure new alerts and check-in completions appear instantly without refreshing.

Key dashboard views:

- **Patient List:** Sortable by risk score, last check-in date, next scheduled visit, and treatment arm. Risk score badges are color-coded (🟢 low, 🟡 medium, 🔴 high).
- **Patient Detail:** Individual timeline showing symptom reports, wearable trends, and alert history overlaid on a single chronological view. Wearable charts show 14-day trends with baseline bands. Check-in entries indicate whether they were text or voice sessions.
- **Cohort Analytics:** Aggregate views comparing adverse event rates, wearable metric distributions, and engagement patterns across treatment arms.
- **Alert Management:** A queue of unresolved alerts with one-click acknowledgment, note-taking, and escalation actions. Alerts update in real time via WebSocket.
- **CRC Symptom Review Panel:** Confirm or override AI symptom classifications before they enter the official trial record.

---

## Data Privacy and Regulatory Compliance

### Hackathon Scope

Full HIPAA, GDPR, 21 CFR Part 11, and ICH E6(R2) compliance is **out of scope** for the hackathon prototype. All data is synthetic mock data running on a local machine. No real patient data is involved. The following section documents the production-intent design for reference only.

### Production-Intent Data Protection Measures (Not Implemented in Hackathon)

| Requirement | Production Implementation |
|-------------|--------------------------|
| Encryption at Rest | AES-256 encryption for all databases; S3 server-side encryption with customer-managed KMS keys |
| Encryption in Transit | TLS 1.3 for all API communications; certificate pinning in the mobile app |
| Access Control | Role-based access control (RBAC) with per-trial, per-site permissions; multi-factor authentication required for all researcher accounts |
| Audit Logging | Immutable audit trail for all data access, modifications, and exports; logs stored in append-only storage with 7-year retention |
| Data Minimization | Wearable data is aggregated to hourly summaries after 90 days; raw data purged after trial completion unless regulatory hold requires retention |
| Patient Rights | In-app data export (FHIR R4 format); account deletion with cryptographic erasure of all associated data |
| 21 CFR Part 11 | Electronic signatures with unique user identification; system validation documentation; tamper-evident audit trails |

### Hackathon Simplifications

- No TLS (all traffic is localhost HTTP)
- No encryption at rest
- No audit logging
- No PII — all patient data is synthetic
- Hardcoded demo accounts, no real authentication flow
- No consent management
- No MFA

### De-Identification Strategy (Production Intent)

Patient data within the analytics pipeline is pseudonymized using a one-way hash of the patient's trial enrollment ID. The mapping between enrollment IDs and personal identifiers is maintained exclusively by the trial site and is never transmitted to or stored by TrialPulse's infrastructure. AI model training uses only fully de-identified data sets reviewed and approved by an independent IRB.

---

## Integration and Interoperability

### Clinical Systems Integration (Production Roadmap)

TrialPulse is designed to complement, not replace, existing clinical trial technology stacks. These integrations are part of the production roadmap and are not implemented in the hackathon prototype.

| System Type | Integration Method | Data Flow |
|------------|-------------------|-----------|
| EDC (e.g., Medidata Rave, Oracle InForm) | REST API or CDISC ODM export | TrialPulse pushes CRC-reviewed symptom data to the EDC as source-verified ePRO entries |
| CTMS (e.g., Oracle Siebel, Veeva) | Bidirectional API | Patient enrollment status and visit schedules sync from CTMS; engagement metrics push back |
| Safety Databases (e.g., Argus, ArisGlobal) | ICH E2B(R3) XML export | Serious adverse events flagged in TrialPulse can be exported directly for regulatory submission |
| EHR Systems | SMART on FHIR R4 | Optional integration for sites that want TrialPulse data visible within their clinical workflow |

---

## Development Roadmap

### Phase 1: Hackathon Prototype (Weeks 1–2) — CURRENT PHASE

**Technology choices:**

- **Backend:** Python 3.12 + FastAPI async monolith (no Node.js/microservices)
- **LLM:** LangChain + LangGraph for vendor-agnostic orchestration
- **Voice:** LiveKit (self-hosted Docker) + Deepgram STT + TTS
- **Mobile:** React Native + Expo (demoed on real device)
- **Dashboard:** React + TypeScript + Tailwind + Recharts
- **Data:** PostgreSQL 16 + Redis 7 + MinIO (all Docker)
- **Infrastructure:** Docker Compose (localhost only, no cloud)

**Deliverables:**

- Functional patient mobile app with AI symptom journal — text chat and voice check-in (single therapeutic area: oncology)
- Simulated wearable data feed with anomaly detection (pre-generated mock data)
- Basic researcher dashboard with patient list, risk scores, patient detail timeline, and alert queue
- Real-time end-to-end data flow: patient checks in → AI classifies → risk score updates → alert appears on dashboard via WebSocket
- Live demo with mock data for 5 patients across a spectrum of risk profiles

### Phase 2: Pilot-Ready MVP (Months 1–3)

- Apple HealthKit and Google Health Connect integration with real wearable devices
- Multi-protocol support with configurable symptom questionnaires
- HIPAA-compliant cloud infrastructure with encryption and access controls
- CRC workflow tools: alert management, patient messaging, note-taking
- Real authentication flow (enrollment codes, JWT, MFA)
- Offline support with sync queue

### Phase 3: Clinical Validation (Months 4–6)

- IRB-approved pilot study with 50–100 patients across 2–3 trial sites
- Validation of AI symptom classifier accuracy against physician-coded AEs
- Usability testing with patients and CRCs; iterative UX refinement
- EDC integration with one major platform (Medidata or Oracle)

### Phase 4: Production Scale (Months 7–12)

- 21 CFR Part 11 validated deployment
- Multilingual support (top 10 languages for global trials)
- Advanced analytics: predictive dropout modeling, cohort safety signal detection
- SOC 2 Type II certification
- Migration from monolith to microservices if scale demands it

---

## Competitive Differentiation

Several products address individual aspects of the problem TrialPulse solves, but none combine all three pillars (AI-driven patient engagement, passive wearable monitoring, and intelligent safety dashboards) into a unified platform:

| Competitor / Category | What They Do | TrialPulse Differentiator |
|----------------------|-------------|--------------------------|
| ePRO Platforms (e.g., Medidata Patient Cloud) | Electronic patient diaries with structured questionnaires | TrialPulse uses conversational AI (LangGraph) for adaptive, natural-language check-ins — plus real-time voice interaction via LiveKit — rather than rigid form-based data capture |
| Wearable Platforms (e.g., Koneksa, ActiGraph) | Collect sensor data from clinical-grade devices | TrialPulse integrates with consumer wearables patients already own, lowering the barrier to participation |
| Safety Monitoring Tools (e.g., ArisGlobal, Oracle Argus) | Post-hoc adverse event management and regulatory reporting | TrialPulse provides proactive, real-time risk scoring and trending before events escalate to reportable AEs |
| Patient Engagement Apps (e.g., Clario, YPrime) | Visit reminders, medication logs, and basic PRO capture | TrialPulse combines engagement with intelligent safety monitoring, making the patient app clinically actionable, not just administrative |
| Voice-based health tools | Generic voice assistants or IVR-based symptom collection | TrialPulse's voice agent is protocol-aware, uses the same clinical LangGraph as text check-in, and produces structured MedDRA-coded outputs — not just free-text transcripts |

---

## Success Metrics and KPIs

The following metrics will be used to evaluate TrialPulse's effectiveness during the pilot phase and beyond:

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Patient Check-In Compliance | > 80% of scheduled check-ins completed | App analytics: completed sessions / scheduled sessions |
| Time to Adverse Event Detection | 50% reduction vs. traditional site-visit-only reporting | Compare AE onset date to first documentation date in TrialPulse vs. EDC |
| CRC Time Savings | 30% reduction in per-patient data management time | Time-motion study comparing CRC workflows with and without TrialPulse |
| Patient Satisfaction (NPS) | > 50 Net Promoter Score | In-app survey at trial midpoint and completion |
| False Positive Alert Rate | < 15% of medium/high alerts deemed clinically insignificant | CRC adjudication of alerts over 30-day measurement period |
| AI Symptom Classification Accuracy | > 90% concordance with physician coding | Blinded comparison of AI-classified vs. physician-classified AEs |
| Voice Check-In Adoption | > 30% of check-ins completed via voice | App analytics: voice sessions / total sessions |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| AI misclassifies a serious adverse event | Medium | Critical | All AI-generated classifications are reviewed by a CRC before entering the trial record; high-severity keywords trigger immediate human escalation regardless of AI classification |
| Low patient adoption of mobile app | Medium | High | Intuitive onboarding, minimal daily time commitment (< 3 minutes per check-in), voice option for patients who prefer speaking over typing, site-level training for CRCs to coach patients |
| Wearable data inconsistency across devices | High | Medium | Normalize data to common units and sampling rates at ingestion; validate against known device specifications; surface data quality indicators on the dashboard |
| Regulatory pushback on AI-generated data | Medium | High | Position TrialPulse as a decision-support tool, not a medical device; maintain human-in-the-loop for all safety decisions; engage regulatory consultants early |
| LLM vendor lock-in or pricing changes | Medium | Medium | LangChain + LangGraph provide complete vendor abstraction; swap providers via env var; support for local models (Ollama) as zero-cost fallback |
| Voice transcription accuracy issues | Medium | Medium | Display live transcript for patient review; store both audio and transcript; allow patients to correct or switch to text at any time; flag low-confidence transcriptions for CRC review |
| Data breach or HIPAA violation | Low | Critical | Defense-in-depth security architecture (production); annual penetration testing; incident response plan with < 72-hour breach notification; for hackathon, all data is synthetic |

---

## Hackathon Demo Setup and Mock Data Guide

This section provides step-by-step instructions for setting up the complete demo environment with mock data, preparing the system for a live demo in front of a judging panel.

### Prerequisites

Ensure the following are installed on the demo machine:

- **Docker Desktop** (v4.25+) with Docker Compose v2
- **Node.js** (v20+) and npm/yarn — for the React Native mobile app and React web dashboard
- **Python** (3.12+) — only needed if running seed scripts outside Docker
- **Expo CLI** (`npm install -g expo-cli`) for the React Native mobile app
- **Expo Go** app installed on the demo phone (iOS or Android)
- **API keys** (stored in `.env` file): `LLM_API_KEY` (Anthropic or OpenAI), `DEEPGRAM_API_KEY` (for voice STT — required only if demoing voice check-in)

### Environment Setup

**Step 1: Clone and configure**

```bash
git clone <repo-url> trialpulse && cd trialpulse
cp .env.example .env
# Edit .env: set LLM_API_KEY, LLM_PROVIDER, DEEPGRAM_API_KEY
```

**Step 2: Start all services**

```bash
docker compose up -d --build
```

This starts PostgreSQL, Redis, MinIO, LiveKit, the FastAPI backend, the React dashboard, and Nginx. The database schema and seed data are automatically loaded on first boot.

**Step 3: Verify**

```bash
docker compose ps          # All services "running" / "healthy"
curl http://localhost:8000/api/v1/health   # {"status": "ok", ...}
open http://localhost:3000                 # Dashboard loads
```

**Step 4: Start the mobile app**

```bash
cd apps/mobile && npm install && npx expo start
# Scan QR code with Expo Go on demo phone (same WiFi as laptop)
```

### Mock Data: 5 Patients with Realistic Profiles

The seed script generates 30 days of data for each patient in an oncology Phase II trial ("ONCO-2026-TP1" — Phase II Study of MT-401 in Advanced Non-Small Cell Lung Cancer, sponsored by Meridian Therapeutics).

**Patient 001 — "Maria Gonzalez" (Healthy Baseline)**
- Subject ID: 001-0089, Arm A, Risk Score: 8 🟢
- 28/30 check-ins completed, no symptoms, all wearables normal
- Purpose: Shows what a healthy, engaged patient looks like

**Patient 002 — "Robert Kim" (Mild Symptoms)**
- Subject ID: 001-0017, Arm B (Placebo), Risk Score: 22 🟢
- Grade 1 fatigue (ongoing), Grade 1 headache (resolved), normal wearables
- Purpose: Shows low-acuity data flowing through the system

**Patient 003 — "David Thompson" (THE DEMO PATIENT — Concerning Trend)**
- Subject ID: 001-0042, Arm A, Risk Score: 67 🟡 → escalates to 82 🔴 during live demo
- Escalating symptoms: Fatigue G1 → Nausea G1 → Nausea G2 + Headache G1 → **[LIVE: Grade 3 nausea + Grade 2 headache]**
- Wearable anomaly: Resting HR rising from 72 to 88 bpm over 14 days, declining sleep and steps
- Purpose: The star of the live demo — demonstrates the end-to-end alert flow

**Patient 004 — "Jennifer Walsh" (Missed Check-Ins)**
- Subject ID: 001-0055, Arm B, Risk Score: 45 🟡
- 18/30 check-ins completed, 3 consecutive misses, no symptoms reported
- Purpose: Shows engagement monitoring and missed check-in alerts

**Patient 005 — "Thomas Okafor" (High Risk)**
- Subject ID: 001-0033, Arm A, Risk Score: 85 🔴
- Multiple concurrent symptoms: Nausea G3, Headache G2, Fatigue G2
- Wearable anomalies: elevated HR, severe step/sleep decline, borderline SpO2
- Purpose: Shows what a high-risk patient looks like on the dashboard

### Live Demo Script (8–10 Minutes)

**Before going on stage:** Open dashboard on laptop (logged in as CRC), have mobile app open on phone with Patient 003 (David Thompson) selected, have Patient 003 detail view ready in a second browser tab.

**Act 1 — "The Problem" (1 min):** Show the dashboard with all 5 patients. Point out the risk score distribution. Highlight Patient 005 (high risk) and Patient 003 (medium, trending up).

**Act 2 — "Patient Text Check-In" (3 min):** On the phone, start a text check-in with Patient 003. Walk through the AI conversation: report severe nausea (7/10) and headache (5/10). Show the AI asking smart follow-up questions. Session completes.

**Act 3 — "Real-Time Dashboard Update" (2 min):** Switch to the laptop. Show the toast notification (🔴 CRITICAL: Grade 3 nausea), risk score animating from 67 → 82, the new alert in the queue. Open Patient 003 detail — show the timeline with the new entry and the wearable chart with the rising HR trend.

**Act 4 — "Voice Check-In" (2 min, if configured):** On the phone, start a voice check-in. Speak naturally about ongoing symptoms. Show the live transcript updating. Point out: "Same AI, same clinical logic — patients choose text or voice."

**Act 5 — "CRC Workflow" (1 min):** On the dashboard, open the pending symptom review. Show the AI's classification (Nausea → MedDRA 10028813, Grade 3, 94% confidence). Click "Confirm." Point out the human-in-the-loop.

**Act 6 — "Cohort Analytics" (1 min, if built):** Show AE incidence comparison between arms. Point out the statistically significant nausea signal in the treatment arm.

### Demo Reset

```bash
# Full reset (wipes database, reseeds)
docker compose down && docker volume rm trialpulse_pgdata && docker compose up -d --build

# Partial reset (keep base data, remove live demo check-ins)
python scripts/run_demo_scenario.py --reset
```

### Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend won't start | Check `docker compose logs backend` — likely missing `LLM_API_KEY` in `.env` |
| Mobile app can't connect | Ensure phone and laptop on same WiFi; update API URL to laptop's local IP |
| Voice check-in fails | Verify `DEEPGRAM_API_KEY` is set; check `docker compose logs livekit` |
| WebSocket updates missing | Check dashboard is connected to `ws://localhost:8000/ws`; inspect browser Network tab |
| Database empty | Run `python scripts/seed_demo_data.py` or restart postgres: `docker compose restart postgres` |

---

## Conclusion

TrialPulse represents a paradigm shift from reactive, visit-based clinical trial monitoring to continuous, intelligent patient engagement and safety oversight. By meeting patients where they are — on their phones, with their existing wearable devices, through text or voice — and empowering researchers with AI-driven insights, the platform has the potential to meaningfully improve patient safety, reduce trial costs, and accelerate the development of new therapeutics.

The hackathon prototype demonstrates this vision with a fully functional local stack: a Python/FastAPI async monolith with LangChain/LangGraph for vendor-agnostic LLM orchestration, a React Native mobile app with both text and voice check-in capabilities (powered by LiveKit), real-time wearable anomaly detection, and a live-updating researcher dashboard — all running in Docker containers on a single machine with no cloud dependencies.

The platform's modular monolith architecture allows it to be adopted incrementally: a sponsor could start with just the AI symptom journal for a single trial and expand to full wearable integration and safety dashboarding as confidence grows. The LangChain/LangGraph foundation ensures the AI components can evolve with the rapidly changing LLM landscape without rewriting application logic. This flexibility, combined with deep integration capabilities with existing clinical systems (planned for post-hackathon phases), positions TrialPulse as a practical, deployable solution rather than a theoretical exercise.

We believe this solution directly addresses the Medpace hackathon challenge by delivering clear value to patients (a better trial experience and faster safety response), to the industry (higher-quality data and reduced operational burden), and to the ultimate goal of accelerating safe, effective therapeutics to the patients who need them.
