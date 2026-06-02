import { getActivityIcon, getActivityLabel, formatNumber } from '@/lib/utils';

interface ActivityCardProps {
  activity: {
    token_id: number;
    activity_type: string;
    carbon_kg: number;
    growth_stage: string;
    health_score: number;
    verified_sources: string[];
  };
  onClick?: () => void;
}

const stageColors: Record<string, string> = {
  seedling: 'bg-yellow-100 text-yellow-800',
  sapling: 'bg-green-100 text-green-800',
  young: 'bg-blue-100 text-blue-800',
  mature: 'bg-purple-100 text-purple-800',
  old: 'bg-gray-100 text-gray-800',
};

export default function ActivityCard({ activity, onClick }: ActivityCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer group"
    >
      <div className="relative h-32 bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center">
        <span className="text-6xl group-hover:scale-110 transition-transform">
          {getActivityIcon(activity.activity_type)}
        </span>
        <div className="absolute top-2 right-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${stageColors[activity.growth_stage] || 'bg-gray-100'}`}>
            {activity.growth_stage}
          </span>
        </div>
        <div className="absolute bottom-2 left-2">
          <span className="px-2 py-1 bg-white/90 rounded-full text-xs font-medium text-gray-700">
            #{activity.token_id}
          </span>
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-2">
          {getActivityLabel(activity.activity_type)}
        </h3>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Carbon:</span>
            <span className="font-medium text-green-600">
              {formatNumber(activity.carbon_kg)} kg
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-gray-500">Health:</span>
            <span className="font-medium">
              {(activity.health_score * 100).toFixed(0)}%
            </span>
          </div>
          
          <div className="flex items-center gap-1 flex-wrap mt-2">
            {activity.verified_sources.map((source) => (
              <span
                key={source}
                className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs"
              >
                ✓ {source}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
