import axios from 'axios';
import type { Node, Session, SessionSummary, NetworkData, ExtractionConfig } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Sessions
  async getSessions(): Promise<Session[]> {
    const response = await api.get('/sessions');
    return response.data;
  },

  async getSession(sessionId: number): Promise<SessionSummary> {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  async getSessionNodes(sessionId: number): Promise<Node[]> {
    const response = await api.get(`/sessions/${sessionId}/nodes`);
    return response.data;
  },

  // Network data
  async getNetworkData(sessionId: number): Promise<NetworkData> {
    const response = await api.get(`/sessions/${sessionId}/network`);
    return response.data;
  },

  // Node expansion
  async expandNode(sessionId: number, nodeId: string): Promise<NetworkData> {
    const response = await api.post(`/sessions/${sessionId}/nodes/${nodeId}/expand`);
    return response.data;
  },

  // Extraction
  async startExtraction(config: ExtractionConfig): Promise<{ session_id: number }> {
    const response = await api.post('/extract', config);
    return response.data;
  },

  async stopExtraction(sessionId: number): Promise<void> {
    await api.post(`/extract/${sessionId}/stop`);
  },

  // Status
  async getExtractionStatus(sessionId: number): Promise<{ status: string; progress: number }> {
    const response = await api.get(`/extract/${sessionId}/status`);
    return response.data;
  },
};

export default apiService; 