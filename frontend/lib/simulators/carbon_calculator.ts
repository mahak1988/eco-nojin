// Enhanced Carbon Calculator Simulator
// Provides realistic mock data for demo without backend

export interface CarbonInput {
  activity_type: string;
  latitude: number;
  longitude: number;
  area_hectares: number;
  tree_count: number;
  species: string;
  annual_rainfall_mm: number;
  avg_temperature_c: number;
  duration_years: number;
}

export interface CarbonResult {
  activity_type: string;
  carbon_absorbed_kg: number;
  carbon_absorbed_tons: number;
  annual_sequestration_rate: number;
  projection_10y_tons: number;
  projection_50y_tons: number;
  confidence: number;
  methodology: string;
  seed_tokens_earned: number;
  estimated_gaia_value_usd: number;
  verification_sources: string[];
  satellite_data: {
    ndvi_before: number;
    ndvi_after: number;
    ndvi_change: number;
    image_date: string;
  };
}

// Species carbon absorption rates (kg CO2/tree/year)
const SPECIES_RATES: Record<string, number> = {
  'quercus_persica': 0.022,  // Persian Oak
  'amygdalus_scoparia': 0.018,  // Zagros Almond
  'pistacia_atlantica': 0.020,  // Wild Pistachio
  'juniperus_excelsa': 0.015,  // Juniper
  'eucalyptus': 0.035,  // Eucalyptus (fast growing)
  'populus': 0.028,  // Poplar
};

// Activity multipliers
const ACTIVITY_MULTIPLIERS: Record<string, number> = {
  'tree_planting': 1.0,
  'soil_regeneration': 0.6,
  'agroforestry': 1.3,
  'mangrove_planting': 2.1,
  'wetland_restoration': 1.8,
  'grassland_restoration': 0.4,
};

// Climate zone factors
function getClimateFactor(lat: number, rainfall: number, temp: number): number {
  // Simplified climate factor based on location
  if (rainfall > 600 && temp > 15) return 1.2;  // Tropical
  if (rainfall > 400 && temp > 10) return 1.0;  // Temperate
  if (rainfall > 200) return 0.7;  // Semi-arid
  return 0.4;  // Arid
}

export function simulateCarbonCalculation(input: CarbonInput): CarbonResult {
  // Base calculation using RothC-like model
  const baseRate = SPECIES_RATES[input.species] || 0.020;
  const activityMult = ACTIVITY_MULTIPLIERS[input.activity_type] || 1.0;
  const climateFactor = getClimateFactor(input.latitude, input.annual_rainfall_mm, input.avg_temperature_c);
  
  // Calculate total carbon
  const annualPerTree = baseRate * activityMult * climateFactor;
  const totalAnnualKg = annualPerTree * input.tree_count;
  const totalTons = (totalAnnualKg * input.duration_years) / 1000;
  
  // Projections with decay factor
  const decayFactor = 0.95; // Trees grow slower over time
  const projection10y = totalAnnualKg * 10 * (1 + decayFactor) / 2 / 1000;
  const projection50y = totalAnnualKg * 50 * Math.pow(decayFactor, 2) / 1000;
  
  // Confidence based on data quality
  const confidence = 0.7 + 
    (input.annual_rainfall_mm > 300 ? 0.1 : 0) +
    (input.duration_years >= 10 ? 0.1 : 0) +
    (input.tree_count >= 100 ? 0.05 : 0);
  
  // Economic values
  const seedTokens = Math.round(totalTons * 100);
  const gaiaValue = totalTons * 50; // $50 per ton CO2
  
  // Satellite simulation
  const ndviBefore = 0.2 + Math.random() * 0.15;
  const ndviAfter = ndviBefore + (0.1 + Math.random() * 0.2);
  
  return {
    activity_type: input.activity_type,
    carbon_absorbed_kg: Math.round(totalAnnualKg * input.duration_years),
    carbon_absorbed_tons: parseFloat(totalTons.toFixed(2)),
    annual_sequestration_rate: Math.round(totalAnnualKg),
    projection_10y_tons: parseFloat(projection10y.toFixed(2)),
    projection_50y_tons: parseFloat(projection50y.toFixed(2)),
    confidence: parseFloat(confidence.toFixed(2)),
    methodology: 'RothC + AquaCrop + Climate Factor Model',
    seed_tokens_earned: seedTokens,
    estimated_gaia_value_usd: parseFloat(gaiaValue.toFixed(2)),
    verification_sources: ['Sentinel-2 NDVI', 'RothC Model', 'AquaCrop Model', 'IPCC Guidelines'],
    satellite_data: {
      ndvi_before: parseFloat(ndviBefore.toFixed(3)),
      ndvi_after: parseFloat(ndviAfter.toFixed(3)),
      ndvi_change: parseFloat((ndviAfter - ndviBefore).toFixed(3)),
      image_date: new Date().toISOString().split('T')[0],
    },
  };
}

// Mock portfolio data generator
export function generateMockPortfolio(address: string) {
  const seed = address.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
  const random = (min: number, max: number) => {
    const x = Math.sin(seed + Math.random()) * 10000;
    return min + (x - Math.floor(x)) * (max - min);
  };

  const certificates = Array.from({ length: Math.floor(random(1, 5)) }, (_, i) => ({
    id: seed + i,
    type: ['tree_planting', 'soil_regeneration', 'agroforestry'][Math.floor(random(0, 3))],
    carbon_kg: Math.floor(random(10000, 200000)),
    health: parseFloat(random(0.7, 0.98).toFixed(2)),
    stage: ['seedling', 'sapling', 'young', 'mature'][Math.floor(random(0, 4))],
    verified: ['satellite', 'iot', 'scientific', 'community'].slice(0, Math.floor(random(1, 4))),
    minted_at: new Date(Date.now() - random(0, 365) * 24 * 60 * 60 * 1000).toISOString(),
  }));

  const totalCarbon = certificates.reduce((sum, c) => sum + c.carbon_kg, 0);
  
  return {
    address,
    total_certificates: certificates.length,
    total_carbon_kg: totalCarbon,
    total_carbon_tons: parseFloat((totalCarbon / 1000).toFixed(2)),
    estimated_value_usd: parseFloat((totalCarbon / 1000 * 50).toFixed(2)),
    certificates,
  };
}
