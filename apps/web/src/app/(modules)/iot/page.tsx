"use client";

import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useSensorData, useIoTAlerts, useAcknowledgeAlert } from '@/hooks/iot/useIoT';
import { 
  Activity, AlertTriangle, CheckCircle, Radio, 
  Thermometer, Droplets, Wind, Sun, Zap, RefreshCw
} from 'lucide-react';

export default function IoTPage() {
  const { t } = useTranslation();
  const { data: sensors, isLoading, refetch } = useSensorData();
  const { data: alerts } = useIoTAlerts();
  const acknowledgeMutation = useAcknowledgeAlert();

  const getSensorIcon = (type: string) => {
    const icons: Record<string, any> = {
      temperature: Thermometer,
      humidity: Droplets,
      wind: Wind,
      light: Sun,
      power: Zap,
    };
    return icons[type] || Activity;
  };

  const getSensorColor = (status: string) => {
    switch (status) {
      case 'normal': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">{t('iot.title')}</h1>
            <p className="text-slate-400">{t('iot.subtitle')}</p>
          </div>
          <Button onClick={() => refetch()} variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            به‌روزرسانی
          </Button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">{t('iot.active_sensors')}</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {sensors?.filter((s: any) => s.status === 'normal').length || 0}
                </p>
              </div>
              <Radio className="w-8 h-8 text-green-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">{t('iot.alerts')}</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {alerts?.filter((a: any) => !a.acknowledged).length || 0}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">{t('iot.critical')}</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {sensors?.filter((s: any) => s.status === 'critical').length || 0}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">{t('iot.total_sensors')}</p>
                <p className="text-3xl font-bold text-white mt-1">{sensors?.length || 0}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
          </Card>
        </div>

        {/* Sensors Grid */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            سنسورهای فعال
          </h3>
          
          {isLoading ? (
            <div className="text-center py-8 text-slate-400">{t('common.loading')}</div>
          ) : sensors && sensors.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sensors.map((sensor: any, idx: number) => {
                const Icon = getSensorIcon(sensor.sensor_type);
                const colorClass = getSensorColor(sensor.status);
                
                return (
                  <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Icon className={`w-5 h-5 ${colorClass}`} />
                        <span className="text-sm font-medium text-white">{sensor.sensor_id}</span>
                      </div>
                      <Badge className={
                        sensor.status === 'normal' ? 'bg-green-600' :
                        sensor.status === 'warning' ? 'bg-yellow-600' : 'bg-red-600'
                      }>
                        {sensor.status}
                      </Badge>
                    </div>
                    
                    <div className="text-3xl font-bold text-white mb-1">
                      {sensor.last_value?.toFixed(1)}
                    </div>
                    <div className="text-sm text-slate-400">{sensor.sensor_type}</div>
                    
                    <div className="mt-3 pt-3 border-t border-slate-700 text-xs text-slate-400">
                      <div>میانگین ۲۴ ساعت: {sensor.mean?.toFixed(1)}</div>
                      <div>حداقل: {sensor.min?.toFixed(1)} | حداکثر: {sensor.max?.toFixed(1)}</div>
                      <div className="mt-1">آخرین به‌روزرسانی: {sensor.last_update}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              <Radio className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>سنسوری یافت نشد</p>
              <p className="text-sm mt-2">لطفاً سنسورها را فعال کنید</p>
            </div>
          )}
        </Card>

        {/* Alerts */}
        {alerts && alerts.length > 0 && (
          <Card className="bg-slate-900/50 border-slate-800 p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              هشدارهای فعال ({alerts.filter((a: any) => !a.acknowledged).length})
            </h3>
            <div className="space-y-3">
              {alerts.slice(0, 10).map((alert: any, idx: number) => (
                <div 
                  key={idx} 
                  className={`bg-slate-800/50 rounded-lg p-4 flex items-center gap-4 ${
                    alert.acknowledged ? 'opacity-50' : ''
                  }`}
                >
                  <AlertTriangle className={`w-6 h-6 flex-shrink-0 ${
                    alert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                  }`} />
                  <div className="flex-1">
                    <div className="font-medium text-white">{alert.message}</div>
                    <div className="text-sm text-slate-400 mt-1">
                      سنسور: {alert.sensor_id} | مقدار: {alert.value?.toFixed(1)} | آستانه: {alert.threshold?.toFixed(1)}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">{alert.timestamp}</div>
                  </div>
                  {!alert.acknowledged && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => acknowledgeMutation.mutate(alert.id)}
                    >
                      <CheckCircle className="w-4 h-4 ml-1" />
                      تأیید
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">پروتکل MQTT</h4>
            <p className="text-sm text-slate-400">ارتباط real-time با سنسورها از طریق EMQX broker</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">۱۲ نوع سنسور</h4>
            <p className="text-sm text-slate-400">دما، رطوبت، خاک، نور، باد، باران و...</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">هشدار هوشمند</h4>
            <p className="text-sm text-slate-400">سیستم آستانه خودکار با اعلان real-time</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
