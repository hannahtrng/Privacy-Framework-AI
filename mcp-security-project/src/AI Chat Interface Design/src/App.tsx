import { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { DefensesDashboard } from './components/DefensesDashboard';

export default function App() {
  const [mode, setMode] = useState<'allow' | 'redact' | 'block'>('redact');
  const [latestAnalysis, setLatestAnalysis] = useState<{
    detections: Array<{ type: string; value: string; severity: 'high' | 'medium' | 'low' }>;
    original: string;
    sanitized: string;
    action: 'ALLOWED' | 'REDACTED' | 'BLOCKED';
  } | null>(null);

  const handleAnalysisComplete = (result: any) => {
    if (result) {
      // Map API response to dashboard state
      const severity = (type: string): 'high' | 'medium' | 'low' => {
        if (type === 'SSN' || type === 'CREDIT_CARD') return 'high';
        if (type === 'PHONE' || type === 'EMAIL') return 'medium';
        return 'low';
      };

      setLatestAnalysis({
        detections: (result.detections || []).map((d: any) => ({
          type: d.kind || d.type,
          value: d.value,
          severity: severity(d.kind || d.type),
        })),
        original: result.original_prompt || '',
        sanitized: result.sanitized_prompt || '',
        action: result.action || 'ALLOWED',
      });
    }
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-[#2a2d35]">
      {/* Left Panel - Chat (70%) */}
      <div className="w-[70%] flex flex-col">
        <ChatPanel 
          onAnalysisComplete={handleAnalysisComplete}
          mode={mode}
        />
      </div>

      {/* Right Panel - Defense Dashboard (30%) */}
      <div className="w-[30%]">
        <DefensesDashboard 
          onModeChange={setMode}
          latestDetections={latestAnalysis?.detections}
          originalPrompt={latestAnalysis?.original}
          sanitizedPrompt={latestAnalysis?.sanitized}
          action={latestAnalysis?.action}
        />
      </div>
    </div>
  );
}