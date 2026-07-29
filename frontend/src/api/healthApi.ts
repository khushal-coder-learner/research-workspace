import { apiClient } from './client';

export async function fetchHealth() {
  const response = await apiClient.get<{ status: string }>('/health');
  return response.data;
}
