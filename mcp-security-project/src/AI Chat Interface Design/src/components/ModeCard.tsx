import { Settings } from 'lucide-react';

type Mode = 'allow' | 'redact' | 'block';

interface ModeCardProps {
  selectedMode: Mode;
  onModeChange?: (mode: Mode) => void;
}

export function ModeCard({ selectedMode, onModeChange }: ModeCardProps) {
  const modes: { value: Mode; label: string; color: string }[] = [
    { value: 'allow', label: 'Allow', color: 'bg-green-500' },
    { value: 'redact', label: 'Redact', color: 'bg-orange-500' },
    { value: 'block', label: 'Block', color: 'bg-red-500' },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Settings className="w-5 h-5 text-[#3A7AFE]" />
        <h3 className="text-gray-900">Mode Selected</h3>
      </div>
      <div className="flex gap-2">
        {modes.map((mode) => (
          <button
            key={mode.value}
            onClick={() => onModeChange?.(mode.value)}
            className={`flex-1 px-3 py-2 rounded-lg transition-all ${
              selectedMode === mode.value
                ? `${mode.color} text-white shadow-md`
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {mode.label}
          </button>
        ))}
      </div>
    </div>
  );
}
