import { Shield } from 'lucide-react';

interface PIIItem {
  type: string;
  value: string;
  severity: 'high' | 'medium' | 'low';
}

interface PIIDetectionCardProps {
  items: PIIItem[];
}

export function PIIDetectionCard({ items }: PIIDetectionCardProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'low':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Shield className="w-5 h-5 text-[#3A7AFE]" />
        <h3 className="text-gray-900">Detected PII</h3>
      </div>
      <div className="space-y-2">
        {items.length === 0 ? (
          <p className="text-sm text-gray-500">No PII detected</p>
        ) : (
          items.map((item, index) => (
            <div
              key={index}
              className={`px-3 py-2 rounded-lg border ${getSeverityColor(item.severity)}`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wide">{item.type}</span>
                <span className="text-xs">{item.value}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
