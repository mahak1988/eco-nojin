"use client";

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useSensorData, useIoTAlerts } from '@/hooks/iot/useIoT';
import { Activity, AlertTriangle, CheckCircle } from 'lucide-react';

export function IoTDashboard() {
  const { data: sensors } = useSensorData();
  const { data: alerts } = useIoTAlerts();

  return (
    <div className="space-y-4">
      <Card className="bg-slate-900/50 border-slate-800 p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-emerald-400" />
          سنسورهای فعال
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sensors?.slice(0, 6).map((sensor: any, idx: number) => (
            <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">{sensor.sensor_id}</span>
                <Badge className={
                  sensor.status === 'normal' ? 'bg-green-600' :
                  sensor.status === 'warning' ? 'bg-yellow-600' : 'bg-red-600'
                }>
                  {sensor.status}
                </Badge>
              </div>
              <div className="text-2xl font-bold text-white">{sensor.last_value?.toFixed(1)}</div>
              <div className="text-xs text-slate-400">{sensor.sensor_type}</div>
            </div>
          ))}
        </div>
      </Card>

      {alerts && alerts.length > 0 && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            هشدارهای فعال
          </h3>
          <div className="space-y-2">
            {alerts.slice(0, 5).map((alert: any, idx: number) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-3 flex items-center gap-3">
                <AlertTriangle className={`w-5 h-5 ${
                  alert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                }`} />
                <div className="flex-1">
                  <div className="text-sm text-white">{alert.message}</div>
                  <div className="text-xs text-slate-400">{alert.sensor_id}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
