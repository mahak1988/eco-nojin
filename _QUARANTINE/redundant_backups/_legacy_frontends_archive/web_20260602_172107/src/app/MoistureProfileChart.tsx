'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Droplets } from 'lucide-react';

interface MoistureProfileChartProps {
  data: any;
  soilParams: any;
  isRTL: boolean;
}

export default function MoistureProfileChart({ data, soilParams, isRTL }: MoistureProfileChartProps) {
  // Prepare data for chart
  const chartData = data.depthPoints.map((depth: number, i: number) => {
    const point: any = { depth };
    
    // Add moisture at different times
    [0, 5, 10, 15, 20, 25, 30].forEach((time, idx) => {
      if (time < data.timePoints.length) {
        point[`t${time}`] = (data.moistureProfiles[i][time] * 100).toFixed(2);
      }
    });
    
    return point;
  });

  const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6'];

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <Droplets className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold">
          {isRTL ? 'پروفیل رطوبت خاک در طول زمان' : 'Soil Moisture Profile Over Time'}
        </h3>
      </div>
      
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="depth" 
              label={{ 
                value: isRTL ? 'عمق (cm)' : 'Depth (cm)', 
                position: 'insideBottom', 
                offset: -10 
              }}
              reversed={isRTL}
            />
            <YAxis 
              label={{ 
                value: isRTL ? 'رطوبت (%)' : 'Moisture (%)', 
                angle: -90, 
                position: 'insideLeft' 
              }}
              domain={[0, soilParams.theta_s * 100]}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              label={isRTL ? 'زمان (روز)' : 'Time (days)'}
            />
            
            {[0, 5, 10, 15, 20, 25, 30].map((time, idx) => (
              <Line
                key={time}
                type="monotone"
                dataKey={`t${time}`}
                stroke={colors[idx]}
                strokeWidth={2}
                name={`${time} ${isRTL ? 'روز' : 'days'}`}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>{isRTL ? 'توضیح:' : 'Description:'}</strong>{' '}
          {isRTL 
            ? 'این نمودار تغییرات رطوبت خاک را در عمق‌های مختلف و در طول زمان نشان می‌دهد. خطوط رنگی مختلف نشان‌دهنده زمان‌های مختلف شبیه‌سازی هستند.'
            : 'This chart shows soil moisture changes at different depths over time. Different colored lines represent different simulation times.'}
        </p>
      </div>
    </div>
  );
}
