import { apiClient } from './client';

export type DocumentStatus = 'UPLOADED' | 'QUEUED' | 'QUEUE_FAILED' | 'PROCESSING' | 'INDEXED' | 'FAILED';

export interface DocumentMeta {
  id: string;
  project_id: string;
  filename: string;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
}

export async function uploadFile(projectId: string, file: File): Promise<DocumentMeta> {
  const formData = new FormData();
  formData.append('project_id', projectId);
  formData.append('uploaded_file', file);
  const response = await apiClient.post<DocumentMeta>('/documents/upload', formData);
  return response.data;
}

export async function fetchFiles(projectId: string): Promise<DocumentMeta[]> {
  const response = await apiClient.get<DocumentMeta[]>(`/projects/${projectId}/documents`);
  return response.data;
}
