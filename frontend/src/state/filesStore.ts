import { create } from 'zustand';

export interface FileMeta {
  id: string;
  project_id: string;
  filename: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface FilesState {
  files: FileMeta[];
  loading: boolean;
  error: string | null;
  setFiles: (files: FileMeta[]) => void;
  addFile: (file: FileMeta) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearFiles: () => void;
}

export const useFilesStore = create<FilesState>((set) => ({
  files: [],
  loading: false,
  error: null,
  setFiles: (files) => set({ files }),
  addFile: (file) => set((state) => ({ files: [...state.files, file] })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearFiles: () => set({ files: [] }),
}));
