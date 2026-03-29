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
      const response = await apiClient.get('/dashboard/alerts', {
        params: { trial_id: trialId, status, severity, page },
      });
      return response as unknown as Alert[];
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

export const useTrialOverview = (trialId: string | null) => {
  return useQuery({
    queryKey: ['trialOverview', trialId],
    queryFn: async (): Promise<TrialOverview> => {
      const response = await apiClient.get(`/dashboard/trial/${trialId}/overview`);
      return response as unknown as TrialOverview;
    },
    enabled: !!trialId,
  });
};

export const useCohortAEIncidence = (trialId: string | null, days = 30) => {
  return useQuery({
    queryKey: ['cohortAE', trialId, days],
    queryFn: async (): Promise<Record<string, unknown>> => {
      const response = await apiClient.get(`/analytics/trial/${trialId}/adverse-events`, {
        params: { days },
      });
      return response as unknown as Record<string, unknown>;
    },
    enabled: !!trialId,
  });
};
