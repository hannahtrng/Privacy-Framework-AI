import { useState } from 'react';
import { Send } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { useCapefIntegration } from '../hooks/useCapefIntegration';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: string;
  piiDetections?: Array<{ kind: string; value: string }>;
}

interface ChatPanelProps {
  onAnalysisComplete?: (result: any) => void;
  mode?: 'allow' | 'redact' | 'block';
}

export function ChatPanel({ onAnalysisComplete, mode = 'redact' }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! How can I help you today?',
      isUser: false,
      timestamp: '10:30 AM',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const { analyzePrompt, loading } = useCapefIntegration();

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, userMessage]);
    
    const promptText = inputValue;
    setInputValue('');

    // Call CAPEF backend
    const result = await analyzePrompt(promptText, mode);

    // Notify parent component of analysis result for dashboard update
    if (onAnalysisComplete) {
      onAnalysisComplete(result);
    }

    if (result) {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: result.llm_response || 'Processing complete.',
        isUser: false,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        piiDetections: result.detections?.map(d => ({ kind: d.kind, value: d.value })),
      };
      setMessages(prev => [...prev, aiResponse]);
    } else {
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Error processing your request. Please try again.',
        isUser: false,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorResponse]);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h1 className="text-gray-900">CAPEF Privacy Shield</h1>
        <p className="text-sm text-gray-500 mt-1">AI Assistant with Privacy Protection</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            content={message.content}
            isUser={message.isUser}
            timestamp={message.timestamp}
          />
        ))}
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-gray-200 bg-white">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Type your message..."
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#3A7AFE] focus:border-transparent resize-none"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
              disabled={loading}
            />
          </div>
          <button
            onClick={handleSend}
            className="px-4 py-3 bg-[#3A7AFE] text-white rounded-xl hover:bg-[#2d63e0] transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!inputValue.trim() || loading}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
