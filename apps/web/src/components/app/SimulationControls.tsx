'use client';

import { Play, Loader2 } from 'lucide-react';

interface SimulationControlsProps {
  params: {
    duration: number;
    timeStep: number;
    initialMoisture: number;
    surfaceFlux: number;
    bottomBoundary: string;
  };
  onChange: (params: any) => void;
  onRun: () => void;
  isSimulating: boolean;
  isRTL: boolean;
}

export default function SimulationControls({ 
  params, 
  onChange, 
  onRun, 
  isSimulating,
  isRTL 
}: SimulationControlsProps) {
  const handleChange = (key: string, value: any) => {
    onChange({ ...params, [key]: value });
  };

  return (
    <div className="space-y-4">
      {/* Duration */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {isRTL ? 'مدت شبیه‌سازی (روز)' : 'Simulation Duration (days)'}
        </label>
        <input
          type="number"
          min={1}
          max={365}
          value={params.duration}
          onChange={(e) => handleChange('duration', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Time Step */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {isRTL ? 'گام زمانی (روز)' : 'Time Step (days)'}
        </label>
        <input
          type="number"
          min={0.01}
          max={1}
          step={0.01}
          value={params.timeStep}
          onChange={(e) => handleChange('timeStep', parseFloat(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Initial Moisture */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {isRTL ? 'رطوبت اولیه (cm³/cm³)' : 'Initial Moisture (cm³/cm³)'}
        </label>
        <input
          type="number"
          min={0.05}
          max={0.5}
          step={0.01}
          value={params.initialMoisture}
          onChange={(e) => handleChange('initialMoisture', parseFloat(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Surface Flux */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {isRTL ? 'شار سطحی (mm/day)' : 'Surface Flux (mm/day)'}
        </label>
        <input
          type="number"
          min={0}
          max={100}
          step={1}
          value={params.surfaceFlux}
          onChange={(e) => handleChange('surfaceFlux', parseFloat(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Bottom Boundary */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {isRTL ? 'شرط مرزی پایین' : 'Bottom Boundary Condition'}
        </label>
        <select
          value={params.bottomBoundary}
          onChange={(e) => handleChange('bottomBoundary', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="free">{isRTL ? 'زهکشی آزاد' : 'Free Drainage'}</option>
          <option value="fixed">{isRTL ? 'هد ثابت' : 'Fixed Head'}</option>
          <option value="flux">{isRTL ? 'شار ثابت' : 'Fixed Flux'}</option>
        </select>
      </div>

      {/* Run Button */}
      <button
        onClick={onRun}
        disabled={isSimulating}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
      >
        {isSimulating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            {isRTL ? 'در حال شبیه‌سازی...' : 'Simulating...'}
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            {isRTL ? 'اجرای شبیه‌سازی' : 'Run Simulation'}
          </>
        )}
      </button>
    </div>
  );
}
