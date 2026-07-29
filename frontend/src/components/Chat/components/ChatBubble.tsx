import { Box, Text, HStack, Icon } from '@chakra-ui/react';
import { FaRobot, FaUser } from 'react-icons/fa';
import React from 'react';
import ReactMarkdown from 'react-markdown'; // For markdown rendering

interface SourceMeta {
  filename?: string;
  source_file?: string;
  [key: string]: any;
}

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  sources?: (string | SourceMeta)[];
}

const ChatBubble = ({ message }: { message: ChatMessage }) => {
  const isUser = message.sender === 'user';
  return (
    <HStack justify={isUser ? 'flex-end' : 'flex-start'}>
      {!isUser && <Icon as={FaRobot} color="blue.400" boxSize={5} />}
      <Box
        bg={isUser ? 'blue.100' : 'white'}
        color={isUser ? 'blue.900' : 'gray.800'}
        borderRadius="xl"
        px={4}
        py={2}
        maxW="70%"
        boxShadow="sm"
        alignSelf={isUser ? 'flex-end' : 'flex-start'}
        ml={isUser ? { base: 6, md: 16 } : 0}
        mr={!isUser ? { base: 6, md: 16 } : 0}
      >
        {/* Render markdown-formatted LLM answers */}
        <ReactMarkdown>{message.text}</ReactMarkdown>
        {message.sources && message.sources.length > 0 && (() => {
          // Deduplicate sources by their display string
          const uniqueSources = Array.from(
            new Set(
              message.sources.map((src: any) =>
                typeof src === 'string'
                  ? src
                  : src.filename || src.source_file || JSON.stringify(src)
              )
            )
          );
          return (
            <Text fontSize="xs" color="gray.500" mt={2}>
              Sources: {uniqueSources.join(', ')}
            </Text>
          );
        })()}

      </Box>
      {isUser && <Icon as={FaUser} color="blue.400" boxSize={5} />}
    </HStack>
  );
};

export default ChatBubble;
