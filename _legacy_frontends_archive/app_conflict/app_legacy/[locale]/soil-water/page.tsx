'use client';

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
