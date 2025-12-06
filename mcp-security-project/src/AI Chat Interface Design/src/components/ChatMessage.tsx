interface ChatMessageProps {
  content: string;
  isUser: boolean;
  timestamp: string;
}

export function ChatMessage({ content, isUser, timestamp }: ChatMessageProps) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className="flex flex-col max-w-[75%]">
        <div
          className={`px-4 py-3 rounded-xl shadow-sm ${
            isUser
              ? 'bg-[#3A7AFE] text-white rounded-tr-sm'
              : 'bg-[#F3F5F8] text-gray-800 rounded-tl-sm'
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
        <span className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'} px-1`}>
          {timestamp}
        </span>
      </div>
    </div>
  );
}
