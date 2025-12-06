import { useState, useEffect } from 'react';
import { PIIDetectionCard } from './PIIDetectionCard';
import { SanitizedPromptCard } from './SanitizedPromptCard';
import { ModeCard } from './ModeCard';
import { ActionCard } from './ActionCard';

type Mode = 'allow' | 'redact' | 'block';
type Action = 'ALLOWED' | 'REDACTED' | 'BLOCKED';

interface DefensesDashboardProps {
  onModeChange?: (mode: Mode) => void;
  latestDetections?: Array<{ type: string; value: string; severity: 'high' | 'medium' | 'low' }>;
  originalPrompt?: string;
  sanitizedPrompt?: string;
  action?: Action;
}

export function DefensesDashboard({
  onModeChange,
  latestDetections = [],
  originalPrompt = '',
  sanitizedPrompt = '',
  action = 'REDACTED',
}: DefensesDashboardProps) {
  const [mode, setMode] = useState<Mode>('redact');

  const handleModeChange = (newMode: Mode) => {
    setMode(newMode);
    onModeChange?.(newMode);
  };

  return (
    <div className="h-full bg-[#F3F5F8] border-l border-gray-200 overflow-y-auto">
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-gray-900">Privacy Defenses</h2>
          <p className="text-sm text-gray-500 mt-1">Real-time PII monitoring & protection</p>
        </div>

        <div className="space-y-4">
          <PIIDetectionCard items={latestDetections.length > 0 ? latestDetections : []} />
          {originalPrompt && sanitizedPrompt && (
            <SanitizedPromptCard original={originalPrompt} sanitized={sanitizedPrompt} />
          )}
          <ModeCard selectedMode={mode} onModeChange={handleModeChange} />
          <ActionCard action={action} />
        </div>

        {/* Info Panel */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-[#3A7AFE] mt-2"></div>
            <div>
              <h3 className="text-blue-900 mb-1">Active Protection</h3>
              <p className="text-xs text-blue-700">
                CAPEF Privacy Shield is actively monitoring and protecting your conversations from PII leakage.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
