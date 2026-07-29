import { useCallback, useRef } from 'react';
import { useFilesStore } from 'state/filesStore';
import { uploadFile } from 'api/filesApi';
import { useProjectsStore } from 'state/projectsStore';
import { getApiError } from 'api/client';
import { useToast } from '@chakra-ui/react';

const SUPPORTED_EXTENSIONS = ['pdf'];
const MAX_SIZE_MB = 20;

export function useFileUpload() {
  const addFile = useFilesStore((state) => state.addFile);
  const setLoading = useFilesStore((state) => state.setLoading);
  const setError = useFilesStore((state) => state.setError);
  const loading = useFilesStore((state) => state.loading);
  const activeProjectId = useProjectsStore((state) => state.activeProjectId);
  const toast = useToast();
  const uploading = useRef(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      if (!file.name) {
        setError('File name is missing.');
        continue;
      }
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (!activeProjectId) {
        setError('Create or select a project before uploading a document.');
        continue;
      }
      if (!ext || !SUPPORTED_EXTENSIONS.includes(ext)) {
        toast({ title: 'Unsupported file type', status: 'error', duration: 4000 });
        continue;
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        toast({ title: 'File too large', status: 'error', duration: 4000 });
        continue;
      }
      setLoading(true);
      uploading.current = true;
      try {
        const uploaded = await uploadFile(activeProjectId, file);
        addFile(uploaded);
        toast({ title: 'File uploaded', status: 'success', duration: 2000 });
      } catch (error: any) {
        const message = getApiError(error, 'Upload failed');
        setError(message);
        toast({ title: 'Upload failed', description: message, status: 'error', duration: 4000 });
      } finally {
        setLoading(false);
        uploading.current = false;
      }
    }
  }, [activeProjectId, addFile, setLoading, setError, toast]);

  return { onDrop, loading, uploading };
}
