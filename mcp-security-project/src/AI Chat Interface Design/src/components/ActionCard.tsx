import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

type Action = 'ALLOWED' | 'REDACTED' | 'BLOCKED';

interface ActionCardProps {
  action: Action;
}

export function ActionCard({ action }: ActionCardProps) {
  const getActionConfig = (action: Action) => {
    switch (action) {
      case 'ALLOWED':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
        };
      case 'REDACTED':
        return {
          icon: AlertTriangle,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
        };
      case 'BLOCKED':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
        };
    }
  };

  const config = getActionConfig(action);
  const Icon = config.icon;

  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-4 shadow-sm`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon className={`w-5 h-5 ${config.color}`} />
        <h3 className="text-gray-900">Action Taken</h3>
      </div>
      <div className={`${config.bgColor} ${config.borderColor} border rounded-lg px-4 py-3 flex items-center justify-center`}>
        <span className={`${config.color} tracking-wide`}>{action}</span>
      </div>
    </div>
  );
}
