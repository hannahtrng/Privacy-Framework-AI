import { Lock } from 'lucide-react';

interface SanitizedPromptCardProps {
  original: string;
  sanitized: string;
}

export function SanitizedPromptCard({ original, sanitized }: SanitizedPromptCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Lock className="w-5 h-5 text-[#3A7AFE]" />
        <h3 className="text-gray-900">Sanitized Prompt</h3>
      </div>
      <div className="bg-[#F3F5F8] rounded-lg p-3 border border-gray-200">
        <code className="text-xs text-gray-700 whitespace-pre-wrap break-words font-mono">
          {sanitized}
        </code>
      </div>
      {original !== sanitized && (
        <div className="mt-2">
          <p className="text-xs text-gray-500">Original prompt was modified</p>
        </div>
      )}
    </div>
  );
}
