-- TrialPulse Seed Data
-- 1 trial, 1 site, 3 staff, 5 patients with 30 days of realistic data

-- =============================================================
-- Fixed UUIDs for demo reproducibility
-- =============================================================

-- Trial & Protocol
INSERT INTO trials (id, sponsor_name, protocol_number, trial_title, therapeutic_area, phase, status)
VALUES (
    'a1b2c3d4-0000-4000-8000-000000000001',
    'Meridian Therapeutics',
    'ONCO-2026-TP1',
    'Phase II Study of MT-401 in Advanced Non-Small Cell Lung Cancer',
    'oncology',
    'II',
    'active'
);

INSERT INTO protocol_config (id, trial_id, checkin_frequency, checkin_window_hours, expected_side_effects, symptom_questions, wearable_required, wearable_metrics, alert_thresholds)
VALUES (
    'a1b2c3d4-0000-4000-8000-000000000002',
    'a1b2c3d4-0000-4000-8000-000000000001',
    'daily',
    24,
    '[
        {"term": "Nausea", "meddra_code": "10028813", "expected_frequency": "very_common"},
        {"term": "Fatigue", "meddra_code": "10016256", "expected_frequency": "very_common"},
        {"term": "Headache", "meddra_code": "10019211", "expected_frequency": "common"},
        {"term": "Rash", "meddra_code": "10040785", "expected_frequency": "common"},
        {"term": "Diarrhoea", "meddra_code": "10012735", "expected_frequency": "common"},
        {"term": "Alopecia", "meddra_code": "10002272", "expected_frequency": "uncommon"}
    ]',
    '[
        "How are you feeling overall today?",
        "Have you noticed any new or worsening symptoms?",
        "Have you taken all your study medication as prescribed?"
    ]',
    true,
    '["heart_rate", "resting_heart_rate", "steps", "sleep_minutes", "spo2"]',
    '{"heart_rate_resting_max": 100, "spo2_min": 92, "anomaly_z_threshold": 2.5}'
);

-- =============================================================
-- SITE
-- =============================================================

INSERT INTO sites (id, trial_id, site_number, site_name, country, timezone)
VALUES (
    'a1b2c3d4-0000-4000-8000-000000000010',
    'a1b2c3d4-0000-4000-8000-000000000001',
    '001',
    'Memorial City Cancer Center',
    'US',
    'America/Chicago'
);

-- =============================================================
-- STAFF (password hash = bcrypt of "demo2026")
-- =============================================================

INSERT INTO staff (id, email, password_hash, first_name, last_name, role) VALUES
('a1b2c3d4-0000-4000-8000-000000000020', 'sarah.chen@memorial.org',    '$2b$12$LJ3m5sA0x8Mwx0jXq4q0aOzKZE7R5J5K5J5K5J5K5J5K5J5K5J', 'Sarah',  'Chen',   'pi'),
('a1b2c3d4-0000-4000-8000-000000000021', 'james.smith@memorial.org',   '$2b$12$LJ3m5sA0x8Mwx0jXq4q0aOzKZE7R5J5K5J5K5J5K5J5K5J5K5J', 'James',  'Smith',  'crc'),
('a1b2c3d4-0000-4000-8000-000000000022', 'rachel.torres@meridian.com', '$2b$12$LJ3m5sA0x8Mwx0jXq4q0aOzKZE7R5J5K5J5K5J5K5J5K5J5K5J', 'Rachel', 'Torres', 'medical_monitor');

INSERT INTO staff_site_access (staff_id, site_id, role) VALUES
('a1b2c3d4-0000-4000-8000-000000000020', 'a1b2c3d4-0000-4000-8000-000000000010', 'pi'),
('a1b2c3d4-0000-4000-8000-000000000021', 'a1b2c3d4-0000-4000-8000-000000000010', 'crc'),
('a1b2c3d4-0000-4000-8000-000000000022', 'a1b2c3d4-0000-4000-8000-000000000010', 'medical_monitor');

-- =============================================================
-- PATIENTS
-- =============================================================

-- Patient 001: Maria Gonzalez — Healthy Baseline (Risk: 8, LOW)
INSERT INTO patients (id, site_id, enrollment_code, subject_id, treatment_arm, enrollment_date, status, app_registered, wearable_connected, timezone)
VALUES ('a1b2c3d4-0000-4000-8000-000000000101', 'a1b2c3d4-0000-4000-8000-000000000010', 'TP-2026-001', '001-0089', 'A', '2026-02-26', 'active', true, true, 'America/Chicago');

-- Patient 002: Robert Kim — Mild Symptoms (Risk: 22, LOW)
INSERT INTO patients (id, site_id, enrollment_code, subject_id, treatment_arm, enrollment_date, status, app_registered, wearable_connected, timezone)
VALUES ('a1b2c3d4-0000-4000-8000-000000000102', 'a1b2c3d4-0000-4000-8000-000000000010', 'TP-2026-002', '001-0017', 'B', '2026-02-20', 'active', true, true, 'America/Chicago');

-- Patient 003: David Thompson — Concerning Trend / THE DEMO PATIENT (Risk: 67→82)
INSERT INTO patients (id, site_id, enrollment_code, subject_id, treatment_arm, enrollment_date, status, app_registered, wearable_connected, timezone)
VALUES ('a1b2c3d4-0000-4000-8000-000000000103', 'a1b2c3d4-0000-4000-8000-000000000010', 'TP-2026-003', '001-0042', 'A', '2026-02-15', 'active', true, true, 'America/Chicago');

-- Patient 004: Jennifer Walsh — Missed Check-Ins (Risk: 45, MEDIUM)
INSERT INTO patients (id, site_id, enrollment_code, subject_id, treatment_arm, enrollment_date, status, app_registered, wearable_connected, timezone)
VALUES ('a1b2c3d4-0000-4000-8000-000000000104', 'a1b2c3d4-0000-4000-8000-000000000010', 'TP-2026-004', '001-0055', 'B', '2026-02-22', 'active', true, true, 'America/Chicago');

-- Patient 005: Thomas Okafor — High Risk (Risk: 85, HIGH)
INSERT INTO patients (id, site_id, enrollment_code, subject_id, treatment_arm, enrollment_date, status, app_registered, wearable_connected, timezone)
VALUES ('a1b2c3d4-0000-4000-8000-000000000105', 'a1b2c3d4-0000-4000-8000-000000000010', 'TP-2026-005', '001-0033', 'A', '2026-02-18', 'active', true, true, 'America/Chicago');

-- Patient app accounts
INSERT INTO patient_app_accounts (patient_id, device_platform, app_version, last_active_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000101', 'ios',     '1.0.0', NOW() - INTERVAL '2 hours'),
('a1b2c3d4-0000-4000-8000-000000000102', 'android', '1.0.0', NOW() - INTERVAL '18 hours'),
('a1b2c3d4-0000-4000-8000-000000000103', 'ios',     '1.0.0', NOW() - INTERVAL '4 hours'),
('a1b2c3d4-0000-4000-8000-000000000104', 'android', '1.0.0', NOW() - INTERVAL '48 hours'),
('a1b2c3d4-0000-4000-8000-000000000105', 'ios',     '1.0.0', NOW() - INTERVAL '6 hours');

-- =============================================================
-- WEARABLE CONNECTIONS
-- =============================================================

INSERT INTO wearable_connections (patient_id, platform, device_name, device_model, last_sync_at, is_active) VALUES
('a1b2c3d4-0000-4000-8000-000000000101', 'apple_healthkit', 'Maria''s Apple Watch', 'Apple Watch Series 9', NOW() - INTERVAL '1 hour',  true),
('a1b2c3d4-0000-4000-8000-000000000102', 'google_health_connect', 'Robert''s Pixel Watch', 'Pixel Watch 2', NOW() - INTERVAL '3 hours', true),
('a1b2c3d4-0000-4000-8000-000000000103', 'apple_healthkit', 'David''s Apple Watch', 'Apple Watch Ultra 2',  NOW() - INTERVAL '2 hours', true),
('a1b2c3d4-0000-4000-8000-000000000104', 'apple_healthkit', 'Jennifer''s Watch', 'Apple Watch SE',          NOW() - INTERVAL '12 hours', true),
('a1b2c3d4-0000-4000-8000-000000000105', 'apple_healthkit', 'Thomas''s Apple Watch', 'Apple Watch Series 9', NOW() - INTERVAL '4 hours', true);

-- =============================================================
-- WEARABLE BASELINES (established from first 14 days)
-- =============================================================

-- Patient 001 — Maria (healthy)
INSERT INTO wearable_baselines (patient_id, metric, baseline_mean, baseline_stddev, baseline_min, baseline_max, sample_count, baseline_start, baseline_end) VALUES
('a1b2c3d4-0000-4000-8000-000000000101', 'resting_heart_rate', 68.0, 3.0, 63, 73,  14, '2026-02-26', '2026-03-11'),
('a1b2c3d4-0000-4000-8000-000000000101', 'steps',             7200, 1500, 4500, 10200, 14, '2026-02-26', '2026-03-11'),
('a1b2c3d4-0000-4000-8000-000000000101', 'sleep_minutes',      450, 48,  360, 540,   14, '2026-02-26', '2026-03-11'),
('a1b2c3d4-0000-4000-8000-000000000101', 'spo2',               97.0, 1.0, 95, 99,   14, '2026-02-26', '2026-03-11');

-- Patient 002 — Robert (mild)
INSERT INTO wearable_baselines (patient_id, metric, baseline_mean, baseline_stddev, baseline_min, baseline_max, sample_count, baseline_start, baseline_end) VALUES
('a1b2c3d4-0000-4000-8000-000000000102', 'resting_heart_rate', 72.0, 4.0, 65, 80,   14, '2026-02-20', '2026-03-05'),
('a1b2c3d4-0000-4000-8000-000000000102', 'steps',             5800, 2000, 2800, 9800, 14, '2026-02-20', '2026-03-05'),
('a1b2c3d4-0000-4000-8000-000000000102', 'sleep_minutes',      408, 60,  300, 510,   14, '2026-02-20', '2026-03-05'),
('a1b2c3d4-0000-4000-8000-000000000102', 'spo2',               98.0, 1.0, 96, 100,   14, '2026-02-20', '2026-03-05');

-- Patient 003 — David (concerning trend — THE DEMO PATIENT)
INSERT INTO wearable_baselines (patient_id, metric, baseline_mean, baseline_stddev, baseline_min, baseline_max, sample_count, baseline_start, baseline_end) VALUES
('a1b2c3d4-0000-4000-8000-000000000103', 'resting_heart_rate', 72.0, 5.0, 64, 80,   14, '2026-02-15', '2026-02-28'),
('a1b2c3d4-0000-4000-8000-000000000103', 'steps',             6500, 1800, 3500, 9500, 14, '2026-02-15', '2026-02-28'),
('a1b2c3d4-0000-4000-8000-000000000103', 'sleep_minutes',      432, 54,  340, 510,   14, '2026-02-15', '2026-02-28'),
('a1b2c3d4-0000-4000-8000-000000000103', 'spo2',               96.0, 1.0, 94, 98,    14, '2026-02-15', '2026-02-28');

-- Patient 004 — Jennifer (missed checkins)
INSERT INTO wearable_baselines (patient_id, metric, baseline_mean, baseline_stddev, baseline_min, baseline_max, sample_count, baseline_start, baseline_end) VALUES
('a1b2c3d4-0000-4000-8000-000000000104', 'resting_heart_rate', 75.0, 6.0, 66, 86,   14, '2026-02-22', '2026-03-07'),
('a1b2c3d4-0000-4000-8000-000000000104', 'steps',             4100, 2500, 1000, 8500, 14, '2026-02-22', '2026-03-07'),
('a1b2c3d4-0000-4000-8000-000000000104', 'sleep_minutes',      360, 90,  180, 510,   14, '2026-02-22', '2026-03-07'),
('a1b2c3d4-0000-4000-8000-000000000104', 'spo2',               97.0, 1.0, 95, 99,    14, '2026-02-22', '2026-03-07');

-- Patient 005 — Thomas (high risk)
INSERT INTO wearable_baselines (patient_id, metric, baseline_mean, baseline_stddev, baseline_min, baseline_max, sample_count, baseline_start, baseline_end) VALUES
('a1b2c3d4-0000-4000-8000-000000000105', 'resting_heart_rate', 70.0, 4.0, 63, 77,   14, '2026-02-18', '2026-03-03'),
('a1b2c3d4-0000-4000-8000-000000000105', 'steps',             8000, 1600, 5200, 11000, 14, '2026-02-18', '2026-03-03'),
('a1b2c3d4-0000-4000-8000-000000000105', 'sleep_minutes',      468, 42,  380, 540,   14, '2026-02-18', '2026-03-03'),
('a1b2c3d4-0000-4000-8000-000000000105', 'spo2',               97.0, 1.0, 95, 99,    14, '2026-02-18', '2026-03-03');

-- =============================================================
-- SYMPTOM ENTRIES (pre-seeded history)
-- =============================================================

-- Patient 002 — Robert: mild symptoms
INSERT INTO symptom_entries (patient_id, symptom_text, meddra_pt_code, meddra_pt_term, meddra_soc, severity_grade, onset_date, is_ongoing, ai_confidence, crc_reviewed, crc_reviewed_at, crc_reviewed_by, created_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000102', 'I feel a bit tired, more than usual', '10016256', 'Fatigue', 'General disorders', 1, '2026-03-02', true, 0.91, true, '2026-03-03 10:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-02 08:30:00+00'),
('a1b2c3d4-0000-4000-8000-000000000102', 'Had a mild headache for a couple days', '10019211', 'Headache', 'Nervous system disorders', 1, '2026-03-05', false, 0.89, true, '2026-03-06 09:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-05 08:15:00+00');

-- Patient 003 — David: escalating pattern (the demo patient)
INSERT INTO symptom_entries (patient_id, symptom_text, meddra_pt_code, meddra_pt_term, meddra_soc, severity_grade, onset_date, is_ongoing, ai_confidence, crc_reviewed, crc_reviewed_at, crc_reviewed_by, created_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000103', 'Feeling more tired than usual lately', '10016256', 'Fatigue', 'General disorders', 1, '2026-03-03', true, 0.88, true, '2026-03-04 10:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-03 08:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000103', 'Started feeling nauseous in the mornings', '10028813', 'Nausea', 'Gastrointestinal disorders', 1, '2026-03-07', true, 0.92, true, '2026-03-08 09:30:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-07 08:15:00+00'),
('a1b2c3d4-0000-4000-8000-000000000103', 'Nausea is worse today, had to lie down. Also still tired.', '10028813', 'Nausea', 'Gastrointestinal disorders', 2, '2026-03-07', true, 0.94, true, '2026-03-12 10:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-11 08:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000103', 'Nausea continuing, and now I have a headache too', '10028813', 'Nausea', 'Gastrointestinal disorders', 2, '2026-03-07', true, 0.91, false, NULL, NULL, '2026-03-14 08:00:00+00');

-- Patient 005 — Thomas: multiple concurrent high-grade symptoms
INSERT INTO symptom_entries (patient_id, symptom_text, meddra_pt_code, meddra_pt_term, meddra_soc, severity_grade, onset_date, is_ongoing, ai_confidence, crc_reviewed, crc_reviewed_at, crc_reviewed_by, created_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000105', 'Feeling nauseous, can''t keep food down', '10028813', 'Nausea', 'Gastrointestinal disorders', 2, '2026-03-05', true, 0.93, true, '2026-03-06 09:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-05 08:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'Nausea much worse, vomited twice. Also have a bad headache.', '10028813', 'Nausea', 'Gastrointestinal disorders', 3, '2026-03-05', true, 0.95, true, '2026-03-10 10:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-09 08:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'Bad headache behind my eyes, pressure feeling', '10019211', 'Headache', 'Nervous system disorders', 2, '2026-03-09', true, 0.90, true, '2026-03-10 10:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-09 08:05:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'Nausea still bad, headache ongoing, and now very fatigued. Can barely get out of bed.', '10028813', 'Nausea', 'Gastrointestinal disorders', 3, '2026-03-05', true, 0.96, true, '2026-03-13 09:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-12 08:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'Extreme fatigue, sleeping most of the day', '10016256', 'Fatigue', 'General disorders', 2, '2026-03-10', true, 0.88, true, '2026-03-13 09:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-12 08:05:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'Nausea and headache still ongoing', '10028813', 'Nausea', 'Gastrointestinal disorders', 3, '2026-03-05', true, 0.96, true, '2026-03-15 09:00:00+00', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-14 08:00:00+00');

-- =============================================================
-- WEARABLE ANOMALIES (pre-seeded)
-- =============================================================

-- Patient 003 — David: trend anomaly detected on day 25
INSERT INTO wearable_anomalies (patient_id, metric, anomaly_type, detected_at, value, baseline_mean, z_score, trend_slope, trend_window, severity) VALUES
('a1b2c3d4-0000-4000-8000-000000000103', 'resting_heart_rate', 'trend_anomaly', '2026-03-12 10:00:00+00', 82.0, 72.0, NULL, 2.3, 7, 'medium'),
('a1b2c3d4-0000-4000-8000-000000000103', 'sleep_minutes',      'trend_anomaly', '2026-03-14 06:00:00+00', 312.0, 432.0, NULL, -17.1, 7, 'medium');

-- Patient 005 — Thomas: point anomalies
INSERT INTO wearable_anomalies (patient_id, metric, anomaly_type, detected_at, value, baseline_mean, z_score, severity) VALUES
('a1b2c3d4-0000-4000-8000-000000000105', 'resting_heart_rate', 'point_anomaly', '2026-03-10 08:00:00+00', 82.0, 70.0, 3.0, 'high'),
('a1b2c3d4-0000-4000-8000-000000000105', 'spo2',              'point_anomaly', '2026-03-12 14:00:00+00', 91.0, 97.0, 6.0, 'high');

-- =============================================================
-- ALERTS (pre-seeded)
-- =============================================================

-- Patient 003 — David
INSERT INTO alerts (patient_id, alert_type, severity, title, description, source_type, status, created_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000103', 'wearable_anomaly', 'medium', 'Resting Heart Rate trend detected',
 'Resting heart rate increasing at +2.3 bpm/day over 7 days. Current: 82 bpm (baseline: 72±5 bpm).',
 'wearable_anomaly', 'acknowledged', '2026-03-12 10:05:00+00'),
('a1b2c3d4-0000-4000-8000-000000000103', 'wearable_anomaly', 'medium', 'Sleep duration declining',
 'Sleep duration declining 22% below baseline. Current: 5.2 hrs (baseline: 7.2±0.9 hrs).',
 'wearable_anomaly', 'open', '2026-03-14 06:05:00+00');

-- Patient 004 — Jennifer: missed checkins
INSERT INTO alerts (patient_id, alert_type, severity, title, description, source_type, status, created_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000104', 'missed_checkin', 'medium', 'Missed check-in (2 consecutive)',
 'Patient did not complete their scheduled check-in. Last completed check-in: 48 hours ago. Last wearable sync: 12 hours ago.',
 'system', 'open', '2026-03-13 18:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000104', 'missed_checkin', 'medium', 'Missed check-in (3 consecutive)',
 'Patient did not complete their scheduled check-in for the 3rd consecutive day. Last wearable sync: 12 hours ago (device still active).',
 'system', 'open', '2026-03-15 18:00:00+00');

-- Patient 005 — Thomas: multiple critical/high alerts
INSERT INTO alerts (patient_id, alert_type, severity, title, description, source_type, status, assigned_to, created_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000105', 'symptom_severe', 'critical', 'Grade 3 Nausea reported',
 'Patient reported Nausea (Grade 3) during check-in. Onset: 2026-03-05. AI confidence: 0.95. Vomiting twice reported.',
 'symptom_entry', 'acknowledged', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-09 08:05:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'wearable_anomaly', 'high', 'Resting Heart Rate elevated',
 'Resting heart rate elevated to 82 bpm (baseline: 70±4 bpm). Z-score: 3.0.',
 'wearable_anomaly', 'acknowledged', 'a1b2c3d4-0000-4000-8000-000000000021', '2026-03-10 08:05:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'risk_score_elevated', 'high', 'Patient risk score elevated to HIGH',
 'Risk score increased from 55 to 85. Contributing factors: Grade 3 nausea, elevated resting HR, declining sleep.',
 'system', 'open', NULL, '2026-03-12 12:00:00+00'),
('a1b2c3d4-0000-4000-8000-000000000105', 'wearable_anomaly', 'medium', 'SpO2 dropped to 91%',
 'SpO2 dropped to 91% (baseline: 97±1%). Single reading. No symptoms reported at time of reading.',
 'wearable_anomaly', 'open', NULL, '2026-03-12 14:05:00+00');

-- =============================================================
-- RISK SCORES (latest snapshot per patient)
-- =============================================================

INSERT INTO risk_scores (patient_id, score, tier, symptom_component, wearable_component, engagement_component, compliance_component, contributing_factors, calculated_at) VALUES
('a1b2c3d4-0000-4000-8000-000000000101', 8,  'low',    0,  0, 3, 5, '[]', NOW() - INTERVAL '1 hour'),
('a1b2c3d4-0000-4000-8000-000000000102', 22, 'low',    11, 0, 5, 6, '[{"factor": "Grade 1 fatigue ongoing", "weight": 3}, {"factor": "83% check-in compliance", "weight": 5}]', NOW() - INTERVAL '2 hours'),
('a1b2c3d4-0000-4000-8000-000000000103', 67, 'medium', 20, 22, 10, 15, '[{"factor": "Grade 2 nausea (escalating)", "weight": 12}, {"factor": "Resting HR trend +2.3 bpm/day", "weight": 15}, {"factor": "Sleep declining 22%", "weight": 7}]', NOW() - INTERVAL '3 hours'),
('a1b2c3d4-0000-4000-8000-000000000104', 45, 'medium', 0,  5,  15, 15, '[{"factor": "3 consecutive missed check-ins", "weight": 15}, {"factor": "60% check-in compliance", "weight": 15}]', NOW() - INTERVAL '1 hour'),
('a1b2c3d4-0000-4000-8000-000000000105', 85, 'high',   35, 25, 5,  10, '[{"factor": "Grade 3 nausea (ongoing)", "weight": 15}, {"factor": "Grade 2 headache + fatigue", "weight": 12}, {"factor": "Resting HR elevated z=3.0", "weight": 15}, {"factor": "SpO2 borderline (91%)", "weight": 10}]', NOW() - INTERVAL '2 hours');

-- =============================================================
-- CHECKIN SESSIONS (sample history)
-- =============================================================

-- Patient 001 — Maria: consistent daily checkins
INSERT INTO checkin_sessions (patient_id, session_type, modality, status, started_at, completed_at, duration_seconds, overall_feeling) VALUES
('a1b2c3d4-0000-4000-8000-000000000101', 'scheduled', 'text', 'completed', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 55 minutes', 300, 5),
('a1b2c3d4-0000-4000-8000-000000000101', 'scheduled', 'text', 'completed', NOW() - INTERVAL '26 hours', NOW() - INTERVAL '25 hours 50 minutes', 280, 5),
('a1b2c3d4-0000-4000-8000-000000000101', 'scheduled', 'text', 'completed', NOW() - INTERVAL '50 hours', NOW() - INTERVAL '49 hours 55 minutes', 240, 4);

-- Patient 003 — David: the demo patient's recent checkins
INSERT INTO checkin_sessions (patient_id, session_type, modality, status, started_at, completed_at, duration_seconds, overall_feeling) VALUES
('a1b2c3d4-0000-4000-8000-000000000103', 'scheduled', 'text',  'completed', '2026-03-14 08:00:00+00', '2026-03-14 08:08:00+00', 480, 2),
('a1b2c3d4-0000-4000-8000-000000000103', 'scheduled', 'voice', 'completed', '2026-03-13 08:00:00+00', '2026-03-13 08:05:00+00', 300, 3),
('a1b2c3d4-0000-4000-8000-000000000103', 'scheduled', 'text',  'completed', '2026-03-12 08:00:00+00', '2026-03-12 08:06:00+00', 360, 3);

-- Patient 005 — Thomas: high-risk patient checkins
INSERT INTO checkin_sessions (patient_id, session_type, modality, status, started_at, completed_at, duration_seconds, overall_feeling) VALUES
('a1b2c3d4-0000-4000-8000-000000000105', 'scheduled', 'text',  'completed', '2026-03-14 08:00:00+00', '2026-03-14 08:10:00+00', 600, 1),
('a1b2c3d4-0000-4000-8000-000000000105', 'scheduled', 'text',  'completed', '2026-03-12 08:00:00+00', '2026-03-12 08:12:00+00', 720, 2),
('a1b2c3d4-0000-4000-8000-000000000105', 'scheduled', 'voice', 'completed', '2026-03-09 08:00:00+00', '2026-03-09 08:07:00+00', 420, 2);
