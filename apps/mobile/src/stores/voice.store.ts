import { create } from 'zustand';
import { startVoiceSession, VoiceSession } from '../services/livekit';

export interface TranscriptEntry {
  id: string;
  role: 'ai' | 'patient';
  text: string;
  timestamp: number;
}

export type AgentState = 'idle' | 'connecting' | 'listening' | 'speaking';

interface VoiceState {
  isConnecting: boolean;
  isConnected: boolean;
  isMuted: boolean;
  agentState: AgentState;
  transcript: TranscriptEntry[];
  sessionId: string | null;
  error: string | null;

  startSession: () => Promise<VoiceSession>;
  setConnected: (connected: boolean) => void;
  setAgentState: (state: AgentState) => void;
  toggleMute: () => void;
  addTranscriptEntry: (role: 'ai' | 'patient', text: string) => void;
  endSession: () => void;
  setError: (error: string | null) => void;
}

export const useVoiceStore = create<VoiceState>((set, get) => ({
  isConnecting: false,
  isConnected: false,
  isMuted: false,
  agentState: 'idle',
  transcript: [],
  sessionId: null,
  error: null,

  startSession: async () => {
    set({ isConnecting: true, error: null, transcript: [], agentState: 'connecting' });
    try {
      const session = await startVoiceSession();
      set({ sessionId: session.sessionId, isConnecting: false });
      return session;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to start voice session';
      set({ error: message, isConnecting: false, agentState: 'idle' });
      throw err;
    }
  },

  setConnected: (connected) =>
    set({ isConnected: connected, agentState: connected ? 'listening' : 'idle' }),

  setAgentState: (agentState) => set({ agentState }),

  toggleMute: () => set((s) => ({ isMuted: !s.isMuted })),

  addTranscriptEntry: (role, text) =>
    set((s) => ({
      transcript: [
        ...s.transcript,
        {
          id: `${Date.now()}-${role}`,
          role,
          text,
          timestamp: Date.now(),
        },
      ],
    })),

  endSession: () =>
    set({
      isConnecting: false,
      isConnected: false,
      isMuted: false,
      agentState: 'idle',
      sessionId: null,
      error: null,
    }),

  setError: (error) => set({ error }),
}));
