# TrialPulse — Technical Design & Implementation Guide

## Complete System Architecture, Feature Specifications, and Build Instructions

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Design](#4-database-design)
5. [Component 1: AI Symptom Journal (Patient Mobile App)](#5-component-1-ai-symptom-journal)
6. [Component 2: Wearable Health Integration](#6-component-2-wearable-health-integration)
7. [Component 3: Researcher Safety Dashboard](#7-component-3-researcher-safety-dashboard)
8. [AI/ML Pipeline](#8-aiml-pipeline)
9. [Alert Engine](#9-alert-engine)
10. [Authentication & Authorization](#10-authentication--authorization)
11. [Data Privacy & Compliance](#11-data-privacy--compliance)
12. [API Specification](#12-api-specification)
13. [Deployment & Infrastructure](#13-deployment--infrastructure)
14. [Testing Strategy](#14-testing-strategy)
15. [Hackathon Prototype Scope](#15-hackathon-prototype-scope)
16. [Hackathon Demo Setup & Mock Data Guide](#16-hackathon-demo-setup--mock-data-guide)

---

## 1. Project Overview

### 1.1 What is TrialPulse?

TrialPulse is an AI-powered clinical trial patient safety and engagement platform composed of three integrated components:

1. **AI Symptom Journal** — A React Native mobile app where trial patients report symptoms through a conversational AI interface (text chat + real-time voice via LiveKit) that adapts questions based on their specific trial protocol.
2. **Wearable Health Integration** — A passive data pipeline that ingests health metrics from consumer wearables (Apple Watch, Fitbit, Garmin, etc.) and runs anomaly detection against patient-specific baselines.
3. **Researcher Safety Dashboard** — A web dashboard where clinical research coordinators (CRCs) and principal investigators (PIs) monitor patient health in real time, triage AI-generated alerts, and identify cohort-level safety signals.

### 1.2 Core Value Proposition

The platform closes the gap between scheduled clinical visits by providing continuous, intelligent monitoring. Today, a patient experiencing a gradual increase in resting heart rate or a new persistent headache might not report it until their next visit weeks later. TrialPulse catches these signals in real time and routes them to the right person.

### 1.3 Target Users

| User | Role | Primary Interactions |
|------|------|---------------------|
| **Trial Patient** | Enrolled participant in a clinical trial | Daily symptom check-ins via mobile app (text chat or voice); passive wearable data sharing |
| **Clinical Research Coordinator (CRC)** | Site-level staff managing day-to-day patient interactions | Dashboard monitoring; alert triage; patient messaging |
| **Principal Investigator (PI)** | Physician overseeing trial safety at the site | Cohort analytics; serious adverse event review; safety signal assessment |
| **Medical Monitor** | Sponsor-side physician responsible for overall trial safety | Escalated alerts; cross-site safety signal analysis |
| **Study Manager** | Sponsor-side operational lead | Protocol configuration; enrollment tracking; site performance metrics |

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                          │
│                                                                     │
│   ┌──────────────────┐          ┌──────────────────────────────┐   │
│   │  Patient Mobile   │          │   Researcher Web Dashboard   │   │
│   │  App (React       │          │   (React + TypeScript)       │   │
│   │  Native + Expo)   │          │                              │   │
│   │                   │          │  ┌────────┐ ┌────────────┐  │   │
│   │ ┌──────────────┐  │          │  │Patient │ │  Cohort    │  │   │
│   │ │ AI Chat UI   │  │          │  │List    │ │  Analytics │  │   │
│   │ ├──────────────┤  │          │  ├────────┤ ├────────────┤  │   │
│   │ │ LiveKit Voice│  │          │  │Patient │ │  Alert     │  │   │
│   │ │ Check-In     │  │          │  │Detail  │ │  Queue     │  │   │
│   │ ├──────────────┤  │          │  └────────┘ └────────────┘  │   │
│   │ │ Health       │  │          │                              │   │
│   │ │ Timeline     │  │          │                              │   │
│   │ ├──────────────┤  │          │                              │   │
│   │ │ Wearable     │  │          │                              │   │
│   │ │ Dashboard    │  │          │                              │   │
│   │ └──────────────┘  │          │                              │   │
│   └────────┬─────────┘          └──────────────┬───────────────┘   │
│            │                                    │                   │
└────────────┼────────────────────────────────────┼───────────────────┘
             │           HTTPS / WSS              │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     NGINX REVERSE PROXY (local)                     │
│   Rate Limiting │ Request Routing │ CORS │ Static File Serving      │
└────────────┬────────────────────────────────────┬───────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│               PYTHON / FASTAPI MONOLITH BACKEND                     │
│                    (fully async — asyncio)                           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   LangChain + LangGraph                       │  │
│  │                 LLM Orchestration Layer                        │  │
│  │  (vendor-agnostic: swap OpenAI, Anthropic, local models)      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  Symptom      │ │  Wearable    │ │  Alert   │ │  Analytics   │  │
│  │  Journal      │ │  Ingestion   │ │  Engine  │ │  Module      │  │
│  │  Module       │ │  Module      │ │          │ │              │  │
│  └──────┬───────┘ └──────┬───────┘ └────┬─────┘ └──────┬───────┘  │
│         │                │              │               │          │
│  ┌──────┴───────┐ ┌──────┴───────┐      │               │          │
│  │  AI/NLP      │ │  Anomaly     │      │               │          │
│  │  Classifier  │ │  Detection   │      │               │          │
│  │  (LangGraph) │ │  (numpy/     │      │               │          │
│  │              │ │  scikit)     │      │               │          │
│  └──────────────┘ └──────────────┘      │               │          │
│                                          │               │          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              LiveKit Integration Layer                        │  │
│  │  Real-time voice check-in agent (STT → LLM → TTS pipeline) │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              WebSocket Manager (native FastAPI WebSockets)    │  │
│  │  Real-time dashboard updates, chat streaming                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└──────────┬───────────────┬──────────────┬───────────────┬──────────┘
           │               │              │               │
           ▼               ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                │
│                     (all dockerized locally)                        │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostgreSQL   │  │  Redis 7     │  │  MinIO       │              │
│  │  16           │  │  (events,    │  │  (S3-compat  │              │
│  │  (Relational) │  │   cache,     │  │   object     │              │
│  │               │  │   pub/sub)   │  │   storage)   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  LiveKit      │                                                   │
│  │  Server       │                                                   │
│  │  (self-hosted │                                                   │
│  │   Docker)     │                                                   │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Monolith Backend Design

The entire backend is a single Python FastAPI application organized into logical modules. This is a deliberate hackathon decision — a monolith avoids inter-service network complexity, simplifies debugging, and allows shared in-process access to database connections, the Redis event bus, and LangChain/LangGraph agent state.

**Module boundaries within the monolith:**

```
app/
├── main.py                  # FastAPI app factory, lifespan events, middleware
├── config.py                # Pydantic Settings (env-based config)
├── deps.py                  # Dependency injection (DB sessions, Redis, etc.)
│
├── modules/
│   ├── auth/                # JWT issuance, password hashing, demo bypass
│   ├── checkin/             # Symptom journal chat + voice session management
│   ├── wearable/            # Wearable data ingestion, normalization, baselines
│   ├── alert/               # Alert rule engine, deduplication, risk scoring
│   ├── analytics/           # Cohort queries, AE incidence, exports
│   ├── dashboard/           # Staff-facing API endpoints
│   └── voice/               # LiveKit agent integration
│
├── ai/                      # LangChain + LangGraph orchestration
│   ├── chains/              # Reusable LangChain chains
│   ├── graphs/              # LangGraph state machines (check-in flow, classifier)
│   ├── prompts/             # Prompt templates
│   └── tools/               # LangChain tools (MedDRA lookup, risk calc, etc.)
│
├── models/                  # SQLAlchemy async ORM models
├── schemas/                 # Pydantic request/response schemas
├── events/                  # Redis pub/sub event bus
└── ws/                      # WebSocket connection manager
```

### 2.3 Service Communication (Internal Event Bus)

Since the backend is a monolith, all communication happens in-process via an async event bus backed by Redis pub/sub. This keeps the architecture decoupled internally while running in a single process.

```
Checkin Module
    │
    ├──▶ publishes "symptom.reported" event (via Redis pub/sub)
    │         │
    │         ▼
    │    Alert Engine (in-process subscriber)
    │         │
    │         ├──▶ evaluates rules
    │         ├──▶ publishes "alert.generated" event
    │         │         │
    │         │         ▼
    │         │    WebSocket Manager ──▶ pushes to dashboard clients
    │         │
    │         └──▶ updates risk_score in PostgreSQL
    │
    └──▶ stores symptom data in PostgreSQL

Wearable Module
    │
    ├──▶ stores time-series data in PostgreSQL (JSONB + timestamped rows)
    ├──▶ publishes "wearable.data_received" event
    │         │
    │         ▼
    │    Anomaly Detection (in-process)
    │         │
    │         ├──▶ compares against patient baseline
    │         ├──▶ publishes "anomaly.detected" event
    │         │         │
    │         │         ▼
    │         │    Alert Engine (same pipeline as above)
    │         │
    │         └──▶ stores anomaly records in PostgreSQL
    │
    └──▶ updates patient baseline statistics
```

**Event bus implementation (Redis pub/sub):**

```python
# app/events/bus.py
import asyncio
import json
from typing import Callable, Dict, List
import redis.asyncio as aioredis

class EventBus:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self._handlers: Dict[str, List[Callable]] = {}
        self._pubsub = None

    async def publish(self, event_type: str, payload: dict):
        """Publish an event to all subscribers."""
        message = json.dumps({"type": event_type, "payload": payload})
        await self.redis.publish("trialpulse:events", message)

    def subscribe(self, event_type: str, handler: Callable):
        """Register an async handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def start_listening(self):
        """Background task that listens for events and dispatches to handlers."""
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe("trialpulse:events")
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                event_type = data["type"]
                for handler in self._handlers.get(event_type, []):
                    asyncio.create_task(handler(data["payload"]))
```

---

## 3. Technology Stack

### 3.1 Frontend

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Patient Mobile App | React Native + Expo | Cross-platform (iOS/Android) from a single codebase; demo on a real mobile device |
| Chat UI | React Native Gifted Chat | Battle-tested chat interface with typing indicators, quick replies, and accessibility |
| Voice Check-In | LiveKit React Native SDK (`@livekit/react-native`) | Real-time voice sessions with the AI agent; low-latency STT/TTS |
| Researcher Dashboard | React 18 + TypeScript | Type safety for complex data models; large ecosystem of charting and table libraries |
| Dashboard Charts | Recharts + D3.js | Recharts for standard charts (bar, line, area); D3 for custom visualizations like patient timelines |
| Dashboard Tables | TanStack Table (React Table v8) | Headless table engine supporting sorting, filtering, pagination, and column resizing |
| State Management | Zustand (mobile) + React Query (both) | Zustand for lightweight local state; React Query for server state caching and background refetching |
| Styling | NativeWind (mobile) + Tailwind CSS (web) | Consistent utility-first styling across platforms |

### 3.2 Backend (Python Monolith)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Web Framework | Python 3.12 + FastAPI | Fully async; auto-generated OpenAPI docs; native WebSocket support; Pydantic validation |
| ASGI Server | Uvicorn | High-performance async server; runs the FastAPI app |
| LLM Orchestration | LangChain + LangGraph | Vendor-agnostic LLM abstraction; LangGraph for stateful multi-step agent workflows (check-in flow, classification); swap providers without code changes |
| Real-Time Voice | LiveKit Agents SDK (`livekit-agents`) + LiveKit server (self-hosted Docker) | Real-time voice pipeline: STT (Deepgram/Whisper) → LangGraph agent → TTS (ElevenLabs/Coqui); runs as a worker within the monolith |
| ORM | SQLAlchemy 2.0 (async) + asyncpg | Async PostgreSQL access; declarative models; migration support via Alembic |
| Migrations | Alembic | Database schema versioning and migration |
| Event Bus | Redis pub/sub (via `redis.asyncio`) | Decoupled in-process event-driven architecture; async pub/sub for alert pipeline |
| Background Tasks | FastAPI BackgroundTasks + asyncio tasks + APScheduler | Async task execution for risk score recalculation, check-in reminders, and data aggregation |
| WebSockets | Native FastAPI WebSockets | Real-time dashboard updates; no external dependency needed |
| Validation | Pydantic v2 | Request/response validation, settings management, JSON schema generation |

### 3.3 Data Stores (All Dockerized Locally)

| Store | Technology | What It Stores |
|-------|-----------|----------------|
| Primary Database | PostgreSQL 16 (Docker) | Patients, trials, protocols, symptom entries, alerts, user accounts, wearable time-series data (JSONB), audit trail |
| Cache + Event Bus | Redis 7 (Docker) | Pub/sub event bus, session data, rate limiting counters, real-time dashboard state, LLM response cache |
| Object Storage | MinIO (Docker, S3-compatible) | Consent documents, exported reports, audio recordings from voice check-ins |
| Voice Infrastructure | LiveKit Server (Docker, self-hosted) | Real-time voice room management, media routing for STT/TTS pipeline |

> **Note:** InfluxDB has been removed. For a hackathon prototype, wearable time-series data is stored directly in PostgreSQL using timestamped rows with JSONB fields. This eliminates an extra service and simplifies the stack. A dedicated time-series DB can be introduced later for production scale.

### 3.4 Infrastructure (Local Only)

| Component | Technology |
|-----------|-----------|
| Container Runtime | Docker |
| Orchestration | Docker Compose |
| Reverse Proxy | Nginx (Docker) |
| Database GUI (optional) | pgAdmin 4 (Docker) or DBeaver (local) |

> **Explicitly excluded for hackathon:** CI/CD pipelines, monitoring/alerting (Datadog, Grafana, Prometheus), log aggregation (Loki, CloudWatch), secrets management services (Vault, AWS Secrets Manager), CDN, cloud hosting, Kubernetes — none of these are needed for a local prototype.

---

## 4. Database Design

### 4.1 PostgreSQL Schema

#### Core Entities

```sql
-- =============================================================
-- TRIALS AND PROTOCOLS
-- =============================================================

CREATE TABLE trials (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sponsor_name      VARCHAR(255) NOT NULL,
    protocol_number   VARCHAR(100) NOT NULL UNIQUE,
    trial_title       TEXT NOT NULL,
    therapeutic_area  VARCHAR(100) NOT NULL,     -- e.g., 'oncology', 'cardiology', 'dermatology'
    phase             VARCHAR(10) NOT NULL,       -- 'I', 'II', 'III', 'IV'
    status            VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'setup', 'active', 'completed', 'terminated'
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE protocol_config (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id              UUID NOT NULL REFERENCES trials(id),
    checkin_frequency     VARCHAR(20) NOT NULL DEFAULT 'daily',  -- 'daily', 'weekly', 'twice_daily'
    checkin_window_hours  INT NOT NULL DEFAULT 24,
    expected_side_effects JSONB NOT NULL DEFAULT '[]',
    -- JSON array of objects: [{"term": "Headache", "meddra_code": "10019211", "expected_frequency": "common"}]
    symptom_questions     JSONB NOT NULL DEFAULT '[]',
    -- Ordered list of baseline questions for this protocol
    wearable_required     BOOLEAN NOT NULL DEFAULT false,
    wearable_metrics      JSONB NOT NULL DEFAULT '["heart_rate", "steps", "sleep"]',
    alert_thresholds      JSONB NOT NULL DEFAULT '{}',
    -- {"heart_rate_resting_max": 100, "spo2_min": 92, "anomaly_z_threshold": 2.5}
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- SITES AND STAFF
-- =============================================================

CREATE TABLE sites (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id      UUID NOT NULL REFERENCES trials(id),
    site_number   VARCHAR(50) NOT NULL,
    site_name     VARCHAR(255) NOT NULL,
    country       VARCHAR(100) NOT NULL,
    timezone      VARCHAR(50) NOT NULL DEFAULT 'UTC',
    status        VARCHAR(20) NOT NULL DEFAULT 'active',
    UNIQUE(trial_id, site_number)
);

CREATE TABLE staff (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    role          VARCHAR(30) NOT NULL,  -- 'crc', 'pi', 'medical_monitor', 'study_manager'
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE staff_site_access (
    staff_id  UUID NOT NULL REFERENCES staff(id),
    site_id   UUID NOT NULL REFERENCES sites(id),
    role      VARCHAR(30) NOT NULL,  -- role at this specific site
    PRIMARY KEY (staff_id, site_id)
);

-- =============================================================
-- PATIENTS
-- =============================================================

CREATE TABLE patients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id             UUID NOT NULL REFERENCES sites(id),
    enrollment_code     VARCHAR(50) NOT NULL UNIQUE,  -- code given to patient at screening
    subject_id          VARCHAR(50) NOT NULL,          -- blinded trial subject number
    treatment_arm       VARCHAR(50),                   -- null if still being randomized
    enrollment_date     DATE NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'enrolled',
    -- 'screening', 'enrolled', 'active', 'completed', 'withdrawn', 'discontinued'
    app_registered      BOOLEAN NOT NULL DEFAULT false,
    wearable_connected  BOOLEAN NOT NULL DEFAULT false,
    timezone            VARCHAR(50) NOT NULL DEFAULT 'UTC',
    language            VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(site_id, subject_id)
);

CREATE TABLE patient_app_accounts (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id        UUID NOT NULL UNIQUE REFERENCES patients(id),
    device_token      TEXT,           -- push notification token
    device_platform   VARCHAR(10),    -- 'ios', 'android'
    app_version       VARCHAR(20),
    last_active_at    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- SYMPTOM JOURNAL
-- =============================================================

CREATE TABLE checkin_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id),
    session_type    VARCHAR(20) NOT NULL DEFAULT 'scheduled',  -- 'scheduled', 'ad_hoc'
    modality        VARCHAR(10) NOT NULL DEFAULT 'text',       -- 'text', 'voice'
    status          VARCHAR(20) NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    duration_seconds INT,
    overall_feeling  INT,  -- 1-5 scale quick rating at start of check-in
    voice_room_id   VARCHAR(255),  -- LiveKit room ID if voice session
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE checkin_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES checkin_sessions(id),
    sequence_number INT NOT NULL,
    role            VARCHAR(10) NOT NULL,  -- 'ai', 'patient'
    content         TEXT NOT NULL,          -- message text (or transcribed voice)
    message_type    VARCHAR(20) NOT NULL DEFAULT 'text',
    -- 'text', 'quick_reply', 'scale_rating', 'date_picker', 'multi_select', 'voice_transcript'
    quick_replies   JSONB,  -- available quick reply options (for AI messages)
    selected_reply  VARCHAR(255),  -- which quick reply the patient selected
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE symptom_entries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id          UUID NOT NULL REFERENCES patients(id),
    session_id          UUID REFERENCES checkin_sessions(id),
    symptom_text        TEXT NOT NULL,          -- patient's original description
    meddra_pt_code      VARCHAR(20),            -- MedDRA Preferred Term code
    meddra_pt_term      VARCHAR(255),           -- MedDRA Preferred Term text
    meddra_soc          VARCHAR(255),           -- System Organ Class
    severity_grade      INT,                    -- CTCAE v5 grade: 1-5
    onset_date          DATE,
    is_ongoing          BOOLEAN DEFAULT true,
    resolution_date     DATE,
    relationship        VARCHAR(30),            -- 'unrelated', 'unlikely', 'possible', 'probable', 'definite'
    action_taken        VARCHAR(50),            -- 'none', 'dose_reduced', 'drug_interrupted', 'drug_discontinued'
    ai_confidence       FLOAT,                  -- 0.0-1.0 confidence in classification
    crc_reviewed        BOOLEAN NOT NULL DEFAULT false,
    crc_reviewed_at     TIMESTAMPTZ,
    crc_reviewed_by     UUID REFERENCES staff(id),
    crc_override_term   VARCHAR(255),           -- if CRC disagrees with AI classification
    crc_override_grade  INT,
    is_sae              BOOLEAN NOT NULL DEFAULT false,  -- serious adverse event flag
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- WEARABLE DATA (stored in PostgreSQL for hackathon simplicity)
-- =============================================================

CREATE TABLE wearable_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id),
    platform        VARCHAR(20) NOT NULL,  -- 'apple_healthkit', 'google_health_connect', 'fitbit'
    device_name     VARCHAR(255),
    device_model    VARCHAR(255),
    last_sync_at    TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE wearable_readings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id),
    metric          VARCHAR(50) NOT NULL,   -- 'heart_rate', 'resting_heart_rate', 'steps', 'sleep_minutes', 'spo2'
    value           FLOAT NOT NULL,
    source          VARCHAR(50),            -- 'apple_watch', 'fitbit', 'garmin', 'mock'
    quality         VARCHAR(20) DEFAULT 'raw',  -- 'raw', 'hourly_avg', 'daily_avg'
    recorded_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_wearable_readings_patient_metric ON wearable_readings(patient_id, metric, recorded_at DESC);

CREATE TABLE wearable_baselines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id),
    metric          VARCHAR(50) NOT NULL,  -- 'resting_heart_rate', 'steps_daily', 'sleep_hours', 'spo2'
    baseline_mean   FLOAT NOT NULL,
    baseline_stddev FLOAT NOT NULL,
    baseline_min    FLOAT,
    baseline_max    FLOAT,
    sample_count    INT NOT NULL,
    baseline_start  DATE NOT NULL,
    baseline_end    DATE NOT NULL,
    is_current      BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(patient_id, metric, is_current) -- only one active baseline per metric
);

CREATE TABLE wearable_anomalies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id),
    metric          VARCHAR(50) NOT NULL,
    anomaly_type    VARCHAR(30) NOT NULL,  -- 'point_anomaly', 'trend_anomaly', 'threshold_breach'
    detected_at     TIMESTAMPTZ NOT NULL,
    value           FLOAT NOT NULL,
    baseline_mean   FLOAT NOT NULL,
    z_score         FLOAT,
    trend_slope     FLOAT,    -- for trend anomalies: rate of change per day
    trend_window    INT,      -- days in the trend window
    severity        VARCHAR(10) NOT NULL,  -- 'low', 'medium', 'high'
    resolved        BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- ALERTS AND RISK SCORES
-- =============================================================

CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id),
    alert_type      VARCHAR(30) NOT NULL,
    -- 'symptom_severe', 'symptom_new', 'wearable_anomaly', 'missed_checkin',
    -- 'engagement_decline', 'risk_score_elevated', 'sae_reported'
    severity        VARCHAR(10) NOT NULL,  -- 'low', 'medium', 'high', 'critical'
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    source_type     VARCHAR(30),  -- 'symptom_entry', 'wearable_anomaly', 'system'
    source_id       UUID,         -- reference to the triggering record
    status          VARCHAR(20) NOT NULL DEFAULT 'open',
    -- 'open', 'acknowledged', 'in_progress', 'resolved', 'dismissed'
    assigned_to     UUID REFERENCES staff(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_scores (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id              UUID NOT NULL REFERENCES patients(id),
    score                   INT NOT NULL,  -- 0-100
    tier                    VARCHAR(10) NOT NULL,  -- 'low', 'medium', 'high'
    symptom_component       FLOAT NOT NULL,  -- 0-40
    wearable_component      FLOAT NOT NULL,  -- 0-30
    engagement_component    FLOAT NOT NULL,  -- 0-15
    compliance_component    FLOAT NOT NULL,  -- 0-15
    contributing_factors    JSONB NOT NULL DEFAULT '[]',
    -- [{"factor": "Grade 3 headache reported", "weight": 15}, ...]
    calculated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risk_scores_patient_date ON risk_scores(patient_id, calculated_at DESC);
CREATE INDEX idx_alerts_patient_status ON alerts(patient_id, status);
CREATE INDEX idx_symptom_entries_patient ON symptom_entries(patient_id, created_at DESC);
CREATE INDEX idx_checkin_sessions_patient ON checkin_sessions(patient_id, started_at DESC);
```

---

## 5. Component 1: AI Symptom Journal

### 5.1 Conversational Flow Architecture (LangGraph State Machine)

The AI symptom journal uses a **LangGraph** state machine that orchestrates the check-in conversation. Each check-in session progresses through defined graph nodes, with the LLM generating natural conversational text at each step. The graph is vendor-agnostic — the underlying LLM can be swapped via LangChain's provider abstraction.

```
┌───────────┐     ┌───────────────┐     ┌────────────────┐
│  GREETING │────▶│ OVERALL       │────▶│ SYMPTOM        │
│           │     │ FEELING       │     │ SCREENING      │
└───────────┘     │ (1-5 scale)   │     │ (open-ended    │
                  └───────────────┘     │  question)     │
                                        └───────┬────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                                    ▼                       ▼
                          ┌──────────────┐        ┌──────────────┐
                          │ NO SYMPTOMS  │        │ SYMPTOM      │
                          │ (brief       │        │ DEEP DIVE    │
                          │  closing)    │        │ (per symptom)│
                          └──────────────┘        └──────┬───────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │ For each     │
                                                  │ symptom:     │
                                                  │              │
                                                  │ 1. Severity  │
                                                  │ 2. Onset     │
                                                  │ 3. Duration  │
                                                  │ 4. Character │
                                                  │ 5. Treatment │
                                                  │ 6. Impact on │
                                                  │    daily life│
                                                  └──────┬───────┘
                                                         │
                                    ┌────────────────────┤
                                    ▼                    ▼
                          ┌──────────────┐     ┌──────────────┐
                          │ MORE         │     │ PROTOCOL-    │
                          │ SYMPTOMS?    │────▶│ SPECIFIC Qs  │
                          │ (loop back)  │     │ (from config)│
                          └──────────────┘     └──────┬───────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ SUMMARY &    │
                                               │ CONFIRMATION │
                                               └──────┬───────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ CLOSING &    │
                                               │ NEXT STEPS   │
                                               └──────────────┘
```

**LangGraph Implementation:**

```python
# app/ai/graphs/checkin_graph.py
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Literal
from app.ai.chains.conversation import get_checkin_chain


class CheckinState(BaseModel):
    """State tracked across the check-in conversation."""
    messages: list = Field(default_factory=list)
    phase: str = "greeting"
    overall_feeling: int | None = None
    reported_symptoms: list = Field(default_factory=list)
    current_symptom_index: int = 0
    symptom_detail_step: int = 0
    protocol_context: dict = Field(default_factory=dict)
    session_complete: bool = False


async def greeting_node(state: CheckinState) -> dict:
    chain = get_checkin_chain(state.protocol_context)
    response = await chain.ainvoke({
        "phase": "greeting",
        "messages": state.messages,
        "protocol": state.protocol_context,
    })
    return {
        "messages": state.messages + [AIMessage(content=response.content)],
        "phase": "overall_feeling",
    }


async def symptom_screening_node(state: CheckinState) -> dict:
    chain = get_checkin_chain(state.protocol_context)
    response = await chain.ainvoke({
        "phase": "symptom_screening",
        "messages": state.messages,
        "protocol": state.protocol_context,
    })
    return {
        "messages": state.messages + [AIMessage(content=response.content)],
        "phase": "awaiting_symptoms",
    }


def route_after_screening(state: CheckinState) -> Literal["deep_dive", "closing"]:
    """Determine if patient reported symptoms or not."""
    if state.reported_symptoms:
        return "deep_dive"
    return "closing"


# Build the graph
def build_checkin_graph():
    graph = StateGraph(CheckinState)

    graph.add_node("greeting", greeting_node)
    graph.add_node("overall_feeling", overall_feeling_node)
    graph.add_node("symptom_screening", symptom_screening_node)
    graph.add_node("deep_dive", symptom_deep_dive_node)
    graph.add_node("protocol_questions", protocol_questions_node)
    graph.add_node("summary", summary_node)
    graph.add_node("closing", closing_node)

    graph.set_entry_point("greeting")
    graph.add_edge("greeting", "overall_feeling")
    graph.add_edge("overall_feeling", "symptom_screening")
    graph.add_conditional_edges("symptom_screening", route_after_screening)
    graph.add_edge("deep_dive", "protocol_questions")
    graph.add_edge("protocol_questions", "summary")
    graph.add_edge("summary", "closing")
    graph.add_edge("closing", END)

    return graph.compile()
```

### 5.2 LangChain LLM Orchestration (Vendor-Agnostic)

All LLM calls go through LangChain's abstraction layer, ensuring no vendor lock-in. The provider is configured via environment variable.

```python
# app/ai/chains/conversation.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from app.ai.llm import get_llm


def get_checkin_chain(protocol_context: dict):
    """Build the check-in conversation chain using LangChain."""
    llm = get_llm()  # vendor-agnostic LLM

    system_prompt = """You are a compassionate clinical trial health assistant for a patient
enrolled in a {therapeutic_area} trial (Protocol: {protocol_number}).

YOUR ROLE:
- Guide the patient through a daily symptom check-in
- Ask clear, warm questions in plain language (no medical jargon)
- Collect enough detail to classify symptoms using MedDRA terminology
- Never provide medical advice, diagnoses, or treatment recommendations
- If the patient reports something concerning, acknowledge it warmly and
  let them know their clinical team will be notified

EXPECTED SIDE EFFECTS FOR THIS PROTOCOL:
{expected_side_effects}

SYMPTOM ASSESSMENT CHECKLIST (collect for each reported symptom):
1. What the symptom feels like (description in patient's own words)
2. When it started (onset)
3. How bad it is on a scale of 1-10
4. Whether it's constant or comes and goes
5. Whether they took anything for it
6. Whether it affects their daily activities

RESPONSE FORMAT:
- Keep messages short (2-3 sentences max)
- Use one question per message
- Offer quick-reply options where appropriate
- End each check-in with a brief summary of what was reported

SAFETY ESCALATION:
If the patient reports any of the following, immediately flag as HIGH PRIORITY:
- Chest pain, difficulty breathing, severe allergic reaction
- Suicidal thoughts or severe depression
- Seizures, loss of consciousness
- Any symptom rated 9-10 severity

Current phase: {phase}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("messages"),
    ])

    return prompt | llm


# app/ai/llm.py
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm():
    """Return a LangChain LLM instance based on configuration.
    Swap providers by changing LLM_PROVIDER env var — no code changes needed.
    """
    if settings.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            max_tokens=1024,
        )
    elif settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            max_tokens=1024,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
```

### 5.3 Symptom Classification Pipeline (LangGraph)

When a check-in session completes, the full conversation is sent to a classification LangGraph that extracts and classifies symptoms:

```python
# app/ai/graphs/classifier_graph.py
from langgraph.graph import StateGraph, END
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.ai.llm import get_llm


class SymptomClassification(BaseModel):
    symptom_text: str
    meddra_pt: str
    meddra_code: str
    severity_ctcae: int = Field(ge=1, le=5)
    onset: str | None = None
    ongoing: bool = True
    confidence: float = Field(ge=0.0, le=1.0)


class ClassifierState(BaseModel):
    conversation_history: list = Field(default_factory=list)
    protocol_context: dict = Field(default_factory=dict)
    extracted_symptoms: list = Field(default_factory=list)
    classifications: list = Field(default_factory=list)
    is_validated: bool = False


async def extract_symptoms_node(state: ClassifierState) -> dict:
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=list[SymptomClassification])

    prompt = f"""Analyze this check-in conversation and extract every symptom
the patient reported. For each symptom, classify it with a MedDRA Preferred Term,
CTCAE v5 severity grade, and your confidence score.

Conversation:
{state.conversation_history}

Protocol context (expected side effects):
{state.protocol_context.get('expected_side_effects', [])}

{parser.get_format_instructions()}"""

    response = await llm.ainvoke(prompt)
    classifications = parser.parse(response.content)
    return {"classifications": classifications}


async def validate_node(state: ClassifierState) -> dict:
    """Validate classifications against known MedDRA codes."""
    validated = []
    for c in state.classifications:
        # Validate MedDRA code exists, severity is within range, etc.
        if 1 <= c.get("severity_ctcae", 0) <= 5 and c.get("confidence", 0) > 0.5:
            validated.append(c)
    return {"classifications": validated, "is_validated": True}


def build_classifier_graph():
    graph = StateGraph(ClassifierState)
    graph.add_node("extract", extract_symptoms_node)
    graph.add_node("validate", validate_node)
    graph.set_entry_point("extract")
    graph.add_edge("extract", "validate")
    graph.add_edge("validate", END)
    return graph.compile()
```

### 5.4 Real-Time Voice Check-In (LiveKit)

Patients can choose to complete their check-in via voice instead of text. The voice pipeline uses a self-hosted LiveKit server with the LiveKit Agents SDK running inside the Python monolith.

**Architecture:**

```
┌─────────────────────┐       ┌──────────────────────┐
│  React Native App   │       │  LiveKit Server      │
│                     │ WebRTC│  (Docker, self-hosted)│
│  ┌───────────────┐  │◄─────▶│                      │
│  │ LiveKit RN    │  │       │  Manages rooms,      │
│  │ SDK           │  │       │  routes media         │
│  │               │  │       └──────────┬───────────┘
│  │ Mic → Publish │  │                  │
│  │ Subscribe ← ▸ │  │                  │ Agent connects
│  └───────────────┘  │                  │ as participant
│                     │                  ▼
│  ┌───────────────┐  │       ┌──────────────────────┐
│  │ Text Chat     │  │       │  Python Backend      │
│  │ (parallel)    │  │       │  (LiveKit Agent)     │
│  └───────────────┘  │       │                      │
│                     │       │  Audio In ──▶ STT    │
└─────────────────────┘       │     (Deepgram/       │
                              │      Whisper)         │
                              │       │               │
                              │       ▼               │
                              │  Transcript ──▶       │
                              │  LangGraph Check-In   │
                              │  Agent (same graph    │
                              │  as text check-in)    │
                              │       │               │
                              │       ▼               │
                              │  Response Text ──▶    │
                              │  TTS (Coqui /         │
                              │  ElevenLabs)          │
                              │       │               │
                              │       ▼               │
                              │  Audio Out ──▶        │
                              │  Publish to room      │
                              └──────────────────────┘
```

**LiveKit Agent Implementation:**

```python
# app/modules/voice/agent.py
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm as livekit_llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, silero
from app.ai.graphs.checkin_graph import build_checkin_graph, CheckinState
from app.ai.llm import get_llm


class TrialPulseVoiceAgent:
    """LiveKit voice agent that runs the same LangGraph check-in flow
    used by the text chat, but with voice input/output."""

    def __init__(self, protocol_context: dict, patient_id: str):
        self.protocol_context = protocol_context
        self.patient_id = patient_id
        self.checkin_graph = build_checkin_graph()
        self.state = CheckinState(protocol_context=protocol_context)

    async def handle_transcript(self, transcript: str) -> str:
        """Process a speech transcript through the LangGraph check-in flow."""
        from langchain_core.messages import HumanMessage

        self.state.messages.append(HumanMessage(content=transcript))
        result = await self.checkin_graph.ainvoke(self.state)
        self.state = CheckinState(**result)

        # Return the latest AI message for TTS
        ai_messages = [m for m in self.state.messages if hasattr(m, 'type') and m.type == 'ai']
        return ai_messages[-1].content if ai_messages else "I'm here to help."


async def entrypoint(ctx: JobContext):
    """LiveKit agent entrypoint — called when a patient joins a voice room."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Extract patient/protocol info from room metadata
    room_metadata = ctx.room.metadata  # JSON with patient_id, protocol_context
    import json
    meta = json.loads(room_metadata) if room_metadata else {}

    agent = TrialPulseVoiceAgent(
        protocol_context=meta.get("protocol_context", {}),
        patient_id=meta.get("patient_id", ""),
    )

    # Configure STT + TTS
    stt = deepgram.STT()
    tts = deepgram.TTS()  # or use Coqui for fully local TTS
    vad = silero.VAD.load()

    assistant = VoiceAssistant(
        vad=vad,
        stt=stt,
        llm=get_llm(),  # LangChain LLM for fallback
        tts=tts,
        chat_ctx=livekit_llm.ChatContext(),
    )
    assistant.start(ctx.room)


# To run as a worker alongside FastAPI:
# Worker is started as an asyncio task during app lifespan
```

**React Native Voice UI:**

```
┌──────────────────────────────┐
│  Voice Check-In              │
│                              │
│  ┌────────────────────────┐  │
│  │    [TrialPulse Avatar] │  │
│  │                        │  │
│  │  "Hi! How are you      │  │
│  │   feeling today?"      │  │
│  │                        │  │
│  │    🔊 Speaking...       │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  📝 Live Transcript:   │  │
│  │  "I've had a headache  │  │
│  │   since yesterday..."  │  │
│  └────────────────────────┘  │
│                              │
│       ┌──────────────┐       │
│       │  🎙️ Listening │       │
│       │  (tap to mute)│       │
│       └──────────────┘       │
│                              │
│  [Switch to Text Chat]       │
└──────────────────────────────┘
```

### 5.5 Mobile App Screen Specifications

#### Screen: Home

- **Top section**: Greeting with patient's first name and current date
- **Status card**: Shows check-in status for today (completed/pending/overdue) with a countdown timer to the check-in window closing
- **Quick action buttons**: Two CTAs — "Start Text Check-In" and "Start Voice Check-In"
- **Health summary strip**: Mini cards showing latest wearable metrics (heart rate, steps, sleep) pulled from the last sync
- **Timeline preview**: Last 3 symptom entries with dates and severity indicators
- **Bottom nav**: Home, Timeline, Wearable, Profile

#### Screen: Chat (Text Check-In)

- **Header**: "Daily Check-In" with session timer and a minimize button
- **Message list**: Scrollable chat bubbles; AI messages on the left (with TrialPulse avatar), patient messages on the right
- **Quick reply bar**: When the AI offers quick replies, they appear as tappable chips above the text input (e.g., "No new symptoms", "Same as yesterday", "Yes", "No")
- **Scale widget**: When severity is requested, a horizontal slider (1-10) replaces the text input temporarily
- **Date picker**: When onset is requested, a date picker appears inline
- **Text input**: Standard text input with send button; microphone icon to switch to voice mode
- **Progress indicator**: Subtle dots at the top showing approximate session progress

#### Screen: Voice Check-In

- **Header**: "Voice Check-In" with session timer and close button
- **Agent avatar**: Animated TrialPulse avatar that pulses/glows when the AI is speaking
- **Live transcript panel**: Scrolling transcript of both patient speech and AI responses, providing a visual record of the voice conversation
- **Voice activity indicator**: Visual feedback showing when the patient's mic is active vs when the AI is speaking
- **Control bar**: Mute/unmute toggle, "Switch to Text" button, end session button
- **Quick reply chips**: Still available for structured inputs (severity rating, yes/no) even during voice mode — tappable as an alternative to speaking

#### Screen: Health Timeline

- **Vertical timeline**: Chronological list of all events: symptom reports, wearable anomaly flags, scheduled visits, and medications
- **Each event card** shows: date/time, event type icon, brief description, severity color indicator
- **Filter chips** at top: "All", "Symptoms", "Wearable Alerts", "Visits"
- **Tap to expand**: Tapping a symptom entry shows full details including AI classification and CRC review status

#### Screen: Wearable Dashboard

- **Connection status**: Card showing connected device name, last sync time, battery level (if available)
- **Metric cards** (one per tracked metric):
  - Current value with trend arrow (↑↓→)
  - Sparkline showing last 7 days
  - Baseline range indicator (green band = normal range)
- **Anomaly alerts**: If any metrics are flagged, a yellow/red banner appears at the top with a brief explanation

#### Screen: Profile & Settings

- **Trial info**: Protocol number, site name, enrollment date, treatment arm (if unblinded)
- **Notification preferences**: Toggle and time-of-day preference for check-in reminders
- **Wearable management**: Connect/disconnect devices
- **Language preference**: Dropdown for supported languages
- **Support**: Contact info for their CRC and a general help link

---

## 6. Component 2: Wearable Health Integration

### 6.1 Supported Platforms and Metrics

```
┌──────────────────┬──────────────────────────────────────────────────┐
│ Platform         │ Integration Method                              │
├──────────────────┼──────────────────────────────────────────────────┤
│ Apple HealthKit  │ Native iOS API via react-native-health          │
│                  │ Reads: HKQuantityType for HR, steps, SpO2,     │
│                  │   sleep, HRV, respiratory rate                  │
│                  │ Background delivery: enabled for real-time HR   │
│                  │                                                  │
│ Google Health    │ Android Health Connect API via                   │
│ Connect          │   react-native-health-connect                   │
│                  │ Reads: HeartRateRecord, StepsRecord,            │
│                  │   SleepSessionRecord, OxygenSaturationRecord    │
│                  │                                                  │
│ Mock Data        │ Pre-generated seed data for hackathon demo      │
│ (Hackathon)      │ 30-day history per patient with baked-in        │
│                  │ anomaly patterns                                │
└──────────────────┴──────────────────────────────────────────────────┘
```

### 6.2 Data Ingestion Pipeline

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Wearable    │     │ Phone Health     │     │ TrialPulse       │
│ Device      │────▶│ Platform         │────▶│ Mobile App       │
│ (Watch)     │ BLE │ (HealthKit /     │ API │                  │
│             │     │  Health Connect) │     │ Reads metrics    │
└─────────────┘     └──────────────────┘     │ every 15 min     │
                                              │ (configurable)   │
                                              └────────┬─────────┘
                                                       │
                                                  HTTPS POST
                                                  (batch upload)
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Wearable Module  │
                                              │ (FastAPI)        │
                                              │                  │
                                              │ 1. Validate &    │
                                              │    normalize     │
                                              │ 2. Write to      │
                                              │    PostgreSQL    │
                                              │ 3. Publish event │
                                              │    (Redis)       │
                                              └────────┬─────────┘
                                                       │
                                              event: "wearable
                                               .data_received"
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Anomaly          │
                                              │ Detection        │
                                              │ (in-process)     │
                                              │                  │
                                              │ 1. Load baseline │
                                              │ 2. Compare       │
                                              │ 3. Flag if       │
                                              │    anomalous     │
                                              └──────────────────┘
```

### 6.3 Data Normalization

```python
# app/modules/wearable/normalization.py

NORMALIZATION_RULES = {
    "heart_rate": {
        "unit": "bpm",
        "valid_range": (30, 250),
        "precision": 0,
    },
    "resting_heart_rate": {
        "unit": "bpm",
        "valid_range": (30, 150),
        "precision": 0,
    },
    "steps": {
        "unit": "count",
        "valid_range": (0, 100_000),
        "precision": 0,
        "aggregation": "sum",
    },
    "sleep_minutes": {
        "unit": "minutes",
        "valid_range": (0, 1440),
        "precision": 0,
    },
    "spo2": {
        "unit": "percent",
        "valid_range": (70, 100),
        "precision": 1,
    },
    "hrv": {
        "unit": "ms",
        "valid_range": (5, 300),
        "precision": 1,
    },
}


async def normalize_reading(metric: str, value: float) -> float | None:
    """Validate and normalize a single wearable reading. Returns None if invalid."""
    rules = NORMALIZATION_RULES.get(metric)
    if not rules:
        return None
    low, high = rules["valid_range"]
    if not (low <= value <= high):
        return None
    return round(value, rules["precision"])
```

### 6.4 Anomaly Detection Algorithms

#### Point Anomaly Detection (Z-Score)

```python
# app/modules/wearable/anomaly_detection.py
import numpy as np


async def detect_point_anomaly(
    value: float,
    baseline_mean: float,
    baseline_stddev: float,
    z_threshold: float = 2.5,
) -> dict | None:
    """
    Flag a single data point as anomalous if it deviates significantly
    from the patient's personal baseline.
    """
    if baseline_stddev == 0:
        return None

    z_score = abs(value - baseline_mean) / baseline_stddev

    if z_score >= z_threshold:
        severity = "low" if z_score < 3.0 else ("medium" if z_score < 4.0 else "high")
        direction = "elevated" if value > baseline_mean else "depressed"
        return {
            "anomaly_type": "point_anomaly",
            "z_score": round(z_score, 2),
            "value": value,
            "baseline_mean": baseline_mean,
            "direction": direction,
            "severity": severity,
        }
    return None
```

#### Trend Detection (Sliding Window Linear Regression)

```python
async def detect_trend_anomaly(
    daily_values: list[tuple],
    window_days: int = 14,
    min_slope_per_day: float = 0.5,
) -> dict | None:
    """
    Detect gradual trends that wouldn't trigger point anomalies.
    Example: resting heart rate increasing by 0.4 BPM/day over 14 days
    = +5.6 BPM total, which is clinically meaningful.
    """
    if len(daily_values) < window_days:
        return None

    recent = daily_values[-window_days:]
    x = np.arange(len(recent))
    y = np.array([v for _, v in recent])

    slope, intercept = np.polyfit(x, y, 1)

    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    if abs(slope) >= min_slope_per_day and r_squared >= 0.5:
        direction = "increasing" if slope > 0 else "decreasing"
        total_change = slope * window_days
        severity = "low" if abs(total_change) < 5 else (
            "medium" if abs(total_change) < 10 else "high"
        )
        return {
            "anomaly_type": "trend_anomaly",
            "slope_per_day": round(slope, 3),
            "total_change": round(total_change, 2),
            "r_squared": round(r_squared, 3),
            "window_days": window_days,
            "direction": direction,
            "severity": severity,
        }
    return None
```

#### Contextual Filtering

```python
async def should_suppress_anomaly(anomaly: dict, patient_context: dict) -> bool:
    """Reduce false positives by checking if there's a reasonable explanation."""
    metric = anomaly["metric"]
    detected_at = anomaly["detected_at"]

    if metric == "heart_rate" and anomaly.get("direction") == "elevated":
        recent_activities = patient_context.get("reported_activities", [])
        for activity in recent_activities:
            if abs((detected_at - activity["timestamp"]).total_seconds()) < 7200:
                if activity["type"] in ("exercise", "physical_activity", "walking"):
                    return True

    if metric == "sleep_minutes":
        if patient_context.get("recent_travel", False):
            return True

    if metric == "steps" and anomaly.get("direction") == "depressed":
        if patient_context.get("visit_today", False):
            return True

    return False
```

### 6.5 Baseline Calculation

```python
async def calculate_baseline(
    patient_id: str,
    metric: str,
    readings: list[dict],
    min_days: int = 7,
    max_days: int = 14,
) -> dict | None:
    """
    Establish a personalized baseline from the patient's initial enrollment period.
    """
    if len(readings) < min_days:
        return None

    recent = readings[-max_days:]
    values = np.array([r["value"] for r in recent])

    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    filtered = values[(values >= lower_bound) & (values <= upper_bound)]

    return {
        "patient_id": patient_id,
        "metric": metric,
        "baseline_mean": round(float(np.mean(filtered)), 2),
        "baseline_stddev": round(float(np.std(filtered)), 2),
        "baseline_min": round(float(np.min(filtered)), 2),
        "baseline_max": round(float(np.max(filtered)), 2),
        "sample_count": len(filtered),
        "baseline_start": recent[0]["date"],
        "baseline_end": recent[-1]["date"],
    }
```

---

## 7. Component 3: Researcher Safety Dashboard

### 7.1 Dashboard Pages and Layouts

#### Page: Patient List (Default View)

```
┌─────────────────────────────────────────────────────────────────┐
│  TrialPulse    [Trial: ABC-123 ▼]    [Site: All ▼]    🔔 3  👤 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Active Alerts: 3 critical, 7 medium    Overdue Check-ins: 5   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Search patients...          [Risk ▼] [Arm ▼] [Status ▼]│   │
│  ├─────┬──────────┬─────┬──────────┬──────────┬───────────┤   │
│  │Risk │ Subject  │ Arm │ Last     │ Open     │ Latest    │   │
│  │Score│ ID       │     │ Check-In │ Alerts   │ Symptom   │   │
│  ├─────┼──────────┼─────┼──────────┼──────────┼───────────┤   │
│  │ 🔴  │ 001-0042 │  A  │ 2h ago   │ 2 (1 🔴) │ Nausea G3 │   │
│  │ 82  │          │     │          │          │           │   │
│  ├─────┼──────────┼─────┼──────────┼──────────┼───────────┤   │
│  │ 🟡  │ 001-0017 │  B  │ 18h ago  │ 1 (🟡)   │ Fatigue G2│   │
│  │ 55  │          │     │          │          │           │   │
│  ├─────┼──────────┼─────┼──────────┼──────────┼───────────┤   │
│  │ 🟢  │ 001-0089 │  A  │ 4h ago   │ 0        │ None      │   │
│  │ 12  │          │     │          │          │           │   │
│  └─────┴──────────┴─────┴──────────┴──────────┴───────────┘   │
│                                                                 │
│  Showing 1-25 of 142 patients              [◀ 1 2 3 4 5 6 ▶]  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Page: Patient Detail

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back    Patient 001-0042    Arm A    Enrolled: 2026-01-15   │
│            Risk Score: 82 🔴    [Message Patient] [Export]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── Tabs ─────────────────────────────────────────────────┐  │
│  │ [Timeline]  [Symptoms]  [Wearables]  [Alerts]  [Notes]  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  === TIMELINE VIEW ===                                          │
│                                                                 │
│  Mar 28 ─── 🔴 Alert: Resting HR elevated (88 bpm, baseline   │
│  10:30am     72±5). Z-score: 3.2                               │
│              [Acknowledge] [Dismiss] [Escalate]                 │
│                                                                 │
│  Mar 28 ─── 💬 Check-in completed (voice)                      │
│  08:15am     Reported: Nausea (Grade 3), Headache (Grade 2)   │
│              AI confidence: 0.94, 0.91                         │
│              [Review & Confirm] [Edit Classification]          │
│                                                                 │
│  Mar 27 ─── ⌚ Wearable sync                                   │
│  11:00pm     HR avg: 82 bpm (↑12% vs baseline)                │
│              Sleep: 5.2 hrs (↓22% vs baseline)                 │
│              Steps: 3,200 (↓45% vs baseline)                   │
│                                                                 │
│  Mar 27 ─── 💬 Check-in completed (text)                       │
│  08:00am     Reported: Nausea (Grade 2), Fatigue (Grade 1)    │
│              ✅ CRC reviewed by J. Smith                       │
│                                                                 │
│  ═══════════════════════════════════════════════════════════    │
│                                                                 │
│  === WEARABLE CHARTS (visible in Wearables tab) ===            │
│                                                                 │
│  Resting Heart Rate (14-day trend)                             │
│  bpm                                                            │
│  90 ┤                                           ●──●           │
│  85 ┤                                    ●──●──●               │
│  80 ┤                              ●──●──●                     │
│  75 ┤               ●──●──●──●──●──●          ← baseline band │
│  70 ┤    ●──●──●──●──●                                         │
│  65 ┤                                                           │
│     └──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──             │
│       14  13  12  11  10  9   8   7   6   5   4   3   2   1    │
│                          Days Ago                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Page: Cohort Analytics

```
┌─────────────────────────────────────────────────────────────────┐
│  Cohort Analytics    [Trial: ABC-123 ▼]    Date Range: [════]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌── Summary Cards ──────────────────────────────────────────┐ │
│  │ Enrolled: 142 │ Active: 128 │ Withdrawn: 8 │ Completed: 6│ │
│  │ Avg Risk: 34  │ High Risk: 12 (8.5%)                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌── AE Incidence by Treatment Arm ─────────────────────────┐ │
│  │                                                           │ │
│  │  Symptom        │ Arm A (n=71) │ Arm B (n=71) │ p-value  │ │
│  │  ───────────────┼──────────────┼──────────────┼───────── │ │
│  │  Nausea         │ 42% (30)     │ 18% (13)     │ 0.003*  │ │
│  │  Headache       │ 31% (22)     │ 28% (20)     │ 0.72    │ │
│  │  Fatigue        │ 55% (39)     │ 48% (34)     │ 0.41    │ │
│  │  Rash           │ 8% (6)       │ 4% (3)       │ 0.31    │ │
│  │                                                           │ │
│  │  * statistically significant (Fisher's exact test)        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌── Wearable Metric Distributions ─────────────────────────┐ │
│  │  [Box plots comparing Arm A vs Arm B for each metric]    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌── Engagement Over Time ──────────────────────────────────┐ │
│  │  [Line chart: check-in compliance % by week, per arm]    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Page: Alert Queue

```
┌─────────────────────────────────────────────────────────────────┐
│  Alert Queue    Open: 10    Acknowledged: 5    Today: 3         │
│  [Critical Only] [Medium+] [All]    [My Alerts ▼]              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔴 CRITICAL │ 001-0042 │ 10:30 AM today                       │
│  Resting heart rate elevated to 88 bpm (baseline: 72±5 bpm).  │
│  Z-score: 3.2. Trend: +2.3 bpm/day over 7 days.               │
│  Patient also reported Grade 3 nausea this morning.            │
│  [Acknowledge] [Contact Patient] [Escalate to PI] [Dismiss]   │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🟡 MEDIUM │ 001-0017 │ Yesterday 6:15 PM                      │
│  Missed scheduled check-in (2nd consecutive).                  │
│  Last completed check-in: 48 hours ago.                        │
│  Last wearable sync: 12 hours ago (device still active).       │
│  [Acknowledge] [Contact Patient] [Dismiss]                     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🟡 MEDIUM │ 001-0091 │ Yesterday 2:00 PM                      │
│  SpO2 dropped to 91% (baseline: 97±1%). Single reading.        │
│  No symptoms reported. Wearable data quality: good.            │
│  [Acknowledge] [Monitor] [Contact Patient] [Dismiss]           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Real-Time Updates via WebSocket

The dashboard maintains a persistent WebSocket connection via native FastAPI WebSockets for live updates.

```python
# app/ws/manager.py
import asyncio
import json
from fastapi import WebSocket
from typing import Dict, Set


class WebSocketManager:
    """Manages WebSocket connections for real-time dashboard updates."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}  # trial_id -> set of websockets

    async def connect(self, websocket: WebSocket, trial_id: str):
        await websocket.accept()
        if trial_id not in self._connections:
            self._connections[trial_id] = set()
        self._connections[trial_id].add(websocket)

    def disconnect(self, websocket: WebSocket, trial_id: str):
        if trial_id in self._connections:
            self._connections[trial_id].discard(websocket)

    async def broadcast(self, trial_id: str, event_type: str, payload: dict):
        """Broadcast an event to all dashboard clients watching a trial."""
        message = json.dumps({"type": event_type, "payload": payload})
        if trial_id in self._connections:
            dead = set()
            for ws in self._connections[trial_id]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.add(ws)
            self._connections[trial_id] -= dead


# Events that trigger real-time pushes:
WS_EVENTS = {
    "alert:new": "Add to alert queue, update patient list risk indicator, show toast notification",
    "checkin:completed": "Update patient list 'Last Check-In' column, refresh patient detail if open",
    "anomaly:detected": "Update patient wearable indicators, may trigger alert:new subsequently",
    "risk_score:updated": "Update patient list sorting, animate score change",
    "alert:updated": "Update alert queue to prevent duplicate work",
}
```

### 7.3 CRC Workflow: Symptom Review

When a patient reports symptoms via the AI journal (text or voice), the CRC must review the AI's classification:

```
AI classifies symptom ──▶ Stored with crc_reviewed = false
                                    │
                                    ▼
                          Dashboard shows yellow
                          "Pending Review" badge
                          on patient row
                                    │
                                    ▼
                          CRC opens Patient Detail
                          ──▶ Symptoms tab
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Review Panel                 │
                    │                               │
                    │  Patient said: "I've had a    │
                    │  really bad headache behind    │
                    │  my eyes for two days"         │
                    │  (via: voice check-in)         │
                    │                               │
                    │  AI Classification:            │
                    │    Term: Headache (10019211)   │
                    │    Grade: 2 (Moderate)         │
                    │    Confidence: 94%             │
                    │                               │
                    │  [✅ Confirm]  [✏️ Override]    │
                    │                               │
                    │  Override options:             │
                    │    Term: [searchable MedDRA    │
                    │      dropdown]                │
                    │    Severity: [1] [2] [3] [4]  │
                    │    Onset: [date picker]        │
                    │    Notes: [free text]          │
                    │                               │
                    └───────────────────────────────┘
                                    │
                                    ▼
                          crc_reviewed = true
                          crc_reviewed_at = NOW()
                          crc_reviewed_by = staff_id
                          (crc_override fields if edited)
```

---

## 8. AI/ML Pipeline

### 8.1 Model Architecture (LangChain + LangGraph)

```
┌─────────────────────────────────────────────────────────────────┐
│           AI/ML LAYER (LangChain + LangGraph)                   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         LangChain Provider Abstraction                   │    │
│  │                                                         │    │
│  │  Configured via env: LLM_PROVIDER / LLM_MODEL           │    │
│  │  Supported: Anthropic, OpenAI, local (Ollama)           │    │
│  │  Zero code changes to switch providers                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐      │
│  │          Check-In Conversation Agent (LangGraph)       │      │
│  │                                                       │      │
│  │  Stateful multi-step graph:                           │      │
│  │    greeting → feeling → screening → deep dive →       │      │
│  │    protocol Qs → summary → closing                    │      │
│  │                                                       │      │
│  │  Same graph serves both text and voice modalities     │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐      │
│  │          Symptom Classifier (LangGraph)                │      │
│  │                                                       │      │
│  │  Input: Full check-in conversation + protocol context │      │
│  │  Steps: extract → classify → validate                 │      │
│  │  Output: JSON array of classified symptoms            │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐      │
│  │          Anomaly Detection Engine                      │      │
│  │                                                       │      │
│  │  Algorithms:                                          │      │
│  │    1. Z-score point anomaly detection                 │      │
│  │    2. Sliding-window linear regression trends         │      │
│  │    3. Contextual filtering (suppress false positives) │      │
│  │                                                       │      │
│  │  Libraries: numpy, scikit-learn, scipy                │      │
│  │  Runs: On every wearable data batch + scheduled cron  │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐      │
│  │          Risk Scoring Engine                           │      │
│  │                                                       │      │
│  │  Inputs:                                              │      │
│  │    - Latest symptom entries (severity, count, trend)  │      │
│  │    - Wearable anomaly flags (count, magnitude)        │      │
│  │    - Engagement metrics (check-in compliance, trends) │      │
│  │    - Protocol compliance (visit attendance, timing)   │      │
│  │                                                       │      │
│  │  Algorithm: Weighted composite score (0-100)          │      │
│  │  Runs: After every new data point + daily recalc      │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Risk Score Calculation

```python
# app/modules/alert/risk_scoring.py

async def calculate_risk_score(patient_id: str, lookback_days: int = 7) -> dict:
    """
    Calculate a composite risk score (0-100) for a patient.
    Called after every new symptom entry, wearable anomaly, or missed check-in.
    Also recalculated daily via APScheduler cron job.
    """

    # ─── COMPONENT 1: Symptom Score (0-40) ───
    recent_symptoms = await get_symptoms(patient_id, days=lookback_days)

    symptom_score = 0
    if recent_symptoms:
        max_severity = max(s["severity_grade"] for s in recent_symptoms)
        symptom_count = len(recent_symptoms)

        severity_map = {1: 3, 2: 8, 3: 15, 4: 22, 5: 25}
        symptom_score += severity_map.get(max_severity, 0)
        symptom_score += min(symptom_count * 2, 10)

        if await is_symptom_worsening(recent_symptoms):
            symptom_score += 5

    # ─── COMPONENT 2: Wearable Score (0-30) ───
    recent_anomalies = await get_anomalies(patient_id, days=lookback_days)

    wearable_score = 0
    if recent_anomalies:
        severity_weights = {"low": 3, "medium": 8, "high": 15}
        anomaly_sum = sum(severity_weights.get(a["severity"], 0) for a in recent_anomalies)
        wearable_score += min(anomaly_sum, 20)

        unique_metrics = len(set(a["metric"] for a in recent_anomalies))
        if unique_metrics >= 2:
            wearable_score += min(unique_metrics * 3, 10)

    # ─── COMPONENT 3: Engagement Score (0-15) ───
    checkin_compliance = await get_checkin_compliance(patient_id, days=lookback_days)

    engagement_score = 0
    if checkin_compliance < 0.5:
        engagement_score = 15
    elif checkin_compliance < 0.7:
        engagement_score = 10
    elif checkin_compliance < 0.85:
        engagement_score = 5

    consecutive_misses = await get_consecutive_missed_checkins(patient_id)
    if consecutive_misses >= 3:
        engagement_score = min(engagement_score + 5, 15)

    # ─── COMPONENT 4: Compliance Score (0-15) ───
    compliance_score = 0
    missed_visits = await get_missed_visits(patient_id, days=30)
    if missed_visits > 0:
        compliance_score += min(missed_visits * 5, 10)

    out_of_window = await get_out_of_window_submissions(patient_id, days=lookback_days)
    if out_of_window > 2:
        compliance_score += 5
    compliance_score = min(compliance_score, 15)

    # ─── COMPOSITE ───
    total_score = min(
        symptom_score + wearable_score + engagement_score + compliance_score, 100
    )
    tier = "low" if total_score <= 30 else ("medium" if total_score <= 70 else "high")

    return {
        "score": total_score,
        "tier": tier,
        "symptom_component": symptom_score,
        "wearable_component": wearable_score,
        "engagement_component": engagement_score,
        "compliance_component": compliance_score,
        "contributing_factors": await build_factor_list(
            recent_symptoms, recent_anomalies, checkin_compliance, missed_visits
        ),
    }
```

---

## 9. Alert Engine

### 9.1 Alert Rules

The Alert Engine evaluates incoming events against a configurable set of rules. It runs as an in-process subscriber to the Redis event bus.

```python
# app/modules/alert/rules.py

ALERT_RULES = [
    {
        "id": "severe_symptom",
        "trigger": "symptom.reported",
        "condition": lambda event: event["severity_grade"] >= 3,
        "severity": lambda event: "critical" if event["severity_grade"] >= 4 else "medium",
        "title": lambda event: f"Grade {event['severity_grade']} {event['meddra_pt_term']} reported",
        "description": lambda event: (
            f"Patient reported {event['meddra_pt_term']} "
            f"(Grade {event['severity_grade']}) during check-in. "
            f"Onset: {event.get('onset_date', 'not specified')}. "
            f"AI confidence: {event.get('ai_confidence', 'N/A')}"
        ),
    },
    {
        "id": "sae_keywords",
        "trigger": "symptom.reported",
        "condition": lambda event: any(
            kw in event.get("symptom_text", "").lower()
            for kw in ["chest pain", "can't breathe", "seizure", "passed out",
                        "allergic reaction", "swelling of face", "suicidal"]
        ),
        "severity": lambda _: "critical",
        "title": lambda _: "Potential serious adverse event detected",
        "description": lambda event: (
            f"Patient's symptom description contains SAE-suggestive keywords. "
            f"Original text: \"{event['symptom_text'][:200]}\". "
            f"Immediate clinical review recommended."
        ),
    },
    {
        "id": "wearable_anomaly",
        "trigger": "anomaly.detected",
        "condition": lambda event: event["severity"] in ("medium", "high"),
        "severity": lambda event: "high" if event["severity"] == "high" else "medium",
        "title": lambda event: (
            f"{event['metric'].replace('_', ' ').title()} "
            f"{'anomaly' if event['anomaly_type'] == 'point_anomaly' else 'trend'} detected"
        ),
        "description": lambda event: (
            f"{event['metric'].replace('_', ' ').title()} value: {event['value']} "
            f"(baseline: {event['baseline_mean']}±{event.get('baseline_stddev', '?')}). "
        ),
    },
    {
        "id": "missed_checkin",
        "trigger": "checkin.missed",
        "condition": lambda event: True,
        "severity": lambda event: "medium" if event.get("consecutive_misses", 1) >= 2 else "low",
        "title": lambda event: (
            f"Missed check-in"
            f"{' (' + str(event['consecutive_misses']) + ' consecutive)' if event.get('consecutive_misses', 1) > 1 else ''}"
        ),
        "description": lambda event: (
            f"Patient did not complete their scheduled check-in. "
            f"Last completed check-in: {event.get('last_checkin', 'unknown')}. "
            f"Last wearable sync: {event.get('last_sync', 'unknown')}."
        ),
    },
    {
        "id": "risk_score_elevated",
        "trigger": "risk_score.updated",
        "condition": lambda event: (
            event["new_tier"] == "high" and event.get("old_tier") != "high"
        ),
        "severity": lambda _: "high",
        "title": lambda _: "Patient risk score elevated to HIGH",
        "description": lambda event: (
            f"Risk score increased from {event.get('old_score', '?')} to {event['new_score']}. "
            f"Contributing factors: {', '.join(f['factor'] for f in event.get('contributing_factors', [])[:3])}."
        ),
    },
]
```

### 9.2 Alert Deduplication

```python
# app/modules/alert/deduplication.py
from sqlalchemy import select, and_
from datetime import datetime, timedelta


async def should_create_alert(
    db_session, rule_id: str, patient_id: str, new_alert: dict
) -> bool:
    """Check if we should create a new alert or suppress it as a duplicate."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    result = await db_session.execute(
        select(Alert).where(
            and_(
                Alert.patient_id == patient_id,
                Alert.alert_type == rule_id,
                Alert.status.in_(["open", "acknowledged"]),
                Alert.created_at > cutoff,
            )
        )
    )
    existing = result.scalars().first()

    if existing:
        await update_existing_alert(db_session, existing.id, new_alert)
        return False
    return True
```

---

## 10. Authentication & Authorization

> **Hackathon note:** For the prototype, authentication is bypassed using hardcoded demo accounts. The JWT flow is implemented but simplified — no MFA, no biometric setup. Tokens are long-lived for demo convenience.

### 10.1 Patient Authentication

```
Patient Onboarding (simplified for hackathon):
1. Patient opens app, selects from pre-loaded demo accounts
2. JWT issued with claims: { patient_id, site_id, trial_id, role: "patient" }
3. No email/password required for demo

Session Management:
- Access tokens: 24-hour expiry (extended for demo)
- No refresh token rotation for hackathon
```

### 10.2 Staff Authentication

```
Staff Login (simplified for hackathon):
1. Select demo account from dropdown (CRC, PI, Medical Monitor)
2. JWT issued immediately — no password or MFA

RBAC Matrix (enforced even in hackathon):
┌────────────────────┬─────┬─────┬─────────────────┬───────────────┐
│ Permission         │ CRC │ PI  │ Medical Monitor  │ Study Manager │
├────────────────────┼─────┼─────┼─────────────────┼───────────────┤
│ View patient data  │ Own │ Own │ All sites        │ All sites     │
│ (own site only)    │ site│ site│                  │               │
├────────────────────┼─────┼─────┼─────────────────┼───────────────┤
│ Review symptoms    │ ✅  │ ✅  │ ✅ (read-only)   │ ❌            │
├────────────────────┼─────┼─────┼─────────────────┼───────────────┤
│ Manage alerts      │ ✅  │ ✅  │ ✅               │ ❌            │
├────────────────────┼─────┼─────┼─────────────────┼───────────────┤
│ View cohort        │ Own │ Own │ ✅               │ ✅            │
│ analytics          │ site│ site│                  │               │
├────────────────────┼─────┼─────┼─────────────────┼───────────────┤
│ Configure protocol │ ❌  │ ❌  │ ✅               │ ✅            │
├────────────────────┼─────┼─────┼─────────────────┼───────────────┤
│ Export data         │ ❌  │ ✅  │ ✅               │ ✅            │
└────────────────────┴─────┴─────┴─────────────────┴───────────────┘
```

---

## 11. Data Privacy & Compliance

> **Hackathon note:** Full HIPAA/GDPR/21 CFR Part 11 compliance is out of scope for the prototype. All data is mock data on a local machine. The following section documents the production-intent design for reference.

### 11.1 Production-Intent Safeguards (Not Implemented in Hackathon)

| Safeguard | Production Implementation |
|-----------|--------------------------|
| Access Control | RBAC with per-site, per-trial permissions; JWT with scoped claims; automatic session timeout |
| Audit Controls | Immutable audit_log table records all data access and modifications |
| Integrity Controls | Database-level constraints; application-level input validation |
| Transmission Security | TLS 1.3 for all API traffic; certificate pinning in mobile app |
| Encryption | AES-256 at rest; application-level field encryption for PII |

### 11.2 Hackathon Simplifications

- No TLS (all traffic is localhost HTTP)
- No encryption at rest
- No audit logging
- No PII — all patient data is synthetic
- Hardcoded demo accounts, no real authentication
- No consent management

---

## 12. API Specification

### 12.1 Core API Endpoints

All endpoints are served by the single FastAPI monolith. The base URL for local development is `http://localhost:8000/api/v1`.

```
BASE URL: http://localhost:8000/api/v1

AUTHENTICATION (hackathon):
  Demo mode: Authorization: Bearer <hardcoded-demo-jwt>
  Patient endpoints: JWT with role=patient
  Staff endpoints: JWT with role in (crc, pi, medical_monitor, study_manager)

───────────────────────────────────────────────────────────────
PATIENT ENDPOINTS
───────────────────────────────────────────────────────────────

POST   /auth/patient/demo-login
       Body: { patient_id: "uuid" }
       Response: { patient_id, access_token }

GET    /patient/profile
       Response: { patient_id, subject_id, trial_name, site_name,
                   enrollment_date, checkin_frequency, wearable_connected }

POST   /checkins/start
       Body: { session_type: "scheduled" | "ad_hoc", modality: "text" | "voice" }
       Response: { session_id, first_message: { role: "ai", content: "..." },
                   voice_room_token: "..." (if modality=voice) }

POST   /checkins/{session_id}/message
       Body: { content: "patient's message text",
               message_type: "text" | "quick_reply" | "scale_rating",
               selected_reply: "option text" (if quick_reply) }
       Response: { ai_response: { role: "ai", content: "...",
                   quick_replies: ["option1", "option2"] | null },
                   session_status: "in_progress" | "completed" }

GET    /checkins/history?limit=20&offset=0
       Response: { sessions: [{ session_id, started_at, completed_at,
                   modality, symptoms_count, overall_feeling }], total: 45 }

GET    /symptoms/history?limit=20&offset=0
       Response: { symptoms: [{ id, symptom_text, meddra_pt_term,
                   severity_grade, onset_date, is_ongoing, created_at }] }

POST   /wearable/sync
       Body: { readings: [{ metric, value, timestamp, source }] }
       Response: { accepted: 150, rejected: 2, anomalies_detected: 0 }

GET    /wearable/summary?days=7
       Response: { metrics: { heart_rate: { latest, avg, trend },
                   steps: { today, avg_7d }, sleep: { last_night, avg_7d },
                   spo2: { latest, avg } }, anomalies: [...] }

───────────────────────────────────────────────────────────────
VOICE CHECK-IN ENDPOINTS
───────────────────────────────────────────────────────────────

POST   /voice/create-room
       Body: { patient_id, session_id }
       Response: { room_name, participant_token (LiveKit JWT) }

GET    /voice/transcript/{session_id}
       Response: { messages: [{ role, content, timestamp }] }

───────────────────────────────────────────────────────────────
STAFF / DASHBOARD ENDPOINTS
───────────────────────────────────────────────────────────────

POST   /auth/staff/demo-login
       Body: { staff_id: "uuid" }
       Response: { access_token, staff: { id, role, sites } }

GET    /dashboard/patients?trial_id=X&site_id=Y&sort=risk_score&order=desc
       &page=1&per_page=25&risk_tier=high&arm=A
       Response: { patients: [{ patient_id, subject_id, treatment_arm,
                   risk_score, risk_tier, last_checkin_at, open_alerts,
                   latest_symptom, wearable_status }], total: 142, page: 1 }

GET    /dashboard/patients/{patient_id}/timeline?days=30
       Response: { events: [{ type, timestamp, title, details, severity }] }

GET    /dashboard/patients/{patient_id}/symptoms?status=pending_review
       Response: { symptoms: [{ id, symptom_text, meddra_pt_term,
                   severity_grade, ai_confidence, crc_reviewed, ... }] }

PUT    /dashboard/patients/{patient_id}/symptoms/{symptom_id}/review
       Body: { action: "confirm" | "override",
               override_term, override_grade, notes }
       Response: { symptom_id, crc_reviewed: true, reviewed_at, reviewed_by }

GET    /dashboard/patients/{patient_id}/wearable?metric=heart_rate&days=14
       Response: { data_points: [{ timestamp, value }],
                   baseline: { mean, stddev }, anomalies: [...] }

GET    /dashboard/alerts?status=open&severity=critical,high&page=1
       Response: { alerts: [...], total: 10 }

PUT    /dashboard/alerts/{alert_id}
       Body: { action: "acknowledge" | "resolve" | "dismiss" | "escalate",
               note: "resolution note text" }
       Response: { alert_id, status, updated_at }

GET    /dashboard/cohort/ae-incidence?trial_id=X&days=30
       Response: { arms: { A: { n: 71, aes: { ... } }, B: { ... } } }

GET    /dashboard/cohort/wearable-distributions?trial_id=X&metric=resting_heart_rate
       Response: { arms: { A: { median, q1, q3, min, max }, B: { ... } } }

───────────────────────────────────────────────────────────────
WEBSOCKET ENDPOINT
───────────────────────────────────────────────────────────────

WS     /ws/dashboard?trial_id=X&token=<jwt>
       Events pushed: alert:new, checkin:completed, anomaly:detected,
                      risk_score:updated, alert:updated
```

---

## 13. Deployment & Infrastructure

### 13.1 Docker Compose (Local Development — All Services)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ─── Databases ───
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: trialpulse
      POSTGRES_USER: tp_admin
      POSTGRES_PASSWORD: tp_hackathon_2026
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./db/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tp_admin -d trialpulse"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: trialpulse
      MINIO_ROOT_PASSWORD: tp_hackathon_2026
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"   # MinIO console

  # ─── LiveKit Server (self-hosted) ───
  livekit:
    image: livekit/livekit-server:latest
    command: --config /etc/livekit.yaml
    volumes:
      - ./infra/livekit.yaml:/etc/livekit.yaml
    ports:
      - "7880:7880"   # HTTP
      - "7881:7881"   # WebRTC TCP
      - "7882:7882/udp"  # WebRTC UDP
    depends_on:
      - redis

  # ─── Python FastAPI Backend (monolith) ───
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://tp_admin:tp_hackathon_2026@postgres:5432/trialpulse
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: trialpulse
      MINIO_SECRET_KEY: tp_hackathon_2026
      LLM_PROVIDER: anthropic
      LLM_MODEL: claude-sonnet-4-20250514
      LLM_API_KEY: ${LLM_API_KEY}
      LIVEKIT_URL: ws://livekit:7880
      LIVEKIT_API_KEY: devkey
      LIVEKIT_API_SECRET: devsecret
      DEEPGRAM_API_KEY: ${DEEPGRAM_API_KEY:-}
      ENVIRONMENT: development
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      livekit:
        condition: service_started
    volumes:
      - ./backend:/app  # hot reload in dev

  # ─── React Web Dashboard ───
  dashboard:
    build: ./apps/dashboard
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000/api/v1
      VITE_WS_URL: ws://localhost:8000/ws

  # ─── Nginx Reverse Proxy ───
  nginx:
    image: nginx:alpine
    volumes:
      - ./infra/nginx.dev.conf:/etc/nginx/nginx.conf
    ports:
      - "8080:8080"
    depends_on:
      - backend
      - dashboard

volumes:
  pgdata:
  minio_data:
```

**LiveKit Configuration:**

```yaml
# infra/livekit.yaml
port: 7880
rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: false
redis:
  address: redis:6379
keys:
  devkey: devsecret
logging:
  level: info
```

### 13.2 Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with uvicorn (auto-reload in dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**requirements.txt:**

```
# Web framework
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.9.0
pydantic-settings>=2.5.0

# Database
sqlalchemy[asyncio]>=2.0.35
asyncpg>=0.30.0
alembic>=1.13.0

# Redis
redis[hiredis]>=5.2.0

# LLM Orchestration (vendor-agnostic)
langchain>=0.3.0
langchain-core>=0.3.0
langchain-anthropic>=0.3.0
langchain-openai>=0.2.0
langgraph>=0.2.0

# LiveKit
livekit>=0.17.0
livekit-agents>=0.11.0
livekit-plugins-deepgram>=0.7.0
livekit-plugins-silero>=0.7.0

# ML / Data
numpy>=1.26.0
scikit-learn>=1.5.0
scipy>=1.14.0

# Auth
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Object storage
minio>=7.2.0

# Scheduling
apscheduler>=3.10.0

# Utilities
httpx>=0.27.0
python-multipart>=0.0.9
```

### 13.3 Project Directory Structure

```
trialpulse/
├── apps/
│   ├── mobile/                       # React Native patient app (Expo)
│   │   ├── src/
│   │   │   ├── screens/
│   │   │   │   ├── HomeScreen.tsx
│   │   │   │   ├── ChatScreen.tsx
│   │   │   │   ├── VoiceCheckInScreen.tsx
│   │   │   │   ├── TimelineScreen.tsx
│   │   │   │   ├── WearableScreen.tsx
│   │   │   │   └── ProfileScreen.tsx
│   │   │   ├── components/
│   │   │   │   ├── ChatBubble.tsx
│   │   │   │   ├── QuickReplyBar.tsx
│   │   │   │   ├── SeveritySlider.tsx
│   │   │   │   ├── MetricCard.tsx
│   │   │   │   ├── TimelineEvent.tsx
│   │   │   │   ├── VoiceAgentAvatar.tsx
│   │   │   │   └── LiveTranscript.tsx
│   │   │   ├── services/
│   │   │   │   ├── api.ts
│   │   │   │   ├── healthkit.ts
│   │   │   │   ├── healthconnect.ts
│   │   │   │   └── livekit.ts
│   │   │   ├── stores/
│   │   │   │   ├── auth.store.ts
│   │   │   │   ├── checkin.store.ts
│   │   │   │   └── wearable.store.ts
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── app.json
│   │
│   └── dashboard/                    # React web dashboard
│       ├── src/
│       │   ├── pages/
│       │   │   ├── PatientListPage.tsx
│       │   │   ├── PatientDetailPage.tsx
│       │   │   ├── CohortAnalyticsPage.tsx
│       │   │   ├── AlertQueuePage.tsx
│       │   │   └── LoginPage.tsx
│       │   ├── components/
│       │   │   ├── PatientTable.tsx
│       │   │   ├── RiskScoreBadge.tsx
│       │   │   ├── PatientTimeline.tsx
│       │   │   ├── WearableChart.tsx
│       │   │   ├── SymptomReviewPanel.tsx
│       │   │   ├── AlertCard.tsx
│       │   │   ├── CohortAETable.tsx
│       │   │   └── BoxPlotChart.tsx
│       │   ├── hooks/
│       │   │   ├── useWebSocket.ts
│       │   │   ├── usePatients.ts
│       │   │   └── useAlerts.ts
│       │   ├── services/
│       │   │   ├── api.ts
│       │   │   └── websocket.ts
│       │   └── App.tsx
│       └── package.json
│
├── backend/                          # Python FastAPI monolith
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # App factory, lifespan, middleware
│   │   ├── config.py                 # Pydantic Settings
│   │   ├── deps.py                   # Dependency injection
│   │   │
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── jwt.py
│   │   │   ├── checkin/
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   ├── wearable/
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── normalization.py
│   │   │   │   └── anomaly_detection.py
│   │   │   ├── alert/
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── rules.py
│   │   │   │   ├── deduplication.py
│   │   │   │   └── risk_scoring.py
│   │   │   ├── analytics/
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   ├── dashboard/
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   └── voice/
│   │   │       ├── router.py
│   │   │       ├── agent.py
│   │   │       └── service.py
│   │   │
│   │   ├── ai/
│   │   │   ├── llm.py                # Vendor-agnostic LLM factory
│   │   │   ├── chains/
│   │   │   │   ├── conversation.py
│   │   │   │   └── classifier.py
│   │   │   ├── graphs/
│   │   │   │   ├── checkin_graph.py
│   │   │   │   └── classifier_graph.py
│   │   │   ├── prompts/
│   │   │   │   ├── checkin_system.py
│   │   │   │   └── classifier_system.py
│   │   │   └── tools/
│   │   │       └── meddra_lookup.py
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── trial.py
│   │   │   ├── patient.py
│   │   │   ├── checkin.py
│   │   │   ├── symptom.py
│   │   │   ├── wearable.py
│   │   │   ├── alert.py
│   │   │   └── staff.py
│   │   │
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── checkin.py
│   │   │   ├── symptom.py
│   │   │   ├── wearable.py
│   │   │   ├── alert.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── events/
│   │   │   └── bus.py                # Redis pub/sub event bus
│   │   │
│   │   └── ws/
│   │       └── manager.py            # WebSocket connection manager
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic/
│       ├── alembic.ini
│       └── versions/
│
├── db/
│   ├── init.sql                      # Schema from Section 4
│   └── seed.sql                      # Mock data for demo (Section 16)
│
├── infra/
│   ├── docker-compose.yml
│   ├── nginx.dev.conf
│   └── livekit.yaml
│
├── scripts/
│   ├── seed_demo_data.py             # Python script to generate mock data
│   ├── generate_wearable_data.py     # Generate 30 days of wearable readings
│   └── run_demo_scenario.py          # Automated demo scenario runner
│
├── docs/
│   ├── DESIGN.md                     # This document
│   └── API.md                        # OpenAPI spec (auto-generated by FastAPI)
│
├── .env.example                      # Environment variable template
└── README.md
```

---

## 14. Testing Strategy

### 14.1 Test Pyramid

| Level | Scope | Tools | Coverage Target |
|-------|-------|-------|----------------|
| Unit Tests | Individual functions, utilities, data transformations | pytest + pytest-asyncio | >80% line coverage |
| Integration Tests | API endpoints, database interactions, event bus | httpx + pytest + Testcontainers | All API endpoints |
| E2E Tests | Full user flows through the mobile app and dashboard | Detox (mobile), Playwright (dashboard) | Critical paths: check-in, alert triage |
| AI/ML Tests | Symptom classifier accuracy, anomaly detection precision/recall | Custom test harness with labeled datasets | >90% classification accuracy, <15% false positive rate |

### 14.2 Critical Test Scenarios

```
PATIENT APP:
  ✓ Patient can log in with demo account
  ✓ Text check-in conversation flows from greeting to completion
  ✓ Voice check-in connects to LiveKit room and produces transcript
  ✓ AI correctly follows up on reported symptoms
  ✓ Quick replies are selectable and sent correctly
  ✓ Wearable data syncs from HealthKit/Health Connect (or mock)

DASHBOARD:
  ✓ Patient list loads sorted by risk score
  ✓ Real-time WebSocket updates reflect new alerts
  ✓ CRC can review and confirm AI symptom classification
  ✓ CRC can override AI classification with different MedDRA term
  ✓ Alert acknowledgment updates status for all viewers
  ✓ Cohort analytics correctly compare treatment arms

ALERT ENGINE:
  ✓ Grade 3+ symptom triggers medium/critical alert
  ✓ SAE keyword detection triggers critical alert
  ✓ Wearable anomaly above threshold triggers alert
  ✓ 2+ consecutive missed check-ins triggers medium alert
  ✓ Risk score crossing into "high" tier triggers alert
  ✓ Duplicate alerts within 24 hours are merged, not duplicated

AI/ML (LangGraph):
  ✓ Symptom classifier maps "bad headache" → Headache (10019211)
  ✓ Classifier assigns appropriate CTCAE grade based on severity description
  ✓ LangGraph check-in flow progresses through all states correctly
  ✓ Voice transcript is correctly fed into the same LangGraph pipeline
  ✓ Anomaly detector flags HR of 95 when baseline is 70±5
  ✓ Anomaly detector does NOT flag HR of 120 during reported exercise
  ✓ Risk score increases when multiple signals co-occur
```

---

## 15. Hackathon Prototype Scope

### 15.1 What to Build for the Hackathon

#### Must Have (Demo-Ready)

1. **Patient Chat Interface (React Native)** — A working conversational symptom check-in for oncology. Built as a React Native Expo app, demoed on a real mobile device. Uses LangChain + LangGraph for conversation orchestration.

2. **Voice Check-In (LiveKit)** — Real-time voice mode where the patient speaks to the AI agent. LiveKit server self-hosted in Docker. STT → LangGraph → TTS pipeline. Live transcript displayed on screen.

3. **Simulated Wearable Dashboard** — Patient-facing view showing mock wearable data (heart rate, steps, sleep) with sparkline charts. Data is pre-generated. One visible anomaly flag on the heart rate chart.

4. **Researcher Dashboard (Basic)** — Web page showing patient list with risk scores, color-coded by tier. Patient detail with timeline. Alert queue with acknowledge/dismiss buttons. Real-time WebSocket updates.

5. **End-to-End Flow Demo** — Patient completes check-in (text or voice) → AI classifies symptoms → risk score updates → alert appears on researcher dashboard in real time. Split-screen or two-device demo.

#### Nice to Have (If Time Permits)

6. **CRC Symptom Review Panel** — Confirm/override workflow for AI-classified symptoms.
7. **Cohort Analytics View** — Bar chart comparing AE rates between two mock treatment arms.

#### Explicitly Out of Scope for Hackathon

- HIPAA compliance, encryption, audit logging
- Multi-language support
- EDC/CTMS integrations
- Real user registration and authentication (use hardcoded demo accounts)
- Offline support
- Push notifications
- CI/CD, monitoring, log aggregation, secrets management, CDN
- Cloud deployment of any kind

### 15.2 Recommended Tech for the Prototype

| Component | Hackathon Choice | Why |
|-----------|-----------------|-----|
| Patient App | React Native (Expo) | Demo on a real mobile device; cross-platform |
| Dashboard | React + Tailwind + Recharts | Fast styling; Recharts for quick charts |
| Backend | Python FastAPI monolith (async) | Single service; no microservice coordination overhead; hot reload |
| LLM Orchestration | LangChain + LangGraph | Vendor-agnostic; swap providers via env var; stateful check-in graphs |
| Voice | LiveKit (self-hosted Docker) + Deepgram STT | Low-latency real-time voice; self-contained in Docker |
| Database | PostgreSQL 16 (Docker) | Full-featured; stores everything including wearable time-series |
| Cache/Events | Redis 7 (Docker) | Pub/sub event bus + caching |
| Object Storage | MinIO (Docker) | S3-compatible; local; no cloud account needed |
| Wearable Data | Pre-generated Python seed script | Simulated 30-day history for 5 mock patients with anomaly patterns |
| Deployment | Docker Compose (localhost) | Single `docker compose up` to start everything |

### 15.3 Prototype Data Seeding

Create a seed script that generates 5 mock patients with realistic data:

```
Patient 001: "Healthy" — no symptoms, normal wearables, risk score 8
Patient 002: "Mild symptoms" — Grade 1 fatigue, normal wearables, risk score 22
Patient 003: "Concerning trend" — Grade 2 nausea + rising resting HR (the demo patient), risk score 67
Patient 004: "Missed check-ins" — No symptoms but 3 missed check-ins, risk score 45
Patient 005: "High risk" — Grade 3 nausea + Grade 2 headache + HR anomaly + declining sleep, risk score 85
```

This gives the demo a realistic spread of scenarios to showcase during the presentation.

---

## 16. Hackathon Demo Setup & Mock Data Guide

This section provides step-by-step instructions for setting up the complete demo environment with mock data, preparing the system for a live demo in front of a judging panel.

### 16.1 Prerequisites

Before starting, ensure the following are installed on the demo machine:

- **Docker Desktop** (v4.25+) with Docker Compose v2
- **Node.js** (v20+) and npm/yarn
- **Python** (3.12+) — only needed if running seed scripts outside Docker
- **Expo CLI** (`npm install -g expo-cli`) for the React Native mobile app
- **Expo Go** app installed on the demo phone (iOS or Android)
- **API keys** (stored in `.env` file):
  - `LLM_API_KEY` — Anthropic API key (or OpenAI, depending on `LLM_PROVIDER`)
  - `DEEPGRAM_API_KEY` — Deepgram API key for voice STT (optional; voice demo requires this)

### 16.2 Environment Setup

**Step 1: Clone and configure environment**

```bash
git clone <repo-url> trialpulse
cd trialpulse
cp .env.example .env
# Edit .env to add your API keys:
#   LLM_API_KEY=sk-ant-...
#   LLM_PROVIDER=anthropic
#   LLM_MODEL=claude-sonnet-4-20250514
#   DEEPGRAM_API_KEY=...  (for voice demo)
```

**Step 2: Start all services**

```bash
docker compose up -d --build
```

This starts: PostgreSQL, Redis, MinIO, LiveKit, the FastAPI backend, the React dashboard, and Nginx. The database schema (`init.sql`) and seed data (`seed.sql`) are automatically loaded on first boot.

**Step 3: Verify services are running**

```bash
docker compose ps
# All services should show "running" / "healthy"

# Test backend health
curl http://localhost:8000/api/v1/health
# Expected: {"status": "ok", "services": {"postgres": "connected", "redis": "connected", "livekit": "connected"}}

# Test dashboard
open http://localhost:3000
```

**Step 4: Start the mobile app**

```bash
cd apps/mobile
npm install
npx expo start
# Scan the QR code with Expo Go on the demo phone
# Ensure demo phone and laptop are on the same WiFi network
```

### 16.3 Mock Data Specification

The seed script (`scripts/seed_demo_data.py`) generates the following mock data. Run it if the Docker init scripts didn't auto-seed:

```bash
cd scripts
python seed_demo_data.py
```

#### Trial & Protocol

```
Trial: "ONCO-2026-TP1"
  Sponsor: "Meridian Therapeutics"
  Title: "Phase II Study of MT-401 in Advanced Non-Small Cell Lung Cancer"
  Therapeutic Area: Oncology
  Phase: II
  Status: Active

Protocol Config:
  Check-in Frequency: Daily
  Check-in Window: 24 hours
  Expected Side Effects: Nausea, Fatigue, Headache, Rash, Diarrhoea, Alopecia
  Wearable Metrics: heart_rate, resting_heart_rate, steps, sleep_minutes, spo2
  Alert Thresholds:
    heart_rate_resting_max: 100
    spo2_min: 92
    anomaly_z_threshold: 2.5
```

#### Site & Staff

```
Site: "001 — Memorial City Cancer Center"
  Country: US
  Timezone: America/Chicago

Staff Accounts (all use password "demo2026" — or no password in demo mode):
  Dr. Sarah Chen       | PI               | staff_id: <uuid-pi>
  James Smith           | CRC              | staff_id: <uuid-crc>
  Dr. Rachel Torres     | Medical Monitor  | staff_id: <uuid-mm>
```

#### Mock Patients (5 patients, 30 days of data each)

**Patient 001 — "Maria Gonzalez" (Healthy Baseline)**
```
Subject ID: 001-0089
Treatment Arm: A (MT-401)
Enrollment Date: 2026-02-26
Risk Score: 8 (LOW 🟢)

Check-In History: 28/30 days completed (93% compliance)
Symptoms: None reported
Wearable Data:
  Resting HR: 68±3 bpm (stable, no anomalies)
  Steps: 7,200±1,500/day
  Sleep: 7.5±0.8 hrs/night
  SpO2: 97±1%
Alerts: None
```

**Patient 002 — "Robert Kim" (Mild Symptoms)**
```
Subject ID: 001-0017
Treatment Arm: B (Placebo)
Enrollment Date: 2026-02-20
Risk Score: 22 (LOW 🟢)

Check-In History: 25/30 days completed (83% compliance)
Symptoms:
  - Fatigue (Grade 1), ongoing since Day 10, AI confidence: 0.91
  - Headache (Grade 1), resolved after 3 days, AI confidence: 0.89
Wearable Data:
  Resting HR: 72±4 bpm (normal)
  Steps: 5,800±2,000/day (slightly below average — matches fatigue)
  Sleep: 6.8±1.0 hrs/night
  SpO2: 98±1%
Alerts: None (Grade 1 symptoms don't trigger alerts)
```

**Patient 003 — "David Thompson" (Concerning Trend — THE DEMO PATIENT)**
```
Subject ID: 001-0042
Treatment Arm: A (MT-401)
Enrollment Date: 2026-02-15
Risk Score: 67 (MEDIUM 🟡) → will escalate to 82 (HIGH 🔴) during live demo

Check-In History: 26/30 days completed (87% compliance)
Symptoms (escalating pattern over last 2 weeks):
  Day 16: Fatigue (Grade 1) — AI confidence: 0.88
  Day 20: Nausea (Grade 1) — AI confidence: 0.92
  Day 24: Nausea (Grade 2) + Fatigue (Grade 1) — AI confidence: 0.94, 0.87
  Day 27: Nausea (Grade 2) + Headache (Grade 1) — AI confidence: 0.91, 0.85
  Day 28: [LIVE DEMO — patient will check in with Grade 3 nausea + Grade 2 headache]

Wearable Data (anomaly pattern baked in):
  Resting HR: Started at 72±5 bpm, gradually rising:
    Days 1-14: 70-74 bpm (normal baseline)
    Days 15-21: 74-78 bpm (subtle increase)
    Days 22-28: 78-88 bpm (accelerating — trend anomaly detected on Day 25)
    Day 28: 88 bpm (point anomaly: z-score 3.2)
  Steps: Declining from 6,500 to 3,200/day over last 10 days
  Sleep: Declining from 7.2 hrs to 5.2 hrs over last 7 days
  SpO2: 96±1% (normal)

Alerts (pre-seeded):
  Day 25: 🟡 MEDIUM — Resting HR trend detected (+2.3 bpm/day over 7 days)
  Day 27: 🟡 MEDIUM — Sleep duration declining (22% below baseline)
  [LIVE DEMO will generate: 🔴 CRITICAL — Resting HR point anomaly + Grade 3 symptom]
```

**Patient 004 — "Jennifer Walsh" (Missed Check-Ins)**
```
Subject ID: 001-0055
Treatment Arm: B (Placebo)
Enrollment Date: 2026-02-22
Risk Score: 45 (MEDIUM 🟡)

Check-In History: 18/30 days completed (60% compliance)
  Last 5 days: MISSED, MISSED, MISSED, completed, MISSED
Symptoms: None reported (but low engagement is concerning)
Wearable Data:
  Resting HR: 75±6 bpm (normal but higher variance)
  Steps: 4,100±2,500/day (irregular)
  Sleep: 6.0±1.5 hrs/night (irregular)
  SpO2: 97±1%
  Last wearable sync: 12 hours ago (device still active)

Alerts:
  Day 26: 🟡 MEDIUM — Missed check-in (2nd consecutive)
  Day 28: 🟡 MEDIUM — Missed check-in (3rd consecutive)
```

**Patient 005 — "Thomas Okafor" (High Risk)**
```
Subject ID: 001-0033
Treatment Arm: A (MT-401)
Enrollment Date: 2026-02-18
Risk Score: 85 (HIGH 🔴)

Check-In History: 27/30 days completed (90% compliance)
Symptoms (multiple concurrent):
  Day 18: Nausea (Grade 2) — AI confidence: 0.93
  Day 22: Nausea (Grade 3) + Headache (Grade 2) — AI confidence: 0.95, 0.90
  Day 25: Nausea (Grade 3) + Headache (Grade 2) + Fatigue (Grade 2) — AI confidence: 0.96, 0.92, 0.88
  Day 27: Nausea (Grade 3, ongoing) + Headache (Grade 2, ongoing) — already reviewed by CRC

Wearable Data:
  Resting HR: 82±6 bpm (elevated; baseline was 70±4)
  Steps: 2,100/day (severely reduced from baseline of 8,000)
  Sleep: 4.5 hrs/night (severely reduced from baseline of 7.8)
  SpO2: 94±2% (borderline low)

Alerts:
  Day 22: 🔴 CRITICAL — Grade 3 nausea reported
  Day 23: 🔴 HIGH — Resting HR elevated (z-score: 3.0)
  Day 25: 🔴 HIGH — Risk score elevated to HIGH (was MEDIUM)
  Day 25: 🟡 MEDIUM — SpO2 dropped to 91% (single reading)
```

### 16.4 Live Demo Scenario (Step-by-Step Script)

Follow this script during the live demo. It's designed to show the end-to-end flow in approximately 8-10 minutes.

**Setup before going on stage:**

1. Open the researcher dashboard on a laptop browser at `http://localhost:3000`
2. Log in as CRC "James Smith" — the patient list should show all 5 patients
3. Have the React Native app open on the demo phone with Patient 003 (David Thompson) logged in
4. Have two browser tabs ready: one for the dashboard, one for the patient detail view of Patient 003
5. Optionally, run the automated demo scenario to pre-trigger the voice check-in background state:
   ```bash
   python scripts/run_demo_scenario.py --prepare
   ```

**Demo Script:**

**Act 1: "The Problem" (1 minute)**
- Show the dashboard with 5 patients. Point out the risk score distribution.
- Highlight Patient 005 (high risk, 🔴) — "This patient has been flagged by our system for multiple co-occurring symptoms and wearable anomalies."
- Highlight Patient 003 (medium, 🟡) — "This patient looks okay, but there's a subtle trend we're about to catch."

**Act 2: "Patient Check-In via Text" (3 minutes)**
- Switch to the mobile phone with Patient 003 logged in.
- Tap "Start Text Check-In."
- Walk through the conversation with the AI:
  - AI greets David, asks how he's feeling → type or quick-reply "Not great" (or 2/5)
  - AI asks about symptoms → type "I've been really nauseous, worse than last time. I also have a bad headache behind my eyes"
  - AI follows up on nausea severity → select "7/10" on the severity slider
  - AI asks about onset → "It started getting bad yesterday"
  - AI asks about headache → type "It's a constant pressure, maybe 5/10"
  - AI summarizes: "You reported nausea (severe) and headache (moderate). I'll share this with your care team."
- The check-in completes.

**Act 3: "Real-Time Dashboard Update" (2 minutes)**
- Switch to the laptop dashboard — the audience sees:
  - A toast notification: "🔴 CRITICAL: Grade 3 nausea reported for 001-0042"
  - Patient 003's risk score animates from 67 → 82, the indicator turns RED
  - The alert queue updates with a new critical alert
- Click into Patient 003's detail view:
  - Show the timeline with the new check-in entry
  - Show the wearable chart with the rising heart rate trend and the new anomaly flag
  - Point out: "The AI classified the nausea as Grade 3 based on the 7/10 severity rating. This was corroborated by rising resting heart rate and declining sleep — the system connected these signals."

**Act 4: "Voice Check-In Demo" (2 minutes — if voice is configured)**
- Go back to the mobile phone
- Tap "Start Voice Check-In"
- The AI greets the patient via voice — the avatar pulses as it speaks
- Speak naturally: "I'm still not feeling great, the nausea hasn't gone away"
- Show the live transcript updating in real time on the phone screen
- The AI responds via voice, asking follow-up questions
- After 2-3 exchanges, end the session
- Point out: "The same LangGraph agent drives both the text and voice experience. Patients choose the modality they're comfortable with."

**Act 5: "CRC Workflow" (1 minute)**
- On the dashboard, show the "Pending Review" badge on Patient 003
- Click into the Symptoms tab → open the review panel
- Show the AI's classification: Nausea → MedDRA 10028813, Grade 3, Confidence 94%
- Click "Confirm" — the badge clears, the review is recorded
- Point out: "The CRC always has the final say. The AI accelerates the process, but a human confirms every classification."

**Act 6: "Cohort Analytics" (1 minute, if built)**
- Navigate to Cohort Analytics
- Show the AE incidence comparison between Arm A and Arm B
- Point out: "Nausea is significantly higher in the treatment arm (42% vs 18%, p=0.003). This is the kind of safety signal that normally takes weeks to surface — TrialPulse makes it visible in real time."

### 16.5 Demo Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend won't start | Check `docker compose logs backend` — likely missing API key in `.env` |
| Mobile app can't connect | Ensure phone and laptop are on same WiFi; check `VITE_API_URL` points to laptop's local IP, not `localhost` |
| Voice check-in fails | Verify `DEEPGRAM_API_KEY` is set; check `docker compose logs livekit` |
| WebSocket updates not arriving | Check that the dashboard is connected to `ws://localhost:8000/ws`; inspect browser DevTools Network tab |
| Risk score not updating | The alert engine runs asynchronously — wait 2-3 seconds after check-in completes; check `docker compose logs backend` for event bus errors |
| Database is empty | Run `python scripts/seed_demo_data.py` or restart postgres to re-run init scripts: `docker compose restart postgres` |
| LiveKit rooms not connecting | Ensure ports 7880-7882 are not blocked; check `docker compose logs livekit` |

### 16.6 Demo Reset (Between Practice Runs)

To reset the database to a clean state with fresh mock data:

```bash
# Stop all services
docker compose down

# Remove database volume (this wipes all data)
docker volume rm trialpulse_pgdata

# Restart — init.sql and seed.sql will re-run automatically
docker compose up -d --build

# Wait for postgres to initialize (~10 seconds)
sleep 10

# Verify
curl http://localhost:8000/api/v1/dashboard/patients?trial_id=<trial-uuid>
```

To reset only the "live demo" portion (keep base data, remove live check-in data):

```bash
python scripts/run_demo_scenario.py --reset
```

---

## Appendix A: MedDRA Quick Reference

Common adverse event terms used in the prototype:

| MedDRA Code | Preferred Term | System Organ Class |
|-------------|---------------|-------------------|
| 10019211 | Headache | Nervous system disorders |
| 10028813 | Nausea | Gastrointestinal disorders |
| 10047700 | Vomiting | Gastrointestinal disorders |
| 10016256 | Fatigue | General disorders |
| 10012735 | Diarrhoea | Gastrointestinal disorders |
| 10003246 | Arthralgia | Musculoskeletal disorders |
| 10037087 | Pyrexia | General disorders |
| 10040785 | Rash | Skin disorders |
| 10002272 | Alopecia | Skin disorders |
| 10022437 | Insomnia | Psychiatric disorders |

## Appendix B: CTCAE v5 Grading Reference

| Grade | Severity | General Description |
|-------|----------|-------------------|
| 1 | Mild | Asymptomatic or mild symptoms; observation only; no intervention needed |
| 2 | Moderate | Minimal, local, or noninvasive intervention indicated; limiting age-appropriate activities |
| 3 | Severe | Medically significant but not immediately life-threatening; hospitalization or prolongation of existing hospitalization indicated |
| 4 | Life-threatening | Urgent intervention indicated |
| 5 | Death | Death related to adverse event |

---

*This document is a living specification. Update it as design decisions are made and implementation progresses.*
