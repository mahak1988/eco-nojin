/**
 * ============================================================================
 *  MapController — Leaflet map controller hook for GIS functionality
 *  Inspired by agri-moon GIS components
 * ============================================================================
 */

import { useEffect, useRef, useState } from "react";

export interface MapControllerOptions {
  center?: [number, number];
  zoom?: number;
  minZoom?: number;
  maxZoom?: number;
}

export interface MapControllerReturn {
  mapRef: React.RefObject<HTMLDivElement>;
  initialize: () => void;
  updateCenter: (center: [number, number]) => void;
  updateZoom: (zoom: number) => void;
  addLayer: (layerId: string, layer: any) => void;
  removeLayer: (layerId: string) => void;
}

export function useMapController(options: MapControllerOptions = {}): MapControllerReturn {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const layersRef = useRef<Record<string, any>>({});

  const initialize = () => {
    // Placeholder for Leaflet map initialization
    // In production, this would create a Leaflet map instance
    if (mapRef.current && !map) {
      // Map initialization logic would go here
      console.log("Map initialized with options:", options);
    }
  };

  const updateCenter = (center: [number, number]) => {
    if (map) {
      // map.setView(center, map.getZoom());
      console.log("Map center updated to:", center);
    }
  };

  const updateZoom = (zoom: number) => {
    if (map) {
      // map.setZoom(zoom);
      console.log("Map zoom updated to:", zoom);
    }
  };

  const addLayer = (layerId: string, layer: any) => {
    layersRef.current[layerId] = layer;
    console.log(`Layer ${layerId} added`);
  };

  const removeLayer = (layerId: string) => {
    delete layersRef.current[layerId];
    console.log(`Layer ${layerId} removed`);
  };

  useEffect(() => {
    initialize();
  }, []);

  return { mapRef, initialize, updateCenter, updateZoom, addLayer, removeLayer };
}

// MapContainer component using the hook
interface MapContainerProps {
  options?: MapControllerOptions;
  className?: string;
}

export function MapContainer({ options, className }: MapContainerProps): JSX.Element {
  const { mapRef, initialize } = useMapController(options);

  return (
    <div
      ref={mapRef}
      className={className}
      onClick={initialize}
      style={{ minHeight: "400px", width: "100%" }}
    >
      {/* Map will be rendered here */}
      <div className="flex h-full items-center justify-center bg-gray-100 text-gray-500">
        Map Placeholder - Leaflet integration pending
      </div>
    </div>
  );
}