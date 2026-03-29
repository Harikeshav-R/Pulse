import { useAlerts, useUpdateAlert } from '../hooks/useAlerts';

interface AlertQueuePageProps {
  trialId: string;
}

export function AlertQueuePage({ trialId }: AlertQueuePageProps) {
  const { data, isLoading, isError } = useAlerts(trialId, 'open');
  const updateAlert = useUpdateAlert();

  if (isLoading) return <div style={{ padding: 20 }}>Loading alerts...</div>;
  if (isError) return <div style={{ padding: 20 }}>Error loading alerts.</div>;

  const handleAcknowledge = (alertId: string) => {
    updateAlert.mutate({ alertId, payload: { action: 'acknowledge', note: 'Acknowledged via dashboard' } });
  };

  const handleDismiss = (alertId: string) => {
    updateAlert.mutate({ alertId, payload: { action: 'dismiss', note: 'Dismissed via dashboard' } });
  };

  return (
    <div style={{ padding: 20 }}>
      <div className="projects-section-header" style={{ marginBottom: 20 }}>
        <p>Alert Queue</p>
      </div>

      {!data || data.length === 0 ? (
        <p>No open alerts.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
          {data.map((alert) => (
            <div key={alert.id} style={{ 
              padding: 15, 
              borderLeft: `4px solid ${alert.severity === 'critical' ? '#ef4444' : alert.severity === 'high' ? '#f97316' : '#facc15'}`,
              backgroundColor: 'var(--surface-bg)',
              borderRadius: 4,
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                <strong style={{ fontSize: '1.1em' }}>
                  {alert.severity === 'critical' ? '🔴 CRITICAL' : alert.severity === 'high' ? '🟠 HIGH' : '🟡 MEDIUM'} | {alert.title}
                </strong>
                <span style={{ fontSize: '0.8em', color: 'var(--secondary-color)' }}>
                  {new Date(alert.created_at).toLocaleString()}
                </span>
              </div>
              <p style={{ margin: '0 0 15px 0' }}>{alert.description}</p>
              
              <div style={{ display: 'flex', gap: 10 }}>
                <button 
                  onClick={() => handleAcknowledge(alert.id)}
                  disabled={updateAlert.isPending}
                  style={{ padding: '6px 12px', backgroundColor: 'var(--link-color)', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}
                >
                  Acknowledge
                </button>
                <button 
                  onClick={() => handleDismiss(alert.id)}
                  disabled={updateAlert.isPending}
                  style={{ padding: '6px 12px', backgroundColor: 'transparent', color: 'var(--text-color)', border: '1px solid var(--muted-border)', borderRadius: 4, cursor: 'pointer' }}
                >
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
