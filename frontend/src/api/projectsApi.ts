import { apiClient } from './client';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectInput {
  name: string;
  description?: string;
}

export async function fetchProjects(): Promise<Project[]> {
  const response = await apiClient.get<Project[]>('/projects');
  return response.data;
}

export async function createProject(input: CreateProjectInput): Promise<Project> {
  const response = await apiClient.post<Project>('/projects', input);
  return response.data;
}
