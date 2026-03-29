import { api } from './api';

export interface VoiceSession {
  sessionId: string;
  roomName: string;
  livekitUrl: string;
  token: string;
}

export async function startVoiceSession(): Promise<VoiceSession> {
  const response = await api.post('/voice/start');
  return {
    sessionId: response.data.session_id,
    roomName: response.data.room_name,
    livekitUrl: response.data.livekit_url,
    token: response.data.token,
  };
}
