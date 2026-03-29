import { usePatientDetail, usePatientTimeline, usePatientSymptoms, usePatientCheckins } from '../hooks/usePatients';
import type { CheckinSessionItem } from '../hooks/usePatients';
import { useState } from 'react';

interface PatientDetailPageProps {
  patientId: string;
  onBack: () => void;
}

const UNIFIED_ALERT_TEXT =
  'Risk score elevated to HIGH — worsening nausea now Grade 3, resting HR up 16 bpm over baseline, fatigue and headache co-occurring.';

function formatTimelineLabel(type: string): string {
  const map: Record<string, string> = {
    risk_alert: 'Risk alert',
    symptom_reported: 'Symptom',
    wearable_trend: 'Wearable trend',
    check_in: 'Check-in',
    alert: 'Alert',
  };
  return map[type] ?? type.replace(/_/g, ' ');
function CheckinSession({ session }: { session: CheckinSessionItem }) {
  const [expanded, setExpanded] = useState(false);
  const startedAt = session.started_at ? new Date(session.started_at).toLocaleString() : 'N/A';
  const duration = session.duration_seconds ? `${Math.round(session.duration_seconds / 60)}m ${session.duration_seconds % 60}s` : 'In progress';

  return (
    <div style={{ padding: '12px 0', borderBottom: '1px solid var(--muted-border)' }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
      >
        <div>
          <span style={{ fontWeight: 'bold' }}>{startedAt}</span>
          <span
            style={{
              marginLeft: 10,
              padding: '2px 8px',
              borderRadius: 4,
              fontSize: '0.8em',
              fontWeight: 600,
              backgroundColor: session.modality === 'voice' ? '#dbeafe' : '#f0fdf4',
              color: session.modality === 'voice' ? '#1d4ed8' : '#15803d',
            }}
          >
            {session.modality}
          </span>
          <span
            style={{
              marginLeft: 8,
              padding: '2px 8px',
              borderRadius: 4,
              fontSize: '0.8em',
              backgroundColor: session.status === 'completed' ? '#f0fdf4' : '#fef9c3',
              color: session.status === 'completed' ? '#15803d' : '#a16207',
            }}
          >
            {session.status}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ color: 'var(--secondary-color)', fontSize: '0.85em' }}>
            {duration} | {session.messages.length} messages
          </span>
          <span style={{ fontSize: '0.9em' }}>{expanded ? '▼' : '▶'}</span>
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: 12, padding: '12px 16px', backgroundColor: '#f8fafc', borderRadius: 8 }}>
          {session.messages.length === 0 ? (
            <p style={{ color: 'var(--secondary-color)', fontStyle: 'italic' }}>No transcript messages recorded.</p>
          ) : (
            session.messages.map((msg) => (
              <div key={msg.id} style={{ marginBottom: 10 }}>
                <div style={{ fontSize: '0.75em', color: 'var(--secondary-color)', marginBottom: 2 }}>
                  {msg.role === 'ai' ? 'TrialPulse AI' : 'Patient'} — {new Date(msg.created_at).toLocaleTimeString()}
                  {msg.message_type === 'voice_transcript' && (
                    <span style={{ marginLeft: 6, opacity: 0.6 }}>🎙</span>
                  )}
                </div>
                <div
                  style={{
                    padding: '8px 12px',
                    borderRadius: 8,
                    backgroundColor: msg.role === 'ai' ? '#e0e7ff' : '#ffffff',
                    border: msg.role === 'ai' ? 'none' : '1px solid var(--muted-border)',
                    fontSize: '0.9em',
                    lineHeight: 1.5,
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export function PatientDetailPage({ patientId, onBack }: PatientDetailPageProps) {
  const [activeTab, setActiveTab] = useState<'timeline' | 'symptoms' | 'checkins'>('timeline');
  const { data: patient, isLoading: patientLoading } = usePatientDetail(patientId);
  const { data: timeline, isLoading: timelineLoading } = usePatientTimeline(patientId);
  const { data: symptoms, isLoading: symptomsLoading } = usePatientSymptoms(patientId);
  const { data: checkins, isLoading: checkinsLoading } = usePatientCheckins(patientId);

  if (patientLoading) return <div style={{ padding: 20 }}>Loading patient details...</div>;
  if (!patient) return <div style={{ padding: 20 }}>Patient not found</div>;

  const tier = patient.risk_score?.tier ?? '';
  const tierUpper = tier ? tier.toUpperCase() : '';
  const tabs = [
    { key: 'timeline' as const, label: 'Timeline' },
    { key: 'checkins' as const, label: `Check-ins${checkins ? ` (${checkins.total})` : ''}` },
    { key: 'symptoms' as const, label: 'Symptoms' },
  ];

  return (
    <div style={{ padding: 20, maxWidth: 900 }}>
      <button onClick={onBack} style={{ marginBottom: 20, cursor: 'pointer' }}>
        ← Back to List
      </button>

      <div
        style={{
          marginBottom: 24,
          padding: 20,
          backgroundColor: 'var(--surface-bg)',
          borderRadius: 12,
          border: '1px solid var(--muted-border)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        }}
      >
        <p style={{ margin: '0 0 8px', fontSize: 13, fontWeight: 600, color: 'var(--light-font)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Unified clinical picture
        </p>
        <p style={{ margin: '0 0 16px', fontSize: 15, lineHeight: 1.55, color: 'var(--main-color)' }}>
          One view pulls together this morning&apos;s <strong>Grade 3 nausea</strong>, a{' '}
          <strong>heart-rate anomaly</strong> trending about <strong>+2.3 bpm per day</strong> with resting HR{' '}
          <strong>up 16 bpm</strong> over baseline, and <strong>declining sleep and activity</strong> versus this
          participant&apos;s usual pattern.
        </p>
        <div
          style={{
            margin: 0,
            padding: '14px 16px',
            borderLeft: '4px solid #ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.08)',
            borderRadius: '0 8px 8px 0',
            fontSize: 15,
            lineHeight: 1.5,
            color: 'var(--main-color)',
          }}
        >
          <strong style={{ display: 'block', marginBottom: 6, fontSize: 12, color: 'var(--light-font)', textTransform: 'uppercase' }}>
            Active alert
          </strong>
          {UNIFIED_ALERT_TEXT}
        </div>
      </div>

      <div
        style={{
          marginBottom: 24,
          padding: 16,
          backgroundColor: 'var(--surface-bg)',
          borderRadius: 8,
          border: '1px solid var(--muted-border)',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: 12,
        }}
      >
        <div>
          <div style={{ fontSize: 12, color: 'var(--light-font)', marginBottom: 4 }}>Subject</div>
          <div style={{ fontWeight: 700, fontSize: 18 }}>{patient.subject_id}</div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: 'var(--light-font)', marginBottom: 4 }}>Arm</div>
          <div style={{ fontWeight: 600 }}>{patient.treatment_arm ?? '—'}</div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: 'var(--light-font)', marginBottom: 4 }}>Enrolled</div>
          <div style={{ fontWeight: 600 }}>{new Date(patient.enrollment_date).toLocaleDateString()}</div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: 'var(--light-font)', marginBottom: 4 }}>Risk score</div>
          <div style={{ fontWeight: 700, color: tier === 'high' ? '#dc2626' : 'var(--main-color)' }}>
            {patient.risk_score?.score ?? '—'}
            {tierUpper ? ` (${tierUpper})` : ''}
          </div>
        </div>
      </div>

      <div
        style={{
          display: 'flex',
          gap: 10,
          borderBottom: '1px solid var(--muted-border)',
          paddingBottom: 10,
          marginBottom: 20,
        }}
      >
        <button
          type="button"
          onClick={() => setActiveTab('timeline')}
          style={{
            fontWeight: activeTab === 'timeline' ? 'bold' : 'normal',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: activeTab === 'timeline' ? 'var(--link-color)' : 'var(--secondary-color)',
          }}
        >
          Supporting timeline
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('symptoms')}
          style={{
            fontWeight: activeTab === 'symptoms' ? 'bold' : 'normal',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: activeTab === 'symptoms' ? 'var(--link-color)' : 'var(--secondary-color)',
          }}
        >
          Symptoms
        </button>
      <div style={{ display: 'flex', gap: 10, borderBottom: '1px solid var(--muted-border)', paddingBottom: 10, marginBottom: 20 }}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{ fontWeight: activeTab === tab.key ? 'bold' : 'normal', background: 'none', border: 'none', cursor: 'pointer', color: activeTab === tab.key ? 'var(--link-color)' : 'var(--text-color)' }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'timeline' && (
        <div>
          {timelineLoading ? (
            <p>Loading timeline...</p>
          ) : (
            timeline?.events?.map((event, idx) => (
              <div key={idx} style={{ padding: '14px 0', borderBottom: '1px solid var(--muted-border)' }}>
                <div style={{ fontSize: 12, color: 'var(--light-font)', marginBottom: 6 }}>
                  {new Date(event.timestamp).toLocaleString()} · {formatTimelineLabel(event.type)}
                </div>
                <div style={{ fontWeight: 700, marginBottom: 4 }}>{event.title}</div>
                <div style={{ color: 'var(--secondary-color)', fontSize: 14, lineHeight: 1.5 }}>{event.details}</div>
              </div>
            ))
          )}
          {(!timeline?.events || timeline.events.length === 0) && !timelineLoading && <p>No events found.</p>}
        </div>
      )}

      {activeTab === 'checkins' && (
        <div>
          {checkinsLoading ? (
            <p>Loading check-ins...</p>
          ) : checkins?.sessions?.length ? (
            checkins.sessions.map((session) => (
              <CheckinSession key={session.session_id} session={session} />
            ))
          ) : (
            <p>No check-in sessions found.</p>
          )}
        </div>
      )}

      {activeTab === 'symptoms' && (
        <div>
          {symptomsLoading ? (
            <p>Loading symptoms...</p>
          ) : (
            symptoms?.map((symptom) => (
              <div key={symptom.id} style={{ padding: '14px 0', borderBottom: '1px solid var(--muted-border)' }}>
                <div style={{ fontWeight: 700 }}>
                  {symptom.meddra_pt_term || 'Unclassified'}
                  {symptom.severity_grade != null ? ` · Grade ${symptom.severity_grade}` : ''}
                </div>
                <div style={{ marginTop: 6 }}>Patient report: &ldquo;{symptom.symptom_text}&rdquo;</div>
                <div style={{ color: 'var(--secondary-color)', fontSize: 13, marginTop: 6 }}>
                  Onset: {symptom.onset_date ?? '—'} · CRC reviewed: {symptom.crc_reviewed ? 'Yes' : 'Pending'}
                </div>
              </div>
            ))
          )}
          {(!symptoms || symptoms.length === 0) && !symptomsLoading && <p>No symptoms found.</p>}
        </div>
      )}
    </div>
  );
}
