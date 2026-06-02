import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
  color?: 'green' | 'blue' | 'purple' | 'yellow' | 'red';
}

const colorClasses = {
  green: 'from-green-500 to-emerald-600',
  blue: 'from-blue-500 to-cyan-600',
  purple: 'from-purple-500 to-pink-600',
  yellow: 'from-yellow-500 to-orange-600',
  red: 'from-red-500 to-rose-600',
};

export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  className,
  color = 'green',
}: StatCardProps) {
  return (
    <div className={cn(
      "relative overflow-hidden rounded-xl bg-white shadow-lg hover:shadow-xl transition-all duration-300",
      className
    )}>
      <div className={cn(
        "absolute top-0 right-0 w-32 h-32 rounded-full bg-gradient-to-br opacity-10 -mr-16 -mt-16",
        colorClasses[color]
      )} />
      
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
            {subtitle && (
              <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
            )}
          </div>
          {icon && (
            <div className={cn(
              "p-3 rounded-lg bg-gradient-to-br text-white",
              colorClasses[color]
            )}>
              {icon}
            </div>
          )}
        </div>
        
        {trend && (
          <div className="mt-4 flex items-center text-sm">
            <span className={cn(
              "font-medium",
              trend.isPositive ? "text-green-600" : "text-red-600"
            )}>
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </span>
            <span className="ml-2 text-gray-500">vs last month</span>
          </div>
        )}
      </div>
    </div>
  );
}
