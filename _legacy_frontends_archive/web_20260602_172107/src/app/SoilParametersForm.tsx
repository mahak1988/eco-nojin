'use client';

import { Droplets, Thermometer, Activity } from 'lucide-react';

interface SoilParametersFormProps {
  params: {
    theta_r: number;
    theta_s: number;
    alpha: number;
    n: number;
    K_s: number;
    l: number;
    depth: number;
  };
  onChange: (params: any) => void;
  isRTL: boolean;
}

export default function SoilParametersForm({ params, onChange, isRTL }: SoilParametersFormProps) {
  const handleChange = (key: string, value: number) => {
    onChange({ ...params, [key]: value });
  };

  const fields = [
    { 
      key: 'theta_r', 
      label: isRTL ? 'رطوبت باقیمانده (θr)' : 'Residual Moisture (θr)',
      unit: 'cm³/cm³',
      min: 0, max: 0.2, step: 0.001,
      icon: Droplets,
      color: 'blue'
    },
    { 
      key: 'theta_s', 
      label: isRTL ? 'رطوبت اشباع (θs)' : 'Saturated Moisture (θs)',
      unit: 'cm³/cm³',
      min: 0.3, max: 0.6, step: 0.001,
      icon: Droplets,
      color: 'cyan'
    },
    { 
      key: 'alpha', 
      label: isRTL ? 'پارامتر α' : 'Alpha Parameter (α)',
      unit: '1/cm',
      min: 0.001, max: 0.1, step: 0.001,
      icon: Activity,
      color: 'teal'
    },
    { 
      key: 'n', 
      label: isRTL ? 'پارامتر n' : 'Parameter n',
      unit: '-',
      min: 1.0, max: 3.0, step: 0.01,
      icon: Activity,
      color: 'green'
    },
    { 
      key: 'K_s', 
      label: isRTL ? 'هدایت اشباع (Ks)' : 'Saturated Conductivity (Ks)',
      unit: 'cm/day',
      min: 0.1, max: 100, step: 0.1,
      icon: Thermometer,
      color: 'orange'
    },
    { 
      key: 'l', 
      label: isRTL ? 'پارامتر l' : 'Parameter l',
      unit: '-',
      min: -1, max: 2, step: 0.1,
      icon: Activity,
      color: 'purple'
    },
    { 
      key: 'depth', 
      label: isRTL ? 'عمق پروفیل' : 'Profile Depth',
      unit: 'cm',
      min: 10, max: 200, step: 10,
      icon: Thermometer,
      color: 'red'
    },
  ];

  return (
    <div className="space-y-4">
      {fields.map((field) => {
        const Icon = field.icon;
        return (
          <div key={field.key}>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Icon className={`w-4 h-4 text-${field.color}-600`} />
              {field.label}
              <span className="text-xs text-gray-500">({field.unit})</span>
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min={field.min}
                max={field.max}
                step={field.step}
                value={(params as any)[field.key]}
                onChange={(e) => handleChange(field.key, parseFloat(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <input
                type="number"
                min={field.min}
                max={field.max}
                step={field.step}
                value={(params as any)[field.key]}
                onChange={(e) => handleChange(field.key, parseFloat(e.target.value))}
                className="w-24 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
