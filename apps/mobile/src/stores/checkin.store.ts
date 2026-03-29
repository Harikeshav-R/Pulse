import { create } from 'zustand';
import { api } from '../services/api';

export interface ChatMessage {
  id: string;
  role: 'ai' | 'patient';
  text: string;
  time: string;
}

interface CheckinState {
  sessionId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  
  startCheckin: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  resetCheckin: () => void;
}

export const useCheckinStore = create<CheckinState>((set, get) => ({
  sessionId: null,
  messages: [],
  isLoading: false,
  error: null,

  resetCheckin: () => set({ sessionId: null, messages: [], isLoading: false, error: null }),

  startCheckin: async () => {
    try {
      set({ isLoading: true, error: null, messages: [] });
      
      const response = await api.post('/checkins/start', {
        session_type: 'scheduled',
        modality: 'text',
      });
      
      const { session_id, message } = response.data;
      
      const now = new Date();
      const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      const firstMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'ai',
        text: message,
        time: timeString,
      };

      set({
        sessionId: session_id,
        messages: [firstMessage],
        isLoading: false,
      });
    } catch (error: any) {
      console.error('Failed to start check-in:', error.response?.data || error.message);
      set({
        error: 'Could not connect to AI assistant.',
        isLoading: false,
      });
    }
  },

  sendMessage: async (content: string) => {
    const { sessionId, messages } = get();
    if (!sessionId) return;

    try {
      set({ isLoading: true, error: null });
      
      const now = new Date();
      const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      // Optimistically add patient message
      const patientMessage: ChatMessage = {
        id: Date.now().toString() + '-p',
        role: 'patient',
        text: content,
        time: timeString,
      };
      
      set({ messages: [...messages, patientMessage] });

      const response = await api.post(`/checkins/${sessionId}/message`, {
        content: content,
        message_type: 'text',
      });

      const { message } = response.data;

      const aiResponseTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      const aiMessage: ChatMessage = {
        id: Date.now().toString() + '-ai',
        role: 'ai',
        text: message,
        time: aiResponseTime,
      };

      set({ 
        messages: [...get().messages, aiMessage],
        isLoading: false 
      });

    } catch (error: any) {
      console.error('Failed to send message:', error.response?.data || error.message);
      set({
        error: 'Message failed to send. Please try again.',
        isLoading: false,
      });
    }
  },
}));
