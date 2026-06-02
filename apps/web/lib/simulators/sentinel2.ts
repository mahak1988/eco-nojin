// Enhanced Sentinel-2 Satellite Simulator
// Provides realistic mock satellite data for demo

export interface SatelliteImage {
  id: string;
  name: string;
  date: string;
  cloud_cover: number;
  ndvi: number;
  download_url: string;
  simulation: boolean;
}

export interface VerificationResult {
  verified: boolean;
  ndvi_before: number;
  ndvi_after: number;
  ndvi_change: number;
  cloud_cover: number;
  confidence: number;
  threshold: number;
  activity_type: string;
  before_date: string;
  after_date: string;
  data_source: string;
  satellite: string;
  resolution_m: number;
  image_before?: SatelliteImage;
  image_after?: SatelliteImage;
}

// Activity-specific NDVI change thresholds
const ACTIVITY_THRESHOLDS: Record<string, number> = {
  'tree_planting': 0.10,
  'mangrove_planting': 0.15,
  'soil_regeneration': 0.05,
  'agroforestry': 0.08,
  'wetland_restoration': 0.10,
  'grassland_restoration': 0.06,
};

// Generate realistic NDVI values based on location and time
function generateNdvi(lat: number, lng: number, date: Date, activityType?: string): number {
  // Base NDVI by latitude (tropical vs temperate)
  const latFactor = lat < 23.5 ? 0.6 : lat < 45 ? 0.5 : 0.4;
  
  // Seasonal variation (simplified)
  const month = date.getMonth();
  const seasonFactor = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.85, 0.75, 0.65, 0.55, 0.45, 0.4][month];
  
  // Activity boost if applicable
  const activityBoost = activityType ? (ACTIVITY_THRESHOLDS[activityType] || 0.1) * 0.5 : 0;
  
  // Random variation for realism
  const noise = (Math.sin(lat * 10 + lng * 5 + date.getTime() / 86400000) * 0.05);
  
  return Math.min(0.95, Math.max(0.1, latFactor * seasonFactor + activityBoost + noise));
}

export function simulateSatelliteSearch(lat: number, lng: number, startDate: Date, endDate: Date, maxCloudCover: number = 20): SatelliteImage[] {
  const images: SatelliteImage[] = [];
  const satellites = ['Sentinel-2A', 'Sentinel-2B'];
  
  // Generate 3-7 mock images
  const count = 3 + Math.floor(Math.abs(Math.sin(lat + lng)) * 4);
  
  for (let i = 0; i < count; i++) {
    const daysOffset = Math.floor(Math.random() * (endDate.getTime() - startDate.getTime()) / 86400000);
    const imageDate = new Date(startDate.getTime() + daysOffset * 86400000);
    const cloudCover = Math.random() * 25;
    
    if (cloudCover <= maxCloudCover) {
      images.push({
        id: `S2_${satellites[i % 2]}_${imageDate.toISOString().split('T')[0].replace(/-/g, '')}`,
        name: `S2${satellites[i % 2].slice(-1)}_MSIL2A_${imageDate.toISOString().split('T')[0].replace(/-/g, '')}`,
        date: imageDate.toISOString(),
        cloud_cover: parseFloat(cloudCover.toFixed(1)),
        ndvi: generateNdvi(lat, lng, imageDate),
        download_url: `https://simulation.dataspace.copernicus.eu/${images.length}`,
        simulation: true,
      });
    }
  }
  
  return images.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export function simulateVerification(
  lat: number, 
  lng: number, 
  activityDate: Date, 
  activityType: string = 'tree_planting'
): VerificationResult {
  const beforeDate = new Date(activityDate);
  beforeDate.setDate(beforeDate.getDate() - 30);
  
  const afterDate = new Date(activityDate);
  afterDate.setDate(afterDate.getDate() + 180);
  
  const ndviBefore = generateNdvi(lat, lng, beforeDate);
  const ndviAfter = generateNdvi(lat, lng, afterDate, activityType);
  const ndviChange = ndviAfter - ndviBefore;
  
  const threshold = ACTIVITY_THRESHOLDS[activityType] || 0.1;
  const verified = ndviChange >= threshold;
  
  // Confidence calculation
  const baseConfidence = verified ? 0.7 : 0.3;
  const cloudBonus = 0.1; // Low cloud = higher confidence
  const changeBonus = Math.min(0.2, Math.abs(ndviChange) * 1.5);
  const confidence = Math.min(0.98, baseConfidence + cloudBonus + changeBonus);
  
  return {
    verified,
    ndvi_before: parseFloat(ndviBefore.toFixed(3)),
    ndvi_after: parseFloat(ndviAfter.toFixed(3)),
    ndvi_change: parseFloat(ndviChange.toFixed(3)),
    cloud_cover: parseFloat((Math.random() * 15).toFixed(1)),
    confidence: parseFloat(confidence.toFixed(3)),
    threshold,
    activity_type: activityType,
    before_date: beforeDate.toISOString(),
    after_date: afterDate.toISOString(),
    data_source: 'SIMULATION (Copernicus Data Space)',
    satellite: 'Sentinel-2A/B',
    resolution_m: 10,
    image_before: {
      id: 'mock_before',
      name: 'S2_MOCK_BEFORE',
      date: beforeDate.toISOString(),
      cloud_cover: 5,
      ndvi: ndviBefore,
      download_url: '#',
      simulation: true,
    },
    image_after: {
      id: 'mock_after',
      name: 'S2_MOCK_AFTER',
      date: afterDate.toISOString(),
      cloud_cover: 3,
      ndvi: ndviAfter,
      download_url: '#',
      simulation: true,
    },
  };
}

// Export for API integration
export const SentinelSimulator = {
  search: simulateSatelliteSearch,
  verify: simulateVerification,
  generateNdvi,
};
