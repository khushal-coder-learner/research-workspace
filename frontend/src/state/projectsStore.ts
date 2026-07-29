import { create } from 'zustand';
import { Project } from 'api/projectsApi';

interface ProjectsState {
  projects: Project[];
  activeProjectId: string | null;
  loading: boolean;
  error: string | null;
  setProjects: (projects: Project[]) => void;
  setActiveProjectId: (projectId: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addProject: (project: Project) => void;
}

export const useProjectsStore = create<ProjectsState>((set) => ({
  projects: [], activeProjectId: null, loading: false, error: null,
  setProjects: (projects) => set((state) => ({
    projects,
    activeProjectId: state.activeProjectId && projects.some((project) => project.id === state.activeProjectId) ? state.activeProjectId : projects[0]?.id || null,
  })),
  setActiveProjectId: (activeProjectId) => set({ activeProjectId }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  addProject: (project) => set({ projects: [project], activeProjectId: project.id }),
}));
