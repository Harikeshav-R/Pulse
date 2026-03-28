import axios from 'axios';

// Mock authentication token for hackathon demo (James Smith - CRC)
const DEMO_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC0wMDAwLTQwMDAtODAwMC0wMDAwMDAwMDAwMjEiLCJzdGFmZl9pZCI6ImExYjJjM2Q0LTAwMDAtNDAwMC04MDAwLTAwMDAwMDAwMDAyMSIsImVtYWlsIjoiamFtZXMuc21pdGhAbWVtb3JpYWwub3JnIiwicm9sZSI6ImNyYyIsInNpdGVzIjpbImExYjJjM2Q0LTAwMDAtNDAwMC04MDAwLTAwMDAwMDAwMDAxMCJdLCJleHAiOjE3NzQ4Mjg3MjN9.IUpHSzTkcA44iAg1MN6BKXMuTLtELlI1RFQ-KWDOHTs';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${DEMO_TOKEN}`,
  },
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
