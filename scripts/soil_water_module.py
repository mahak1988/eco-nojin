#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soil Water Module - Complete Implementation
============================================
ایجاد ماژول کامل Soil Water با نمودار، جدول و تمام ویژگی‌ها
r"""

from pathlib import Path

PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def write_file(path, content):
    """نوشتن فایل"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Created: {path.relative_to(PROJECT_ROOT)}")


# ============================================================================
# صفحه اصلی Soil Water
# ============================================================================

soil_water_page = """'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
  Droplets, TrendingUp, Activity, Settings, Play, Pause, 
  Download, Upload, Save, RefreshCw, Info, AlertCircle,
  Thermometer, Wind, Sun, CloudRain
} from 'lucide-react';
import SoilParametersForm from '@/components/soil-water/SoilParametersForm';
import MoistureProfileChart from '@/components/soil-water/MoistureProfileChart';
import HydraulicConductivityChart from '@/components/soil-water/HydraulicConductivityChart';
import SimulationResultsTable from '@/components/soil-water/SimulationResultsTable';
import WaterBalanceChart from '@/components/soil-water/WaterBalanceChart';
import SimulationControls from '@/components/soil-water/SimulationControls';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function SoilWaterPage() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);

  // State management
  const [soilParams, setSoilParams] = useState({
    theta_r: 0.078,
    theta_s: 0.43,
    alpha: 0.036,
    n: 1.56,
    K_s: 24.96,
    l: 0.5,
    depth: 100,
  });

  const [simulationParams, setSimulationParams] = useState({
    duration: 30,
    timeStep: 0.1,
    initialMoisture: 0.25,
    surfaceFlux: 10,
    bottomBoundary: 'free',
  });

  const [results, setResults] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'conductivity' | 'balance' | 'table'>('profile');

  // Run simulation
  const runSimulation = async () => {
    setIsSimulating(true);
    
    // Simulate API call (در production به backend متصل می‌شود)
    setTimeout(() => {
      // Generate mock results
      const depthPoints = Array.from({ length: 11 }, (_, i) => i * 10);
      const timePoints = Array.from({ length: simulationParams.duration + 1 }, (_, i) => i);
      
      const moistureProfiles = depthPoints.map(depth => {
        return timePoints.map(time => {
          const baseMoisture = soilParams.theta_r + 
            (soilParams.theta_s - soilParams.theta_r) * 
            Math.exp(-depth / 50) * 
            (1 - Math.exp(-time / 5));
          return baseMoisture;
        });
      });

      const conductivityProfiles = depthPoints.map(depth => {
        const theta = soilParams.theta_r + 
          (soilParams.theta_s - soilParams.theta_r) * Math.exp(-depth / 50);
        const Se = (theta - soilParams.theta_r) / (soilParams.theta_s - soilParams.theta_r);
        const K = soilParams.K_s * Math.pow(Se, soilParams.l) * 
          Math.pow(1 - Math.pow(1 - Math.pow(Se, 1/soilParams.n), soilParams.n), 2);
        return K;
      });

      const waterBalance = timePoints.map(time => {
        const infiltration = Math.min(simulationParams.surfaceFlux * time, 100);
        const drainage = Math.max(0, infiltration * 0.3 * (1 - Math.exp(-time / 10)));
        const storage = infiltration - drainage;
        return { time, infiltration, drainage, storage };
      });

      setResults({
        depthPoints,
        timePoints,
        moistureProfiles,
        conductivityProfiles,
        waterBalance,
        summary: {
          totalInfiltration: waterBalance[waterBalance.length - 1].infiltration,
          totalDrainage: waterBalance[waterBalance.length - 1].drainage,
          finalStorage: waterBalance[waterBalance.length - 1].storage,
          averageMoisture: moistureProfiles.reduce((sum, profile) => 
            sum + profile[profile.length - 1], 0) / moistureProfiles.length,
        }
      });
      
      setIsSimulating(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center gap-4 mb-4">
            <Droplets className="w-12 h-12" />
            <div>
              <h1 className="text-4xl font-bold">
                {isRTL ? 'شبیه‌سازی آب در خاک' : 'Soil Water Simulation'}
              </h1>
              <p className="text-blue-100 mt-2">
                {isRTL 
                  ? 'مدل‌سازی نفوذ، زهکشی و پروفیل رطوبت با معادله ریچاردز' 
                  : 'Modeling infiltration, drainage, and moisture profile with Richards equation'}
              </p>
            </div>
          </div>
          
          {/* Quick Stats */}
          {results && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CloudRain className="w-5 h-5" />
                  <span className="text-sm text-blue-100">
                    {isRTL ? 'نفوذ کل' : 'Total Infiltration'}
                  </span>
                </div>
                <div className="text-2xl font-bold">
                  {results.summary.totalInfiltration.toFixed(1)} mm
                </div>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5" />
                  <span className="text-sm text-blue-100">
                    {isRTL ? 'زهکشی کل' : 'Total Drainage'}
                  </span>
                </div>
                <div className="text-2xl font-bold">
                  {results.summary.totalDrainage.toFixed(1)} mm
                </div>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-5 h-5" />
                  <span className="text-sm text-blue-100">
                    {isRTL ? 'ذخیره نهایی' : 'Final Storage'}
                  </span>
                </div>
                <div className="text-2xl font-bold">
                  {results.summary.finalStorage.toFixed(1)} mm
                </div>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Droplets className="w-5 h-5" />
                  <span className="text-sm text-blue-100">
                    {isRTL ? 'رطوبت میانگین' : 'Avg Moisture'}
                  </span>
                </div>
                <div className="text-2xl font-bold">
                  {(results.summary.averageMoisture * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Parameters */}
          <div className="lg:col-span-1 space-y-6">
            {/* Soil Parameters */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <Settings className="w-5 h-5 text-blue-600" />
                <h2 className="text-xl font-bold">
                  {isRTL ? 'پارامترهای خاک' : 'Soil Parameters'}
                </h2>
              </div>
              <SoilParametersForm 
                params={soilParams}
                onChange={setSoilParams}
                isRTL={isRTL}
              />
            </div>

            {/* Simulation Controls */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-5 h-5 text-blue-600" />
                <h2 className="text-xl font-bold">
                  {isRTL ? 'کنترل شبیه‌سازی' : 'Simulation Controls'}
                </h2>
              </div>
              <SimulationControls
                params={simulationParams}
                onChange={setSimulationParams}
                onRun={runSimulation}
                isSimulating={isSimulating}
                isRTL={isRTL}
              />
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-900">
                  <p className="font-semibold mb-2">
                    {isRTL ? 'درباره این ماژول' : 'About This Module'}
                  </p>
                  <p className="text-blue-700">
                    {isRTL 
                      ? 'این ماژول از معادله ریچاردز برای شبیه‌سازی جریان آب در خاک غیراشباع استفاده می‌کند. مدل van Genuchten-Mualem برای توصیف ویژگی‌های هیدرولیکی خاک به کار می‌رود.'
                      : 'This module uses Richards equation to simulate water flow in unsaturated soil. The van Genuchten-Mualem model is used to describe soil hydraulic properties.'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tab Navigation */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  {[
                    { id: 'profile', label: isRTL ? 'پروفیل رطوبت' : 'Moisture Profile', icon: Droplets },
                    { id: 'conductivity', label: isRTL ? 'هدایت هیدرولیکی' : 'Hydraulic Conductivity', icon: TrendingUp },
                    { id: 'balance', label: isRTL ? 'تراز آب' : 'Water Balance', icon: Activity },
                    { id: 'table', label: isRTL ? 'جدول نتایج' : 'Results Table', icon: Activity },
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors ${
                          activeTab === tab.id
                            ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        {tab.label}
                      </button>
                    );
                  })}
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {!results ? (
                  <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                    <AlertCircle className="w-16 h-16 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">
                      {isRTL ? 'هنوز شبیه‌سازی انجام نشده است' : 'No simulation has been run yet'}
                    </p>
                    <p className="text-sm mt-2">
                      {isRTL 
                        ? 'پارامترها را تنظیم کرده و دکمه "اجرای شبیه‌سازی" را بزنید'
                        : 'Configure parameters and click "Run Simulation"'}
                    </p>
                  </div>
                ) : (
                  <>
                    {activeTab === 'profile' && (
                      <MoistureProfileChart 
                        data={results}
                        soilParams={soilParams}
                        isRTL={isRTL}
                      />
                    )}
                    {activeTab === 'conductivity' && (
                      <HydraulicConductivityChart
                        data={results}
                        soilParams={soilParams}
                        isRTL={isRTL}
                      />
                    )}
                    {activeTab === 'balance' && (
                      <WaterBalanceChart
                        data={results}
                        isRTL={isRTL}
                      />
                    )}
                    {activeTab === 'table' && (
                      <SimulationResultsTable
                        data={results}
                        soilParams={soilParams}
                        isRTL={isRTL}
                      />
                    )}
                  </>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            {results && (
              <div className="flex gap-3">
                <button className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
                  <Download className="w-5 h-5" />
                  {isRTL ? 'دانلود نتایج' : 'Download Results'}
                </button>
                <button className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors">
                  <Save className="w-5 h-5" />
                  {isRTL ? 'ذخیره سناریو' : 'Save Scenario'}
                </button>
                <button className="flex items-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-xl hover:bg-gray-700 transition-colors">
                  <RefreshCw className="w-5 h-5" />
                  {isRTL ? 'بازنشانی' : 'Reset'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
"""

write_file(FRONTEND_DIR / "app" / "[locale]" / "soil-water" / "page.tsx", soil_water_page)

# ============================================================================
# کامپوننت فرم پارامترهای خاک
# ============================================================================

soil_parameters_form = """'use client';

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
"""

write_file(
    FRONTEND_DIR / "components" / "soil-water" / "SoilParametersForm.tsx", soil_parameters_form
)

# ============================================================================
# کامپوننت نمودار پروفیل رطوبت
# ============================================================================

moisture_profile_chart = """'use client';

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
"""

write_file(
    FRONTEND_DIR / "components" / "soil-water" / "MoistureProfileChart.tsx", moisture_profile_chart
)

# ============================================================================
# کامپوننت نمودار هدایت هیدرولیکی
# ============================================================================

hydraulic_conductivity_chart = """'use client';

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
"""

write_file(
    FRONTEND_DIR / "components" / "soil-water" / "HydraulicConductivityChart.tsx",
    hydraulic_conductivity_chart,
)

# ============================================================================
# کامپوننت نمودار تراز آب
# ============================================================================

water_balance_chart = """'use client';

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
"""

write_file(
    FRONTEND_DIR / "components" / "soil-water" / "WaterBalanceChart.tsx", water_balance_chart
)

# ============================================================================
# کامپوننت جدول نتایج
# ============================================================================

simulation_results_table = """'use client';

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
"""

write_file(
    FRONTEND_DIR / "components" / "soil-water" / "SimulationResultsTable.tsx",
    simulation_results_table,
)

# ============================================================================
# کامپوننت کنترل‌های شبیه‌سازی
# ============================================================================

simulation_controls = """'use client';

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
r"""

write_file(
    FRONTEND_DIR / "components" / "soil-water" / "SimulationControls.tsx", simulation_controls
)

print("\n" + "=" * 70)
print("✅ ماژول Soil Water با موفقیت ایجاد شد!")
print("=" * 70)
print("\n📋 فایل‌های ایجاد شده:")
print("  • app/[locale]/soil-water/page.tsx")
print("  • components/soil-water/SoilParametersForm.tsx")
print("  • components/soil-water/MoistureProfileChart.tsx")
print("  • components/soil-water/HydraulicConductivityChart.tsx")
print("  • components/soil-water/WaterBalanceChart.tsx")
print("  • components/soil-water/SimulationResultsTable.tsx")
print("  • components/soil-water/SimulationControls.tsx")
print("\n🎨 ویژگی‌های ماژول:")
print("  ✓ نمودار پروفیل رطوبت در طول زمان")
print("  ✓ نمودار هدایت هیدرولیکی")
print("  ✓ نمودار تراز آب (Area Chart)")
print("  ✓ جدول نتایج با آمار")
print("  ✓ فرم پارامترهای خاک (van Genuchten)")
print("  ✓ کنترل‌های شبیه‌سازی")
print("  ✓ کارت‌های آماری")
print("  ✓ پشتیبانی از RTL و i18n")
print("\n📦 نیاز به نصب:")
print("  npm install recharts lucide-react")
print("\n🚀 اجرا:")
print("  cd frontend && npm run dev")
