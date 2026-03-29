import { usePatientDetail, usePatientTimeline, usePatientSymptoms } from '../hooks/usePatients';
import { useState } from 'react';

interface PatientDetailPageProps {
  patientId: string;
  onBack: () => void;
}

export function PatientDetailPage({ patientId, onBack }: PatientDetailPageProps) {
  const [activeTab, setActiveTab] = useState<'timeline' | 'symptoms'>('timeline');
  const { data: patient, isLoading: patientLoading } = usePatientDetail(patientId);
  const { data: timeline, isLoading: timelineLoading } = usePatientTimeline(patientId);
  const { data: symptoms, isLoading: symptomsLoading } = usePatientSymptoms(patientId);

  if (patientLoading) return <div style={{ padding: 20 }}>Loading patient details...</div>;
  if (!patient) return <div style={{ padding: 20 }}>Patient not found</div>;

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
        <button 
          onClick={() => setActiveTab('timeline')} 
          style={{ fontWeight: activeTab === 'timeline' ? 'bold' : 'normal', background: 'none', border: 'none', cursor: 'pointer', color: activeTab === 'timeline' ? 'var(--link-color)' : 'var(--text-color)' }}
        >
          Timeline
        </button>
        <button 
          onClick={() => setActiveTab('symptoms')}
          style={{ fontWeight: activeTab === 'symptoms' ? 'bold' : 'normal', background: 'none', border: 'none', cursor: 'pointer', color: activeTab === 'symptoms' ? 'var(--link-color)' : 'var(--text-color)' }}
        >
          Symptoms
        </button>
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
