import axios from 'axios';
import { useAuthStore } from '../stores/auth.store';

// For iOS Simulator, localhost correctly points to the Mac's localhost.
// If testing on a physical device or Android emulator later, this might need
// to be changed to the local network IP (e.g., 192.168.x.x) or 10.0.2.2.
const BASE_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Configure interceptor to inject the JWT Bearer token
api.interceptors.request.use(
  (config) => {
    // We can't use React hooks outside comps. Zustand's API allows `.getState()`.
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
