import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Measurement {
  type: 'line' | 'area';
  points: [number, number][];
  distance?: number;
  area?: number;
  timestamp: string;
}

interface DrawnFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon' | 'Point' | 'LineString';
    coordinates: any;
  };
  properties: {
    type: string;
    area?: number;
    area_hectares?: number;
    perimeter?: number;
    center?: [number, number];
    created_at: string;
    name?: string;
    crop_type?: string;
  };
}

interface GisState {
  mapCenter: { lat: number; lng: number };
  mapZoom: number;
  selectedLayer: string;
  measurements: Measurement[];
  drawnFeatures: DrawnFeature[];
  setMapCenter: (center: { lat: number; lng: number }) => void;
  setMapZoom: (zoom: number) => void;
  setSelectedLayer: (layer: string) => void;
  addMeasurement: (measurement: Measurement) => void;
  addFeature: (feature: DrawnFeature) => void;
  clearAll: () => void;
  exportData: (format: string) => Promise<string>;
}

export const useGisStore = create<GisState>()(
  persist(
    (set, get) => ({
      mapCenter: { lat: 35.6892, lng: 51.3890 },
      mapZoom: 10,
      selectedLayer: 'Esri Satellite',
      measurements: [],
      drawnFeatures: [],
      
      setMapCenter: (center) => set({ mapCenter: center }),
      setMapZoom: (zoom) => set({ mapZoom: zoom }),
      setSelectedLayer: (layer) => set({ selectedLayer: layer }),
      
      addMeasurement: (measurement) => 
        set((state) => ({ measurements: [...state.measurements, measurement] })),
      
      addFeature: (feature) => 
        set((state) => ({ drawnFeatures: [...state.drawnFeatures, feature] })),
      
      clearAll: () => set({ measurements: [], drawnFeatures: [] }),
      
      exportData: async (format: string) => {
        const state = get();
        
        if (format === 'geojson') {
          const geojson = {
            type: 'FeatureCollection',
            features: state.drawnFeatures,
            metadata: {
              exportedAt: new Date().toISOString(),
              format: 'GeoJSON',
              coordinateSystem: 'WGS84',
              totalFeatures: state.drawnFeatures.length,
              totalMeasurements: state.measurements.length
            }
          };
          return JSON.stringify(geojson, null, 2);
        }
        
        if (format === 'kml') {
          let kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Econojin GIS Export</name>
  <description>Exported at ${new Date().toISOString()}</description>
`;
          
          state.drawnFeatures.forEach((feature, idx) => {
            kml += `  <Placemark>
    <name>مزرعه ${idx + 1}</name>
    <description>مساحت: ${feature.properties.area_hectares?.toFixed(2) || 0} هکتار</description>
    <Polygon>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
            ${feature.geometry.coordinates[0].map((c: any) => `${c[0]},${c[1]},0`).join(' ')}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>
`;
          });
          
          kml += `</Document>
</kml>`;
          return kml;
        }
        
        return JSON.stringify(state);
      }
    }),
    {
      name: 'econojin-gis-storage',
    }
  )
);
