import React, { useRef, useEffect } from 'react';
import { Box, VStack, Spinner, Flex, Alert, AlertIcon } from '@chakra-ui/react';
import { useChatStore } from 'state/chatStore';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';
import { useFilesStore } from 'state/filesStore';

// Show friendly message if no files are uploaded
const ChatArea = () => {
  const messages = useChatStore((state) => state.messages);
  const files = useFilesStore((state) => state.files);
  const noFiles = !files || files.length === 0;
  const loading = useChatStore((state) => state.loading);
  const error = useChatStore((state) => state.error);

  // Ref for the scrollable chat area
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when messages change
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  return (
    <Flex direction="column" h="100%" minH={0} flex="1" px={{ base: 2, sm: 4, md: 8 }} pb={{ base: 4, md: 6 }}>
      <Box flex="1" minH={0}>
        {noFiles ? (
          <Alert status="info" borderRadius="md" maxW="sm" mt={6} mx="auto">
            <AlertIcon />
            Please upload a file to start chatting.
          </Alert>
        ) : (
          <>
            {error && (
              <Box mb={2} p={2} bg="red.50" color="red.600" borderRadius="md" fontSize="sm">
                {error}
              </Box>
            )}
            {/* Scrollable chat area */}
            <Box
              ref={chatScrollRef}
              h={{ base: '48vh', md: '60vh' }}
              maxH={{ base: '48vh', md: '60vh' }}
              overflowY="auto"
              w="100%"
              px={1}
              tabIndex={0}
              aria-label="Chat messages"
              bg="white"
              borderRadius="md"
              boxShadow="xs"
              _focus={{ outline: '2px solid #3182ce' }}
            >
              <VStack spacing={3} align="stretch" w="100%">
                {messages.map((msg, idx) => (
                  <ChatBubble key={idx} message={msg} />
                ))}
                {loading && (
                  <Box alignSelf="flex-start" p={2}>
                    <Spinner size="sm" color="blue.400" />
                  </Box>
                )}
              </VStack>
            </Box>
          </>
        )}
      </Box>
      <Box
        position="sticky"
        bottom={{ base: 12, md: 24 }}
        p={2}
        borderTop="1px solid #eee"
        zIndex={1}
        bg="white"
        boxShadow="sm"
        borderRadius="lg"
      >
        <ChatInput />
      </Box>
    </Flex>
  );
};

export default ChatArea;
