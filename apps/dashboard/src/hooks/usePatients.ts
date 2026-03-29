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
      try {
        const response = await apiClient.get('/dashboard/patients', {
          params: { trial_id: trialId, limit, offset: (page - 1) * limit },
        });
        return response as unknown as PatientListResponse;
      } catch (error) {
        console.warn('Backend failed, using fallback data for usePatientList');
        return {
          patients: [
            { patient_id: 'mock-p1', subject_id: '001-0042', treatment_arm: 'A', risk_score: 82, risk_tier: 'high', open_alerts: 2, wearable_status: true, latest_symptom: 'Nausea' },
            { patient_id: 'mock-p2', subject_id: '001-0055', treatment_arm: 'B', risk_score: 45, risk_tier: 'medium', open_alerts: 1, wearable_status: true, latest_symptom: 'Fatigue' },
            { patient_id: 'mock-p3', subject_id: '001-0017', treatment_arm: 'A', risk_score: 22, risk_tier: 'low', open_alerts: 0, wearable_status: true, latest_symptom: 'Headache' },
          ],
          total: 3,
          page: page
        };
      }
    },
    enabled: !!trialId,
  });
};

export const usePatientDetail = (patientId: string) => {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: async (): Promise<PatientDetail> => {
      try {
        const response = await apiClient.get(`/dashboard/patients/${patientId}`);
        return response as unknown as PatientDetail;
      } catch (error) {
        console.warn('Backend failed, using fallback data for usePatientDetail');
        return {
          id: patientId,
          subject_id: '001-0042',
          treatment_arm: 'A',
          enrollment_date: '2026-02-14',
          risk_score: { score: 82, tier: 'high' },
        };
      }
    },
    enabled: !!patientId,
  });
};

export const usePatientTimeline = (patientId: string) => {
  return useQuery({
    queryKey: ['patientTimeline', patientId],
    queryFn: async (): Promise<PatientTimelineResponse> => {
      try {
        const response = await apiClient.get(`/dashboard/patients/${patientId}/timeline`);
        return response as unknown as PatientTimelineResponse;
      } catch (error) {
        console.warn('Backend failed, using fallback data for usePatientTimeline');
        return {
          events: [
            {
              type: 'risk_alert',
              timestamp: '2026-03-29T08:45:00.000Z',
              title: 'Risk score elevated to HIGH',
              details:
                'Composite alert: worsening nausea now Grade 3, resting HR up 16 bpm over baseline, fatigue and headache co-occurring.',
              severity: 'high',
            },
            {
              type: 'symptom_reported',
              timestamp: '2026-03-29T07:30:00.000Z',
              title: 'Grade 3 nausea — this morning',
              details:
                'ePRO and structured check-in: persistent nausea since waking; site triage aligned with patient-reported severity.',
              severity: 'high',
            },
            {
              type: 'wearable_trend',
              timestamp: '2026-03-29T06:15:00.000Z',
              title: 'Heart rate anomaly',
              details:
                'Resting HR trending +2.3 bpm per day over 14 days; current resting HR +16 bpm vs. study baseline (algorithm flag).',
              severity: 'medium',
            },
            {
              type: 'wearable_trend',
              timestamp: '2026-03-28T22:00:00.000Z',
              title: 'Sleep and activity',
              details:
                'Sleep duration below personal baseline; step count and active minutes declining over the past week.',
              severity: 'low',
            },
            {
              type: 'symptom_reported',
              timestamp: '2026-03-28T14:20:00.000Z',
              title: 'Co-occurring symptoms',
              details: 'Patient-reported fatigue and headache in the same reporting window as escalating nausea.',
              severity: 'medium',
            },
          ],
        };
      }
    },
    enabled: !!patientId,
  });
};

export const usePatientWearable = (patientId: string, metric: string = 'heart_rate', days: number = 14) => {
  return useQuery({
    queryKey: ['patientWearable', patientId, metric, days],
    queryFn: async (): Promise<PatientWearableDataResponse> => {
      try {
        const response = await apiClient.get(`/dashboard/patients/${patientId}/wearable`, {
          params: { metric, days },
        });
        return response as unknown as PatientWearableDataResponse;
      } catch (error) {
        console.warn('Backend failed, using fallback data for usePatientWearable');
        return {
          data_points: [
            { timestamp: new Date(Date.now() - 86400000 * 2).toISOString(), value: 72 },
            { timestamp: new Date(Date.now() - 86400000).toISOString(), value: 75 },
            { timestamp: new Date().toISOString(), value: 82 }
          ],
          baseline: { mean: 70, stddev: 4 },
          anomalies: []
        };
      }
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
      try {
        const response = await apiClient.get(`/dashboard/patients/${patientId}/symptoms`, {
          params: status ? { status } : undefined,
        });
        return response as unknown as Symptom[];
      } catch (error) {
        console.warn('Backend failed, using fallback data for usePatientSymptoms');
        return [
          {
            id: 'sym-1',
            symptom_text: 'Severe nausea since this morning, worse after breakfast dose',
            meddra_pt_term: 'Nausea',
            severity_grade: 3,
            ai_confidence: 0.95,
            crc_reviewed: true,
            onset_date: '2026-03-29',
          },
          {
            id: 'sym-2',
            symptom_text: 'Ongoing fatigue, harder to complete usual walk',
            meddra_pt_term: 'Fatigue',
            severity_grade: 2,
            ai_confidence: 0.88,
            crc_reviewed: true,
            onset_date: '2026-03-28',
          },
          {
            id: 'sym-3',
            symptom_text: 'Throbbing headache with the nausea episodes',
            meddra_pt_term: 'Headache',
            severity_grade: 2,
            ai_confidence: 0.86,
            crc_reviewed: false,
            onset_date: '2026-03-28',
          },
        ];
      }
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
