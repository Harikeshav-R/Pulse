import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';

// --- Types ---
export interface PatientListItem {
  patient_id: string;
  subject_id: string;
  treatment_arm?: string;
  risk_score?: number;
  risk_tier?: string;
  last_checkin_at?: string;
  open_alerts: number;
  latest_symptom?: string;
  wearable_status: boolean;
}

export interface PatientListResponse {
  patients: PatientListItem[];
  total: number;
  page: number;
}

export interface PatientTimelineEvent {
  type: string;
  timestamp: string;
  title: string;
  details: string;
  severity?: string;
}

export interface PatientTimelineResponse {
  events: PatientTimelineEvent[];
}

export interface PatientWearableDataResponse {
  data_points: { timestamp: string; value: number }[];
  baseline?: { mean: number; stddev: number };
  anomalies: unknown[];
}

export interface CheckinMessageItem {
  id: string;
  role: string;
  content: string;
  message_type: string;
  created_at: string;
}

export interface CheckinSessionItem {
  session_id: string;
  modality: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  messages: CheckinMessageItem[];
}

export interface PatientCheckinsResponse {
  sessions: CheckinSessionItem[];
  total: number;
}

export interface Symptom {
  id: string;
  symptom_text: string;
  meddra_pt_term?: string;
  severity_grade?: number;
  ai_confidence?: number;
  crc_reviewed: boolean;
  onset_date?: string;
}

export interface PatientDetail {
  id: string;
  subject_id: string;
  treatment_arm?: string;
  enrollment_date: string;
  risk_score?: {
    score: number;
    tier: string;
  };
  [key: string]: unknown;
}

// --- Hooks ---

export const usePatientList = (trialId: string, page = 1, limit = 20) => {
  return useQuery({
    queryKey: ['patients', trialId, page, limit],
    queryFn: async (): Promise<PatientListResponse> => {
      const response = await apiClient.get('/dashboard/patients', {
        params: { trial_id: trialId, limit, offset: (page - 1) * limit },
      });
      return response as unknown as PatientListResponse;
    },
    enabled: !!trialId,
  });
};

export const usePatientDetail = (patientId: string) => {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: async (): Promise<PatientDetail> => {
      const response = await apiClient.get(`/dashboard/patients/${patientId}`);
      return response as unknown as PatientDetail;
    },
    enabled: !!patientId,
  });
};

export const usePatientTimeline = (patientId: string) => {
  return useQuery({
    queryKey: ['patientTimeline', patientId],
    queryFn: async (): Promise<PatientTimelineResponse> => {
      const response = await apiClient.get(`/dashboard/patients/${patientId}/timeline`);
      return response as unknown as PatientTimelineResponse;
    },
    enabled: !!patientId,
  });
};

export const usePatientWearable = (patientId: string, metric: string = 'heart_rate', days: number = 14) => {
  return useQuery({
    queryKey: ['patientWearable', patientId, metric, days],
    queryFn: async (): Promise<PatientWearableDataResponse> => {
      const response = await apiClient.get(`/dashboard/patients/${patientId}/wearable`, {
        params: { metric, days },
      });
      return response as unknown as PatientWearableDataResponse;
    },
    enabled: !!patientId,
  });
};

export const usePatientCheckins = (patientId: string) => {
  return useQuery({
    queryKey: ['patientCheckins', patientId],
    queryFn: async (): Promise<PatientCheckinsResponse> => {
      const response = await apiClient.get(`/dashboard/patients/${patientId}/checkins`);
      return response as unknown as PatientCheckinsResponse;
    },
    enabled: !!patientId,
  });
};

export const usePatientSymptoms = (patientId: string, status?: string) => {
  return useQuery({
    queryKey: ['patientSymptoms', patientId, status],
    queryFn: async (): Promise<Symptom[]> => {
      const response = await apiClient.get(`/dashboard/patients/${patientId}/symptoms`, {
        params: status ? { status } : undefined,
      });
      return response as unknown as Symptom[];
    },
    enabled: !!patientId,
  });
};

export const useReviewSymptom = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ symptomId, payload }: { symptomId: string, payload: unknown }) => {
      const response = await apiClient.post(`/dashboard/symptoms/${symptomId}/review`, payload);
      return response;
    },
    onSuccess: () => {
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['patientSymptoms'] });
    },
  });
};
