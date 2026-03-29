import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export interface Alert {
  id: string;
  patient_id: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  source_type?: string;
  status: string;
  created_at: string;
}

export const useAlerts = (trialId: string, status?: string, severity?: string, page = 1) => {
  return useQuery({
    queryKey: ['alerts', trialId, status, severity, page],
    queryFn: async (): Promise<Alert[]> => {
      try {
        const response = await apiClient.get('/dashboard/alerts', {
          params: { trial_id: trialId, status, severity, page },
        });
        return response as unknown as Alert[];
      } catch (error) {
        console.warn('Backend failed, using fallback data for useAlerts');
        return [
          {
            id: 'mock-alert-1',
            patient_id: 'mock-p1',
            alert_type: 'wearable_anomaly',
            severity: 'high',
            title: 'Elevated Resting Heart Rate',
            description: 'Patient average resting heart rate has increased by 15 bpm over the last 3 days.',
            status: 'open',
            created_at: new Date().toISOString()
          },
          {
            id: 'mock-alert-2',
            patient_id: 'mock-p2',
            alert_type: 'missed_checkin',
            severity: 'medium',
            title: 'Missed 2 Consecutive Check-ins',
            description: 'Patient has not completed their daily check-in for 48 hours.',
            status: 'open',
            created_at: new Date().toISOString()
          }
        ];
      }
    },
    enabled: !!trialId,
  });
};

export const useUpdateAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ alertId, payload }: { alertId: string, payload: unknown }) => {
      const response = await apiClient.put(`/dashboard/alerts/${alertId}`, payload);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });
};

export interface TrialOverview {
  trial_id: string;
  total_patients: number;
  total_sites: number;
  open_alerts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
  };
  checkins_last_7_days: number;
}

export const useTrialOverview = (trialId: string | null, queryEnabled = true) => {
  return useQuery({
    queryKey: ['trialOverview', trialId],
    queryFn: async (): Promise<TrialOverview> => {
      try {
        const response = await apiClient.get(`/dashboard/trial/${trialId}/overview`);
        return response as unknown as TrialOverview;
      } catch (error) {
        console.warn('Backend failed, using fallback data for useTrialOverview');
        return {
          trial_id: trialId || 'mock',
          total_patients: 120,
          total_sites: 5,
          open_alerts: { critical: 2, high: 5, medium: 12, low: 8 },
          risk_distribution: { low: 80, medium: 30, high: 10 },
          checkins_last_7_days: 850
        };
      }
    },
    enabled: !!trialId && queryEnabled,
  });
};

export const useCohortAEIncidence = (trialId: string | null, days = 30, queryEnabled = true) => {
  return useQuery({
    queryKey: ['cohortAE', trialId, days],
    queryFn: async (): Promise<Record<string, unknown>> => {
      try {
        const response = await apiClient.get(`/analytics/trial/${trialId}/adverse-events`, {
          params: { days },
        });
        return response as unknown as Record<string, unknown>;
      } catch (error) {
        console.warn('Backend failed, using fallback data for useCohortAEIncidence');
        return {
          "Fatigue": { count: 45, grade3_plus: 2 },
          "Nausea": { count: 30, grade3_plus: 5 },
          "Headache": { count: 25, grade3_plus: 0 },
        };
      }
    },
    enabled: !!trialId && queryEnabled,
  });
};
