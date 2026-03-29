import { create } from 'zustand';
import { api } from '../services/api';

// Fixed Patient ID for Demo Patient (David Thompson)
// From db/seed.sql
const DEMO_PATIENT_ID = 'a1b2c3d4-0000-4000-8000-000000000103';

interface AuthState {
  token: string | null;
  patientId: string | null;
  isLoading: boolean;
  error: string | null;
  loginDemoPatient: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  patientId: null,
  isLoading: false,
  error: null,

  loginDemoPatient: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await api.post('/auth/patient/demo-login', {
        patient_id: DEMO_PATIENT_ID,
      });
      
      const { access_token, patient_id } = response.data;
      
      set({
        token: access_token,
        patientId: patient_id,
        isLoading: false,
      });
      console.log('Successfully logged in demo patient');
    } catch (error: any) {
      console.error('Demo login failed:', error.response?.data || error.message);
      set({
        error: 'Failed to login demo patient. Is the backend running?',
        isLoading: false,
      });
    }
  },
}));
