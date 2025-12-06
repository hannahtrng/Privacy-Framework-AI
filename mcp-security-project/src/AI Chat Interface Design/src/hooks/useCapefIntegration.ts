import { useState, useCallback } from 'react';

export interface CapefResult {
  sanitized_prompt: string;
  llm_response: string;
  detections: Array<{
    kind: string;
    value: string;
    start: number;
    end: number;
  }>;
  action: 'allowed' | 'redacted' | 'blocked';
  mode: 'allow' | 'redact' | 'block';
}

export function useCapefIntegration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzePrompt = useCallback(
    async (prompt: string, mode: 'allow' | 'redact' | 'block' = 'redact'): Promise<CapefResult | null> => {
      setLoading(true);
      setError(null);

      try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('mode', mode);

        const response = await fetch('/api/analyze', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { analyzePrompt, loading, error };
}
