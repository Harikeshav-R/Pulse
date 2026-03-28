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

export const useAlerts = (status?: string, severity?: string, page = 1) => {
  return useQuery({
    queryKey: ['alerts', status, severity, page],
    queryFn: async (): Promise<{ alerts: Alert[]; total: number }> => {
      const response = await apiClient.get('/dashboard/alerts', {
        params: { status, severity, page },
      });
      return response as any;
    },
  });
};

export const useUpdateAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ alertId, payload }: { alertId: string, payload: any }) => {
      const response = await apiClient.put(`/dashboard/alerts/${alertId}`, payload);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });
};

export const useTrialOverview = (trialId: string | null) => {
  return useQuery({
    queryKey: ['trialOverview', trialId],
    queryFn: async () => {
      const response = await apiClient.get(`/dashboard/trial/${trialId}/overview`);
      return response as any;
    },
    enabled: !!trialId,
  });
};

export const useCohortAEIncidence = (trialId: string | null, days = 30) => {
  return useQuery({
    queryKey: ['cohortAE', trialId, days],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/cohort/ae-incidence', {
        params: { trial_id: trialId, days },
      });
      return response as any;
    },
    enabled: !!trialId,
  });
};
