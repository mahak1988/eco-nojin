'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';

interface WaterBalanceChartProps {
  data: any;
  isRTL: boolean;
}

export default function WaterBalanceChart({ data, isRTL }: WaterBalanceChartProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold">
          {isRTL ? 'تراز آب در طول زمان' : 'Water Balance Over Time'}
        </h3>
      </div>
      
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data.waterBalance} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <defs>
              <linearGradient id="colorInfiltration" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.2}/>
              </linearGradient>
              <linearGradient id="colorDrainage" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.2}/>
              </linearGradient>
              <linearGradient id="colorStorage" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.2}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              label={{ 
                value: isRTL ? 'زمان (روز)' : 'Time (days)', 
                position: 'insideBottom', 
                offset: -10 
              }}
            />
            <YAxis 
              label={{ 
                value: isRTL ? 'مقدار (mm)' : 'Amount (mm)', 
                angle: -90, 
                position: 'insideLeft' 
              }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            
            <Area
              type="monotone"
              dataKey="infiltration"
              stroke="#3b82f6"
              fillOpacity={1}
              fill="url(#colorInfiltration)"
              name={isRTL ? 'نفوذ' : 'Infiltration'}
            />
            <Area
              type="monotone"
              dataKey="drainage"
              stroke="#ef4444"
              fillOpacity={1}
              fill="url(#colorDrainage)"
              name={isRTL ? 'زهکشی' : 'Drainage'}
            />
            <Area
              type="monotone"
              dataKey="storage"
              stroke="#22c55e"
              fillOpacity={1}
              fill="url(#colorStorage)"
              name={isRTL ? 'ذخیره' : 'Storage'}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-600">
          <p className="text-sm font-semibold text-blue-900 mb-1">
            {isRTL ? 'نفوذ کل' : 'Total Infiltration'}
          </p>
          <p className="text-2xl font-bold text-blue-600">
            {data.summary.totalInfiltration.toFixed(1)} mm
          </p>
        </div>
        <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-600">
          <p className="text-sm font-semibold text-red-900 mb-1">
            {isRTL ? 'زهکشی کل' : 'Total Drainage'}
          </p>
          <p className="text-2xl font-bold text-red-600">
            {data.summary.totalDrainage.toFixed(1)} mm
          </p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-600">
          <p className="text-sm font-semibold text-green-900 mb-1">
            {isRTL ? 'ذخیره نهایی' : 'Final Storage'}
          </p>
          <p className="text-2xl font-bold text-green-600">
            {data.summary.finalStorage.toFixed(1)} mm
          </p>
        </div>
      </div>
    </div>
  );
}
