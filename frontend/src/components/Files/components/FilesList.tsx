import React from 'react';
import { VStack, Text, Spinner } from '@chakra-ui/react';
import FilePill from './FilePill';
import { FileMeta } from 'state/filesStore';

interface FilesListProps {
  files: FileMeta[];
  loading: boolean;
}

const FilesList: React.FC<FilesListProps> = ({ files, loading }) => {
  if (loading) {
    return <Spinner size="md" mx="auto" my={6} />;
  }
  if (!Array.isArray(files) || files.length === 0) {
    return <Text color="gray.400">No files uploaded yet.</Text>;
  }
  return (
    <VStack align="stretch" spacing={2}>
      {files.map((file) => (
        <FilePill
          key={file.id}
          file={file}
        />
      ))}
    </VStack>
  );
};

export default FilesList;
