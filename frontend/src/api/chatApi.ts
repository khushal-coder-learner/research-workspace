import { apiClient } from './client';

export interface ChatOptions {
  question: string;
  projectId: string;
}

export interface ChatSource {
  text: string;
  score: number;
  page_number: number;
  filename: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

export async function sendChat({ question, projectId }: ChatOptions): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(`/projects/${projectId}/query`, {
    query: question,
  });
  return response.data;
}
