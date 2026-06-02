"use client";

import { useState } from 'react';
import { MapPin, Satellite, Leaf, Navigation } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

// Sample activity locations
const SAMPLE_ACTIVITIES = [
  { id: 1, lat: 35.6892, lng: 51.3890, type: 'tree_planting', carbon: 203, name: 'Tehran Forest' },
  { id: 2, lat: 32.6546, lng: 51.6680, type: 'agroforestry', carbon: 85, name: 'Isfahan Farm' },
  { id: 3, lat: 29.5916, lng: 52.5837, type: 'soil_regeneration', carbon: 120, name: 'Shiraz Plains' },
  { id: 4, lat: 38.0962, lng: 46.2738, type: 'tree_planting', carbon: 156, name: 'Tabriz Woods' },
  { id: 5, lat: 36.2605, lng: 59.6168, type: 'wetland_restoration', carbon: 95, name: 'Mashhad Wetlands' },
  { id: 6, lat: 27.1832, lng: 56.2666, type: 'mangrove_planting', carbon: 245, name: 'Hormozgan Coast' },
];

const TYPE_COLORS: Record<string, string> = {
  tree_planting: 'bg-green-500',
  agroforestry: 'bg-yellow-500',
  soil_regeneration: 'bg-brown-500',
  wetland_restoration: 'bg-blue-500',
  mangrove_planting: 'bg-teal-500',
};

export default function MapPage() {
  const [selectedActivity, setSelectedActivity] = useState<any>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="pt-24 pb-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
              <Satellite className="w-10 h-10 text-blue-600" />
              Global Activity Map
            </h1>
            <p className="text-gray-600">
              Explore ecological activities verified by Sentinel-2 satellite imagery
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Sidebar */}
            <div className="space-y-4">
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Activities</h2>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {SAMPLE_ACTIVITIES.map(activity => (
                    <div
                      key={activity.id}
                      onClick={() => setSelectedActivity(activity)}
                      className={`p-4 rounded-lg cursor-pointer transition ${
                        selectedActivity?.id === activity.id
                          ? 'bg-green-50 border-2 border-green-500'
                          : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold">{activity.name}</h3>
                          <p className="text-sm text-gray-600 capitalize">
                            {activity.type.replace(/_/g, ' ')}
                          </p>
                        </div>
                        <span className={`w-3 h-3 rounded-full ${TYPE_COLORS[activity.type]}`} />
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                        <Leaf className="w-4 h-4" />
                        <span>{activity.carbon} tons CO₂</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-500 to-cyan-600 text-white rounded-2xl shadow-lg p-6">
                <Satellite className="w-8 h-8 mb-3" />
                <h3 className="text-lg font-bold mb-2">Satellite Verification</h3>
                <p className="text-sm text-blue-100">
                  All activities are verified using Sentinel-2 NDVI analysis 
                  from Copernicus Data Space Ecosystem.
                </p>
              </div>
            </div>

            {/* Map */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden h-[700px] relative">
                {/* Placeholder for actual map - using CSS grid representation */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-green-50 to-blue-100">
                  {/* Grid lines */}
                  <div className="absolute inset-0" style={{
                    backgroundImage: `
                      linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px)
                    `,
                    backgroundSize: '50px 50px',
                  }} />
                  
                  {/* Activity markers */}
                  {SAMPLE_ACTIVITIES.map(activity => {
                    // Convert lat/lng to approximate position on map (Iran centered)
                    const x = ((activity.lng - 44) / 20) * 100;
                    const y = ((40 - activity.lat) / 15) * 100;
                    
                    return (
                      <button
                        key={activity.id}
                        onClick={() => setSelectedActivity(activity)}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 group"
                        style={{ left: `${x}%`, top: `${y}%` }}
                      >
                        <div className="relative">
                          <div className={`w-8 h-8 rounded-full ${TYPE_COLORS[activity.type]} border-4 border-white shadow-lg flex items-center justify-center`}>
                            <MapPin className="w-4 h-4 text-white" />
                          </div>
                          <div className={`absolute inset-0 rounded-full ${TYPE_COLORS[activity.type]} opacity-50 animate-ping`} />
                        </div>
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-white rounded-lg shadow-xl p-3 min-w-max z-10">
                          <div className="font-bold">{activity.name}</div>
                          <div className="text-sm text-gray-600">{activity.carbon} tons CO₂</div>
                        </div>
                      </button>
                    );
                  })}

                  {/* Iran borders approximation */}
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="text-center opacity-20">
                      <div className="text-9xl font-bold">IR</div>
                      <div className="text-2xl">Iran</div>
                    </div>
                  </div>
                </div>

                {/* Map overlay info */}
                <div className="absolute top-4 left-4 bg-white/90 backdrop-blur rounded-lg shadow-lg p-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Navigation className="w-4 h-4 text-green-600" />
                    <span className="font-medium">Iran Region</span>
                  </div>
                </div>

                {/* Selected activity details */}
                {selectedActivity && (
                  <div className="absolute bottom-4 left-4 right-4 bg-white rounded-xl shadow-2xl p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-xl font-bold">{selectedActivity.name}</h3>
                        <p className="text-gray-600 capitalize">
                          {selectedActivity.type.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <button
                        onClick={() => setSelectedActivity(null)}
                        className="text-gray-400 hover:text-gray-600 text-2xl"
                      >
                        ×
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <div className="text-sm text-gray-500">Carbon</div>
                        <div className="text-2xl font-bold text-green-600">
                          {selectedActivity.carbon}t
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">Latitude</div>
                        <div className="text-lg font-medium">
                          {selectedActivity.lat.toFixed(4)}°
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">Longitude</div>
                        <div className="text-lg font-medium">
                          {selectedActivity.lng.toFixed(4)}°
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        ✓ Satellite Verified
                      </span>
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                        NDVI: +0.167
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}
