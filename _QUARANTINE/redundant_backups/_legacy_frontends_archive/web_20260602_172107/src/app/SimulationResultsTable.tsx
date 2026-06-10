'use client';

import { Table } from 'lucide-react';

interface SimulationResultsTableProps {
  data: any;
  soilParams: any;
  isRTL: boolean;
}

export default function SimulationResultsTable({ data, soilParams, isRTL }: SimulationResultsTableProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <Table className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold">
          {isRTL ? 'جدول نتایج شبیه‌سازی' : 'Simulation Results Table'}
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {isRTL ? 'عمق (cm)' : 'Depth (cm)'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {isRTL ? 'رطوبت اولیه (%)' : 'Initial Moisture (%)'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {isRTL ? 'رطوبت نهایی (%)' : 'Final Moisture (%)'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {isRTL ? 'تغییر (%)' : 'Change (%)'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {isRTL ? 'K (cm/day)' : 'K (cm/day)'}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.depthPoints.map((depth: number, i: number) => {
              const initialMoisture = (data.moistureProfiles[i][0] * 100).toFixed(2);
              const finalMoisture = (data.moistureProfiles[i][data.moistureProfiles[i].length - 1] * 100).toFixed(2);
              const change = (parseFloat(finalMoisture) - parseFloat(initialMoisture)).toFixed(2);
              const conductivity = data.conductivityProfiles[i].toFixed(2);
              
              return (
                <tr key={depth} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {depth}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {initialMoisture}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {finalMoisture}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      parseFloat(change) > 0 
                        ? 'bg-green-100 text-green-800' 
                        : parseFloat(change) < 0 
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {parseFloat(change) > 0 ? '+' : ''}{change}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {conductivity}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-gray-900 mb-3">
          {isRTL ? 'خلاصه آماری' : 'Statistical Summary'}
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-500">{isRTL ? 'میانگین رطوبت' : 'Avg Moisture'}</p>
            <p className="text-lg font-bold text-gray-900">
              {(data.summary.averageMoisture * 100).toFixed(2)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">{isRTL ? 'حداکثر رطوبت' : 'Max Moisture'}</p>
            <p className="text-lg font-bold text-gray-900">
              {(soilParams.theta_s * 100).toFixed(2)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">{isRTL ? 'حداقل رطوبت' : 'Min Moisture'}</p>
            <p className="text-lg font-bold text-gray-900">
              {(soilParams.theta_r * 100).toFixed(2)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">{isRTL ? 'میانگین K' : 'Avg K'}</p>
            <p className="text-lg font-bold text-gray-900">
              {(data.conductivityProfiles.reduce((sum: number, val: number) => sum + val, 0) / data.conductivityProfiles.length).toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
