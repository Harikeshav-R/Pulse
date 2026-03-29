import { usePatientDetail, usePatientTimeline, usePatientSymptoms, usePatientCheckins } from '../hooks/usePatients';
import type { CheckinSessionItem } from '../hooks/usePatients';
import { useState } from 'react';

interface PatientDetailPageProps {
  patientId: string;
  onBack: () => void;
}

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

  const tabs = [
    { key: 'timeline' as const, label: 'Timeline' },
    { key: 'checkins' as const, label: `Check-ins${checkins ? ` (${checkins.total})` : ''}` },
    { key: 'symptoms' as const, label: 'Symptoms' },
  ];

  return (
    <div style={{ padding: 20 }}>
      <button onClick={onBack} style={{ marginBottom: 20, cursor: 'pointer' }}>
        ← Back to List
      </button>

      <div style={{ marginBottom: 20, padding: 15, backgroundColor: 'var(--surface-bg)', borderRadius: 8, border: '1px solid var(--muted-border)' }}>
        <h2>Patient {patient.subject_id}</h2>
        <p><strong>Arm:</strong> {patient.treatment_arm || 'N/A'}</p>
        <p><strong>Enrolled:</strong> {new Date(patient.enrollment_date).toLocaleDateString()}</p>
        <p><strong>Risk Score:</strong> {patient.risk_score?.score} ({patient.risk_score?.tier})</p>
      </div>

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
          {timelineLoading ? <p>Loading timeline...</p> : timeline?.events?.map((event, idx) => (
            <div key={idx} style={{ padding: '10px 0', borderBottom: '1px solid var(--muted-border)' }}>
              <div style={{ fontWeight: 'bold' }}>{new Date(event.timestamp).toLocaleString()} - {event.type}</div>
              <div>{event.title}</div>
              <div style={{ color: 'var(--secondary-color)', fontSize: '0.9em' }}>{event.details}</div>
            </div>
          ))}
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
          {symptomsLoading ? <p>Loading symptoms...</p> : symptoms?.map((symptom) => (
            <div key={symptom.id} style={{ padding: '10px 0', borderBottom: '1px solid var(--muted-border)' }}>
              <div style={{ fontWeight: 'bold' }}>{symptom.meddra_pt_term || 'Unclassified'} (Grade {symptom.severity_grade || '?'})</div>
              <div>Original text: "{symptom.symptom_text}"</div>
              <div style={{ color: 'var(--secondary-color)', fontSize: '0.9em' }}>Onset: {symptom.onset_date} | Reviewed: {symptom.crc_reviewed ? 'Yes' : 'No'}</div>
            </div>
          ))}
          {(!symptoms || symptoms.length === 0) && !symptomsLoading && <p>No symptoms found.</p>}
        </div>
      )}
    </div>
  );
}
