'use client';
import React from 'react';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Calculator, Leaf, Coins, DollarSign, MapPin, TreePine, Loader2 } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function CalculatePage() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa' || locale === 'ar' || locale === 'ur';

  const [formData, setFormData] = useState({
    activity_type: 'tree_planting',
    latitude: 35.6892,
    longitude: 51.3890,
    area_hectares: 1.0,
    tree_count: 1000,
    species: 'quercus_persica',
    annual_rainfall_mm: 400,
    avg_temperature_c: 18,
    duration_years: 20,
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/gaia/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error('Calculation failed');
      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <Calculator className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict?.carbon?.title || (isPersian ? 'محاسبه‌گر کربن' : 'Carbon Calculator')}</h1>
          <p className="text-gray-600 dark:text-gray-400">{dict?.carbon?.subtitle || (isPersian ? 'محاسبه با مدل‌های RothC و AquaCrop' : 'Calculate with RothC and AquaCrop models')}</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">{dict?.carbon?.activityType || 'Activity Type'}</label>
                <select value={formData.activity_type} onChange={(e) => setFormData({...formData, activity_type: e.target.value})}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none">
                  <option value="tree_planting">{dict?.carbon?.treePlanting || 'Tree Planting'}</option>
                  <option value="soil_regeneration">{dict?.carbon?.soilRegeneration || 'Soil Regeneration'}</option>
                  <option value="agroforestry">{dict?.carbon?.agroforestry || 'Agroforestry'}</option>
                  <option value="mangrove_planting">Mangrove Planting</option>
                  <option value="wetland_restoration">Wetland Restoration</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">{dict?.carbon?.latitude || 'Latitude'}</label>
                  <input type="number" step="0.0001" value={formData.latitude} onChange={(e) => setFormData({...formData, latitude: parseFloat(e.target.value)})}
                    className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">{dict?.carbon?.longitude || 'Longitude'}</label>
                  <input type="number" step="0.0001" value={formData.longitude} onChange={(e) => setFormData({...formData, longitude: parseFloat(e.target.value)})}
                    className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">{dict?.carbon?.treeCount || 'Tree Count'}</label>
                  <input type="number" value={formData.tree_count} onChange={(e) => setFormData({...formData, tree_count: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">{dict?.carbon?.duration || 'Duration (years)'}</label>
                  <input type="number" value={formData.duration_years} onChange={(e) => setFormData({...formData, duration_years: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{dict?.carbon?.species || 'Species'}</label>
                <select value={formData.species} onChange={(e) => setFormData({...formData, species: e.target.value})}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg">
                  <option value="quercus_persica">Persian Oak (بلوط ایرانی)</option>
                  <option value="eucalyptus">Eucalyptus</option>
                  <option value="populus">Poplar</option>
                </select>
              </div>

              <button type="submit" disabled={loading}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-4 rounded-lg font-semibold disabled:opacity-50 transition shadow-lg flex items-center justify-center gap-2">
                {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> {dict?.common?.loading || 'Calculating...'}</> : (dict?.carbon?.calculate || 'Calculate Carbon')}
              </button>

              {error && <div className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 p-3 rounded-lg">{error}</div>}
            </form>
          </div>

          <div className="space-y-6">
            {result ? (
              <>
                <div className="bg-gradient-to-br from-green-500 to-emerald-700 text-white rounded-2xl p-8 shadow-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Leaf className="w-6 h-6" />
                    <h2 className="text-xl font-bold">{dict?.carbon?.carbonAbsorbed || 'Carbon Absorbed'}</h2>
                  </div>
                  <div className="text-5xl font-bold mb-2">{result.carbon_absorbed_tons?.toFixed(2)}<span className="text-2xl ml-2">tons CO₂</span></div>
                  <div className="text-green-100 text-sm mt-2">Methodology: {result.methodology}</div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                    <Coins className="w-8 h-8 text-yellow-500 mb-2" />
                    <div className="text-2xl font-bold">{Math.round(result.seed_tokens_earned || 0).toLocaleString()}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">SEED Tokens</div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                    <DollarSign className="w-8 h-8 text-green-500 mb-2" />
                    <div className="text-2xl font-bold">${(result.estimated_gaia_value_usd || 0).toFixed(2)}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">GAIA Value</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                  <h3 className="font-bold mb-4">Projections</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span>Annual Rate:</span><span className="font-bold">{(result.annual_sequestration_rate || 0).toFixed(0)} kg/yr</span></div>
                    <div className="flex justify-between"><span>10-Year:</span><span className="font-bold">{(result.projection_10y_tons || 0).toFixed(2)} tons</span></div>
                    <div className="flex justify-between"><span>50-Year:</span><span className="font-bold">{(result.projection_50y_tons || 0).toFixed(2)} tons</span></div>
                    <div className="flex justify-between"><span>Confidence:</span><span className="font-bold text-green-600">{((result.confidence || 0) * 100).toFixed(1)}%</span></div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-12 text-center h-full flex flex-col items-center justify-center">
                <TreePine className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
                <p className="text-gray-500">{isPersian ? 'فرم را پر کنید و روی محاسبه کلیک کنید' : 'Fill the form and click Calculate'}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
