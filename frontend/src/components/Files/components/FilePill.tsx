import React from 'react';
import { HStack, Icon, Text, Box } from '@chakra-ui/react';
import { FaFileAlt } from 'react-icons/fa';
import { FileMeta } from 'state/filesStore';

const getFileExt = (filename?: string) => {
  if (!filename) return '';
  const parts = filename.split('.');
  return parts.length > 1 ? parts.pop()?.toLowerCase() : '';
};

type FilePillProps = {
  file: FileMeta;
};

const FilePill = ({ file }: FilePillProps) => (
  <HStack spacing={2} px={3} py={2} borderRadius="full" bg="gray.100" _hover={{ bg: 'blue.50' }}>
    <Icon as={FaFileAlt} color="blue.400" />
    <Text fontSize="sm" isTruncated>{file.filename}</Text>
    <Box as="span" fontSize="xs" color="gray.500">{getFileExt(file.filename)}</Box>
    <Box as="span" fontSize="xs" color={file.status === 'INDEXED' ? 'green.500' : 'orange.500'}>
      {file.status}
    </Box>
  </HStack>
);

export default FilePill;
