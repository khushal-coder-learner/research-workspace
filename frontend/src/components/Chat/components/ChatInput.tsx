import React, { useState, useRef } from 'react';
import { HStack, Input, IconButton, Spinner, useToast } from '@chakra-ui/react';
import { FaPaperPlane } from 'react-icons/fa';
import { useChatStore } from 'state/chatStore';
import { useFilesStore } from 'state/filesStore';
import { useProjectsStore } from 'state/projectsStore';

// Chat input is disabled if no files are uploaded
const ChatInput = () => {
  const [value, setValue] = useState('');

  const sendChat = useChatStore((state) => state.sendChat);
  const loading = useChatStore((state) => state.loading);
  const error = useChatStore((state) => state.error);
  const toast = useToast();
  const files = useFilesStore((state) => state.files);
  const chatDisabled = !files || files.length === 0;
  const activeProjectId = useProjectsStore((state) => state.activeProjectId);

  const handleSend = async () => {
    if (!value.trim() || loading || chatDisabled) return; // Disable send if no files are uploaded
    if (!activeProjectId) return;
    await sendChat(value, activeProjectId);
    setValue('');
  };

  // Show error toast if error changes
  React.useEffect(() => {
    if (error) {
      toast({
        title: 'Chat Error',
        description: error,
        status: 'error',
        duration: 4000,
        isClosable: true,
        position: 'top',
      });
    }
  }, [error, toast]);

  return (
    <HStack spacing={2}>

      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={chatDisabled ? 'Please upload a file to start chatting' : 'Type your message...'}
        isDisabled={chatDisabled || loading}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSend();
        }}
      />
      <IconButton
        aria-label="Send"
        icon={loading ? <Spinner size="sm" /> : <FaPaperPlane />}
        onClick={handleSend}
        isDisabled={chatDisabled || loading || !value.trim()}
        colorScheme="blue"
      />
    </HStack>
  );
};

export default ChatInput;
