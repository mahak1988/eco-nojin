"use client";

import { useState } from 'react';
import { Calculator, Leaf, Coins, DollarSign, TrendingUp, MapPin, TreePine } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import LoadingSpinner from '@/components/LoadingSpinner';
import { gaiaApi } from '@/lib/api';
import { formatNumber, formatUSD, calculateCO2Equivalent, getActivityLabel } from '@/lib/utils';
import type { CarbonResult } from '@/lib/types';

const SPECIES = [
  { value: 'quercus_persica', label: 'Persian Oak (بلوط ایرانی)' },
  { value: 'amygdalus_scoparia', label: 'Zagros Almond (بادام کوهی)' },
  { value: 'pistacia_atlantica', label: 'Wild Pistachio (بنه)' },
  { value: 'juniperus_excelsa', label: 'Juniper (ارس)' },
  { value: 'eucalyptus', label: 'Eucalyptus' },
  { value: 'populus', label: 'Poplar' },
];

const ACTIVITIES = [
  { value: 'tree_planting', label: '🌳 Tree Planting' },
  { value: 'soil_regeneration', label: '🌱 Soil Regeneration' },
  { value: 'agroforestry', label: '🌾 Agroforestry' },
  { value: 'mangrove_planting', label: '🌊 Mangrove Planting' },
  { value: 'wetland_restoration', label: '💧 Wetland Restoration' },
  { value: 'grassland_restoration', label: '🌿 Grassland Restoration' },
];

export default function CalculatePage() {
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
  
  const [result, setResult] = useState<CarbonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await gaiaApi.calculateCarbon(formData);
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Calculation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const equivalents = result ? calculateCO2Equivalent(formData.tree_count, formData.duration_years) : null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Navbar />
      
      <div className="container mx-auto px-4 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4 flex items-center justify-center gap-3">
              <Calculator className="w-10 h-10 text-green-600" />
              Carbon Calculator
            </h1>
            <p className="text-gray-600 text-lg">
              Calculate carbon absorption using IPCC, RothC, and AquaCrop models
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Form */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold mb-6">Activity Details</h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Activity Type</label>
                  <select
                    value={formData.activity_type}
                    onChange={(e) => setFormData({...formData, activity_type: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none transition"
                  >
                    {ACTIVITIES.map(act => (
                      <option key={act.value} value={act.value}>{act.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <MapPin className="w-4 h-4 inline mr-1" />
                      Latitude
                    </label>
                    <input
                      type="number"
                      step="0.0001"
                      value={formData.latitude}
                      onChange={(e) => setFormData({...formData, latitude: parseFloat(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Longitude</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={formData.longitude}
                      onChange={(e) => setFormData({...formData, longitude: parseFloat(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <TreePine className="w-4 h-4 inline mr-1" />
                      Tree Count
                    </label>
                    <input
                      type="number"
                      value={formData.tree_count}
                      onChange={(e) => setFormData({...formData, tree_count: parseInt(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Area (hectares)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={formData.area_hectares}
                      onChange={(e) => setFormData({...formData, area_hectares: parseFloat(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Species</label>
                  <select
                    value={formData.species}
                    onChange={(e) => setFormData({...formData, species: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                  >
                    {SPECIES.map(sp => (
                      <option key={sp.value} value={sp.value}>{sp.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Duration (yrs)</label>
                    <input
                      type="number"
                      value={formData.duration_years}
                      onChange={(e) => setFormData({...formData, duration_years: parseInt(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Rainfall (mm)</label>
                    <input
                      type="number"
                      value={formData.annual_rainfall_mm}
                      onChange={(e) => setFormData({...formData, annual_rainfall_mm: parseFloat(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Temp (°C)</label>
                    <input
                      type="number"
                      value={formData.avg_temperature_c}
                      onChange={(e) => setFormData({...formData, avg_temperature_c: parseFloat(e.target.value)})}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:outline-none"
                    />
                  </div>
                </div>
                
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-4 rounded-lg font-semibold disabled:opacity-50 transition shadow-lg hover:shadow-xl"
                >
                  {loading ? 'Calculating...' : 'Calculate Carbon'}
                </button>
                
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                    {error}
                  </div>
                )}
              </form>
            </div>
            
            {/* Results */}
            <div className="space-y-6">
              {loading ? (
                <div className="bg-white rounded-2xl shadow-xl p-12">
                  <LoadingSpinner size="lg" text="Running scientific models..." />
                </div>
              ) : result ? (
                <>
                  <div className="bg-gradient-to-br from-green-500 to-emerald-700 text-white rounded-2xl p-8 shadow-xl">
                    <div className="flex items-center gap-2 mb-2">
                      <Leaf className="w-6 h-6" />
                      <h2 className="text-xl font-bold">Carbon Absorbed</h2>
                    </div>
                    <div className="text-5xl font-bold mb-2">
                      {result.carbon_absorbed_tons.toFixed(2)}
                      <span className="text-2xl ml-2">tons CO₂</span>
                    </div>
                    <div className="text-green-100">
                      {getActivityLabel(formData.activity_type)} over {formData.duration_years} years
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white rounded-xl p-6 shadow-lg">
                      <Coins className="w-8 h-8 text-yellow-500 mb-2" />
                      <div className="text-2xl font-bold">{formatNumber(result.seed_tokens_earned, 0)}</div>
                      <div className="text-gray-600 text-sm">SEED Tokens</div>
                    </div>
                    
                    <div className="bg-white rounded-xl p-6 shadow-lg">
                      <DollarSign className="w-8 h-8 text-green-500 mb-2" />
                      <div className="text-2xl font-bold">{formatUSD(result.estimated_gaia_value_usd)}</div>
                      <div className="text-gray-600 text-sm">GAIA Value</div>
                    </div>
                  </div>
                  
                  {equivalents && (
                    <div className="bg-white rounded-xl p-6 shadow-lg">
                      <h3 className="font-bold mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Real-World Impact
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-gray-700">🚗 Cars removed (1 year)</span>
                          <span className="font-bold text-2xl">{equivalents.cars}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-gray-700">✈️ Flights offset (NYC-LA)</span>
                          <span className="font-bold text-2xl">{equivalents.flights}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-gray-700">🏠 Homes powered (1 year)</span>
                          <span className="font-bold text-2xl">{equivalents.homes}</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="bg-white rounded-xl p-6 shadow-lg">
                    <h3 className="font-bold mb-4">Projections</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Annual Rate:</span>
                        <span className="font-semibold">{formatNumber(result.annual_sequestration_rate)} kg/year</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">10-Year Projection:</span>
                        <span className="font-semibold">{formatNumber(result.projection_10y_tons)} tons</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">50-Year Projection:</span>
                        <span className="font-semibold">{formatNumber(result.projection_50y_tons)} tons</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Confidence:</span>
                        <span className="font-semibold text-green-600">{(result.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-900">
                    <strong>Methodology:</strong> {result.methodology}
                  </div>
                </>
              ) : (
                <div className="bg-gray-50 rounded-2xl p-12 text-center">
                  <Calculator className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Fill the form and click Calculate to see results</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}
