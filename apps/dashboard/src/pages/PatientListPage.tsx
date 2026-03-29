import { useState } from 'react';
import { usePatientList } from '../hooks/usePatients';

interface PatientListPageProps {
  trialId: string;
  onSelectPatient: (patientId: string) => void;
}

export function PatientListPage({ trialId, onSelectPatient }: PatientListPageProps) {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = usePatientList(trialId, page);

  if (isLoading) return <div style={{ padding: 20 }}>Loading patients...</div>;
  if (isError) return <div style={{ padding: 20 }}>Error loading patients. Ensure the backend is running.</div>;
  if (!data) return <div style={{ padding: 20 }}>No data available.</div>;

  return (
    <div style={{ padding: 20 }}>
      <div className="projects-section-header" style={{ marginBottom: 20 }}>
        <p>Patient List</p>
      </div>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--muted-border)' }}>
            <th style={{ padding: 10 }}>Risk Score</th>
            <th style={{ padding: 10 }}>Subject ID</th>
            <th style={{ padding: 10 }}>Arm</th>
            <th style={{ padding: 10 }}>Last Check-In</th>
            <th style={{ padding: 10 }}>Open Alerts</th>
            <th style={{ padding: 10 }}>Latest Symptom</th>
            <th style={{ padding: 10 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.patients.map((patient) => (
            <tr key={patient.patient_id} style={{ borderBottom: '1px solid var(--muted-border)' }}>
              <td style={{ padding: 10 }}>
                {patient.risk_score !== null ? (
                  <span style={{ 
                    color: patient.risk_tier === 'high' ? '#ef4444' : patient.risk_tier === 'medium' ? '#f59e0b' : '#10b981',
                    fontWeight: 'bold'
                  }}>
                    {patient.risk_tier === 'high' ? '🔴 ' : patient.risk_tier === 'medium' ? '🟡 ' : '🟢 '}
                    {patient.risk_score}
                  </span>
                ) : '-'}
              </td>
              <td style={{ padding: 10 }}>{patient.subject_id}</td>
              <td style={{ padding: 10 }}>{patient.treatment_arm || '-'}</td>
              <td style={{ padding: 10 }}>
                {patient.last_checkin_at ? new Date(patient.last_checkin_at).toLocaleDateString() : '-'}
              </td>
              <td style={{ padding: 10 }}>{patient.open_alerts}</td>
              <td style={{ padding: 10 }}>{patient.latest_symptom || 'None'}</td>
              <td style={{ padding: 10 }}>
                <button 
                  onClick={() => onSelectPatient(patient.patient_id)}
                  style={{
                    backgroundColor: 'var(--link-color)',
                    color: 'white',
                    border: 'none',
                    padding: '6px 12px',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  View Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: 20, display: 'flex', gap: 10, alignItems: 'center' }}>
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))} 
          disabled={page === 1}
          style={{ padding: '6px 12px', cursor: page === 1 ? 'not-allowed' : 'pointer' }}
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button 
          onClick={() => setPage(p => p + 1)}
          disabled={data.patients.length < 20}
          style={{ padding: '6px 12px', cursor: data.patients.length < 20 ? 'not-allowed' : 'pointer' }}
        >
          Next
        </button>
      </div>
    </div>
  );
}
