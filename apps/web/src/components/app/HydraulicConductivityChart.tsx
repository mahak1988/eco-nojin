'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

interface HydraulicConductivityChartProps {
  data: any;
  soilParams: any;
  isRTL: boolean;
}

export default function HydraulicConductivityChart({ data, soilParams, isRTL }: HydraulicConductivityChartProps) {
  // Prepare data for chart
  const chartData = data.depthPoints.map((depth: number, i: number) => ({
    depth,
    conductivity: data.conductivityProfiles[i].toFixed(2),
    logConductivity: Math.log10(data.conductivityProfiles[i]).toFixed(2),
  }));

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold">
          {isRTL ? 'هدایت هیدرولیکی در عمق' : 'Hydraulic Conductivity vs Depth'}
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
              yAxisId="left"
              label={{ 
                value: isRTL ? 'K (cm/day)' : 'K (cm/day)', 
                angle: -90, 
                position: 'insideLeft' 
              }}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              label={{ 
                value: isRTL ? 'log(K)' : 'log(K)', 
                angle: 90, 
                position: 'insideRight' 
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
            
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="conductivity"
              stroke="#3b82f6"
              strokeWidth={3}
              name={isRTL ? 'هدایت هیدرولیکی' : 'Hydraulic Conductivity'}
              dot={{ fill: '#3b82f6', r: 4 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="logConductivity"
              stroke="#ef4444"
              strokeWidth={2}
              strokeDasharray="5 5"
              name={isRTL ? 'لگاریتم هدایت' : 'Log Conductivity'}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm font-semibold text-blue-900 mb-2">
            {isRTL ? 'هدایت اشباع (Ks)' : 'Saturated Conductivity (Ks)'}
          </p>
          <p className="text-2xl font-bold text-blue-600">
            {soilParams.K_s.toFixed(2)} cm/day
          </p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <p className="text-sm font-semibold text-purple-900 mb-2">
            {isRTL ? 'میانگین هدایت' : 'Average Conductivity'}
          </p>
          <p className="text-2xl font-bold text-purple-600">
            {(data.conductivityProfiles.reduce((sum: number, val: number) => sum + val, 0) / data.conductivityProfiles.length).toFixed(2)} cm/day
          </p>
        </div>
      </div>
    </div>
  );
}
