import React, { useEffect, useState } from 'react';
import { Box, Button, Divider, Heading, HStack, Input, Select, Text, useToast } from '@chakra-ui/react';
import { useFilesStore } from 'state/filesStore';
import { useProjectsStore } from 'state/projectsStore';
import { fetchFiles } from 'api/filesApi';
import { createProject, fetchProjects } from 'api/projectsApi';
import { getApiError } from 'api/client';
import { FileUpload, FilesList, FileErrorAlert } from 'components/Files';

const FilesSidebar = () => {
  const files = useFilesStore((state) => state.files);
  const setFiles = useFilesStore((state) => state.setFiles);
  const loading = useFilesStore((state) => state.loading);
  const setLoading = useFilesStore((state) => state.setLoading);
  const error = useFilesStore((state) => state.error);
  const setError = useFilesStore((state) => state.setError);
  const projects = useProjectsStore((state) => state.projects);
  const activeProjectId = useProjectsStore((state) => state.activeProjectId);
  const setProjects = useProjectsStore((state) => state.setProjects);
  const setActiveProjectId = useProjectsStore((state) => state.setActiveProjectId);
  const [newProjectName, setNewProjectName] = useState('');
  const [creatingProject, setCreatingProject] = useState(false);
  const toast = useToast();

  useEffect(() => {
    fetchProjects().then(setProjects).catch((requestError) => setError(getApiError(requestError, 'Failed to fetch projects')));
  }, [setProjects, setError]);

  useEffect(() => {
    if (!activeProjectId) {
      setFiles([]);
      return;
    }
    setLoading(true);
    fetchFiles(activeProjectId)
      .then((documents) => { setFiles(documents); setError(null); })
      .catch((requestError) => setError(getApiError(requestError, 'Failed to fetch documents')))
      .finally(() => setLoading(false));
  }, [activeProjectId, setFiles, setLoading, setError]);

  const handleCreateProject = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!newProjectName.trim()) return;
    setCreatingProject(true);
    try {
      const project = await createProject({ name: newProjectName.trim() });
      setProjects([...projects, project]);
      setActiveProjectId(project.id);
      setNewProjectName('');
      toast({ title: 'Project created', status: 'success', duration: 2000 });
    } catch (requestError) {
      const message = getApiError(requestError, 'Project creation failed');
      setError(message);
      toast({ title: 'Project creation failed', description: message, status: 'error', duration: 4000 });
    } finally {
      setCreatingProject(false);
    }
  };

  return (
    <Box display="flex" flexDirection="column" h={{ base: '100dvh', md: '100vh' }} minW={{ base: '100vw', md: '320px' }} maxW={{ base: '100vw', md: '400px' }} p={0} bg="white" boxShadow={{ base: 'none', md: 'md' }}>
      <Box p={{ base: 3, md: 4 }} pb={0}>
        <Heading size="md" mb={4} fontSize={{ base: 'lg', md: 'xl' }}>Research Workspace</Heading>
        <Text fontSize="sm" color="gray.500" mb={2}>Project</Text>
        <Select value={activeProjectId || ''} onChange={(event) => setActiveProjectId(event.target.value || null)} mb={2} placeholder="Select a project">
          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
        </Select>
        <HStack as="form" onSubmit={handleCreateProject} mb={4}>
          <Input value={newProjectName} onChange={(event) => setNewProjectName(event.target.value)} placeholder="New project name" size="sm" />
          <Button type="submit" size="sm" colorScheme="blue" isLoading={creatingProject}>Create</Button>
        </HStack>
        <FileUpload />
        <Divider my={4} />
        <FileErrorAlert error={error} />
      </Box>
      <Box flex={1} px={{ base: 2, md: 4 }} overflowY="auto" minH={0}>
        {!activeProjectId && <Text color="gray.400">Select or create a project to view documents.</Text>}
        {activeProjectId && <FilesList files={files} loading={loading} />}
      </Box>
    </Box>
  );
};

export default FilesSidebar;
