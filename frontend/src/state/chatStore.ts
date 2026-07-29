import { create } from 'zustand';

import type { ChatSource } from 'api/chatApi';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  sources?: ChatSource[];
}

interface ChatState {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  sendMessage: (msg: ChatMessage) => void;
  receiveMessage: (msg: ChatMessage) => void;
  clearChat: () => void;
  sendChat: (question: string, projectId: string) => Promise<void>;
}

import { sendChat as sendChatApi } from 'api/chatApi';

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  error: null,
  sendMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  receiveMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  clearChat: () => set({ messages: [] }),
  /**
   * Send a project-scoped question to the FastAPI query endpoint.
   */
  sendChat: async (
    question: string,
    projectId: string
  ) => {
    set({ loading: true, error: null });
    try {
      set((state) => ({ messages: [...state.messages, { sender: 'user', text: question }] }));
      const response = await sendChatApi({ question, projectId });
      set((state) => ({
        messages: [...state.messages, { sender: 'ai', text: response.answer, sources: response.sources }],
        loading: false,
        error: null,
      }));
    } catch (err: any) {
      set({ loading: false, error: typeof err === 'string' ? err : 'Chat failed' });
    }
  },
}));
