-- TrialPulse Database Schema
-- PostgreSQL 16

-- =============================================================
-- EXTENSIONS
-- =============================================================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================
-- TRIALS AND PROTOCOLS
-- =============================================================

CREATE TABLE trials (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sponsor_name      VARCHAR(255) NOT NULL,
    protocol_number   VARCHAR(100) NOT NULL UNIQUE,
    trial_title       TEXT NOT NULL,
    therapeutic_area  VARCHAR(100) NOT NULL,
    phase             VARCHAR(10) NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE protocol_config (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id              UUID NOT NULL REFERENCES trials(id) ON DELETE CASCADE,
    checkin_frequency     VARCHAR(20) NOT NULL DEFAULT 'daily',
    checkin_window_hours  INT NOT NULL DEFAULT 24,
    expected_side_effects JSONB NOT NULL DEFAULT '[]',
    symptom_questions     JSONB NOT NULL DEFAULT '[]',
    wearable_required     BOOLEAN NOT NULL DEFAULT false,
    wearable_metrics      JSONB NOT NULL DEFAULT '["heart_rate", "steps", "sleep"]',
    alert_thresholds      JSONB NOT NULL DEFAULT '{}',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- SITES AND STAFF
-- =============================================================

CREATE TABLE sites (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id      UUID NOT NULL REFERENCES trials(id) ON DELETE CASCADE,
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
    role          VARCHAR(30) NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE staff_site_access (
    staff_id  UUID NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    site_id   UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    role      VARCHAR(30) NOT NULL,
    PRIMARY KEY (staff_id, site_id)
);

-- =============================================================
-- PATIENTS
-- =============================================================

CREATE TABLE patients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id             UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    enrollment_code     VARCHAR(50) NOT NULL UNIQUE,
    subject_id          VARCHAR(50) NOT NULL,
    treatment_arm       VARCHAR(50),
    enrollment_date     DATE NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'enrolled',
    app_registered      BOOLEAN NOT NULL DEFAULT false,
    wearable_connected  BOOLEAN NOT NULL DEFAULT false,
    timezone            VARCHAR(50) NOT NULL DEFAULT 'UTC',
    language            VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(site_id, subject_id)
);

CREATE TABLE patient_app_accounts (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id        UUID NOT NULL UNIQUE REFERENCES patients(id) ON DELETE CASCADE,
    device_token      TEXT,
    device_platform   VARCHAR(10),
    device_model      VARCHAR(100),
    app_version       VARCHAR(20),
    last_active_at    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- SYMPTOM JOURNAL
-- =============================================================

CREATE TABLE checkin_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    session_type    VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    modality        VARCHAR(10) NOT NULL DEFAULT 'text',
    status          VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    duration_seconds INT,
    overall_feeling  INT,
    voice_room_id   VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE checkin_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES checkin_sessions(id) ON DELETE CASCADE,
    sequence_number INT NOT NULL,
    role            VARCHAR(10) NOT NULL,
    content         TEXT NOT NULL,
    message_type    VARCHAR(20) NOT NULL DEFAULT 'text',
    quick_replies   JSONB,
    selected_reply  VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE symptom_entries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id          UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    session_id          UUID REFERENCES checkin_sessions(id) ON DELETE SET NULL,
    symptom_text        TEXT NOT NULL,
    meddra_pt_code      VARCHAR(20),
    meddra_pt_term      VARCHAR(255),
    meddra_soc          VARCHAR(255),
    severity_grade      INT,
    onset_date          DATE,
    is_ongoing          BOOLEAN DEFAULT true,
    resolution_date     DATE,
    relationship        VARCHAR(30),
    action_taken        VARCHAR(50),
    ai_confidence       FLOAT,
    crc_reviewed        BOOLEAN NOT NULL DEFAULT false,
    crc_reviewed_at     TIMESTAMPTZ,
    crc_reviewed_by     UUID REFERENCES staff(id) ON DELETE SET NULL,
    crc_override_term   VARCHAR(255),
    crc_override_grade  INT,
    is_sae              BOOLEAN NOT NULL DEFAULT false,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- WEARABLE DATA
-- =============================================================

CREATE TABLE wearable_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    platform        VARCHAR(50) NOT NULL,
    device_name     VARCHAR(255),
    device_model    VARCHAR(255),
    last_sync_at    TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE wearable_readings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    metric          VARCHAR(50) NOT NULL,
    value           FLOAT NOT NULL,
    source          VARCHAR(50),
    quality         VARCHAR(20) DEFAULT 'raw',
    recorded_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_wearable_readings_patient_metric
    ON wearable_readings(patient_id, metric, recorded_at DESC);

CREATE TABLE wearable_baselines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    metric          VARCHAR(50) NOT NULL,
    baseline_mean   FLOAT NOT NULL,
    baseline_stddev FLOAT NOT NULL,
    baseline_min    FLOAT,
    baseline_max    FLOAT,
    sample_count    INT NOT NULL,
    baseline_start  DATE NOT NULL,
    baseline_end    DATE NOT NULL,
    is_current      BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(patient_id, metric, is_current)
);

CREATE TABLE wearable_anomalies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    metric          VARCHAR(50) NOT NULL,
    anomaly_type    VARCHAR(30) NOT NULL,
    detected_at     TIMESTAMPTZ NOT NULL,
    value           FLOAT NOT NULL,
    baseline_mean   FLOAT NOT NULL,
    z_score         FLOAT,
    trend_slope     FLOAT,
    trend_window    INT,
    severity        VARCHAR(10) NOT NULL,
    resolved        BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- ALERTS AND RISK SCORES
-- =============================================================

CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    alert_type      VARCHAR(30) NOT NULL,
    severity        VARCHAR(10) NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    source_type     VARCHAR(30),
    source_id       UUID,
    status          VARCHAR(20) NOT NULL DEFAULT 'open',
    assigned_to     UUID REFERENCES staff(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_scores (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id              UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    score                   INT NOT NULL,
    tier                    VARCHAR(10) NOT NULL,
    symptom_component       FLOAT NOT NULL,
    wearable_component      FLOAT NOT NULL,
    engagement_component    FLOAT NOT NULL,
    compliance_component    FLOAT NOT NULL,
    contributing_factors    JSONB NOT NULL DEFAULT '[]',
    calculated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risk_scores_patient_date ON risk_scores(patient_id, calculated_at DESC);
CREATE INDEX idx_alerts_patient_status ON alerts(patient_id, status);
CREATE INDEX idx_symptom_entries_patient ON symptom_entries(patient_id, created_at DESC);
CREATE INDEX idx_checkin_sessions_patient ON checkin_sessions(patient_id, started_at DESC);
