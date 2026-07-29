"use client";

import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, useMap, Marker, Popup, GeoJSON, Polygon, Polyline, WMSTileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useGisStore } from '@/store/gis/useGisStore';
import { Button } from '@/components/ui/button';
import { Edit3, Ruler, Check, X, ZoomIn, ZoomOut, Maximize } from 'lucide-react';

import { CHART, GIS } from '@econojin/ui/lib/chart-colors';

// Fix Leaflet default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Helper function to calculate distance (Haversine formula)
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// Helper function to calculate polygon area
function calculateArea(coordinates: [number, number][]): number {
  let area = 0;
  const n = coordinates.length;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    area += coordinates[i][0] * coordinates[j][1];
    area -= coordinates[j][0] * coordinates[i][1];
  }
  area = Math.abs(area) / 2;
  const avgLat = coordinates.reduce((sum, p) => sum + p[0], 0) / n;
  return area * 111320 * 111320 * Math.cos(avgLat * Math.PI / 180);
}

// ✅ RELIABLE MAP CLICK HANDLER USING useMapEvents
function MapClickHandler({ 
  drawingMode, 
  currentPoints, 
  setCurrentPoints, 
  addMeasurement, 
  addFeature, 
  setDrawingMode 
}: any) {
  useMapEvents({
    click: (e) => {
      if (!drawingMode) return;
      
      const { lat, lng } = e.latlng;
      const newPoints = [...currentPoints, [lat, lng] as [number, number]];
      setCurrentPoints(newPoints);

      if (drawingMode === 'line' && newPoints.length === 2) {
        const distance = calculateDistance(
          currentPoints[0][0], currentPoints[0][1],
          lat, lng
        );
        
        addMeasurement({
          type: 'line',
          points: newPoints,
          distance: distance,
          timestamp: new Date().toISOString()
        });
        
        setCurrentPoints([]);
        setDrawingMode(null);
      }
    }
  });
  return null;
}

// Change cursor to crosshair when drawing
function MapCursor({ drawingMode }: { drawingMode: string | null }) {
  const map = useMap();
  useEffect(() => {
    if (drawingMode) {
      map.getContainer().style.cursor = 'crosshair';
    } else {
      map.getContainer().style.cursor = '';
    }
    return () => {
      map.getContainer().style.cursor = '';
    };
  }, [drawingMode, map]);
  return null;
}

// Sync map with external state
function MapSync({ center, zoom, onCenterChange, onZoomChange }: any) {
  const map = useMap();
  
  useEffect(() => {
    if (map.getZoom() !== zoom) {
      map.setZoom(zoom);
    }
  }, [zoom, map]);
  
  useEffect(() => {
    const handleMove = () => {
      const c = map.getCenter();
      onCenterChange({ lat: c.lat, lng: c.lng });
    };
    
    const handleZoom = () => {
      onZoomChange(map.getZoom());
    };
    
    map.on('moveend', handleMove);
    map.on('zoomend', handleZoom);
    
    return () => {
      map.off('moveend', handleMove);
      map.off('zoomend', handleZoom);
    };
  }, [map, onCenterChange, onZoomChange]);
  
  return null;
}

// Layer configurations
const layerConfigs: Record<string, { type: string; url: string; params?: any; attribution: string }> = {
  'Sentinel-2': {
    type: 'wms',
    url: 'https://tiles.maps.eox.at/wms',
    params: { layers: 's2cloudless', format: 'image/jpeg', transparent: false },
    attribution: 'Sentinel-2 Cloudless | EOX'
  },
  'Sentinel-2 TMS': {
    type: 'tile',
    url: 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless/default/g/WebMercatorQuad/{z}/{y}/{x}.jpg',
    attribution: 'Sentinel-2 Cloudless | EOX'
  },
  'Landsat': {
    type: 'tile',
    url: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}',
    attribution: 'USGS Landsat'
  },
  'Esri Satellite': {
    type: 'tile',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Esri World Imagery'
  },
  'Topographic': {
    type: 'tile',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '© OpenTopoMap (CC-BY-SA)'
  },
  'OSM': {
    type: 'tile',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors'
  }
};

export function InteractiveMap({ center, zoom, onCenterChange, onZoomChange }: any) {
  const { drawnFeatures, selectedLayer, addFeature, addMeasurement } = useGisStore();
  const [drawingMode, setDrawingMode] = useState<string | null>(null);
  const [currentPoints, setCurrentPoints] = useState<[number, number][]>([]);
  const mapRef = useRef<L.Map | null>(null);

  const currentLayerConfig = layerConfigs[selectedLayer] || layerConfigs['Esri Satellite'];

  const finishPolygon = () => {
    if (currentPoints.length < 3) return;
    
    const area = calculateArea(currentPoints);
    let perimeter = 0;
    for (let i = 0; i < currentPoints.length; i++) {
      const next = (i + 1) % currentPoints.length;
      perimeter += calculateDistance(
        currentPoints[i][0], currentPoints[i][1],
        currentPoints[next][0], currentPoints[next][1]
      );
    }
    
    const centerLat = currentPoints.reduce((sum, p) => sum + p[0], 0) / currentPoints.length;
    const centerLng = currentPoints.reduce((sum, p) => sum + p[1], 0) / currentPoints.length;
    
    addFeature({
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [[...currentPoints.map(p => [p[1], p[0]]), [currentPoints[0][1], currentPoints[0][0]]]]
      },
      properties: {
        type: 'farm',
        area: area,
        area_hectares: area / 10000,
        perimeter: perimeter,
        center: [centerLng, centerLat],
        created_at: new Date().toISOString()
      }
    });
    
    setCurrentPoints([]);
    setDrawingMode(null);
  };

  const cancelDrawing = () => {
    setDrawingMode(null);
    setCurrentPoints([]);
  };

  const handleZoomIn = () => {
    if (mapRef.current) mapRef.current.zoomIn();
  };

  const handleZoomOut = () => {
    if (mapRef.current) mapRef.current.zoomOut();
  };

  const handleFitBounds = () => {
    if (mapRef.current && drawnFeatures.length > 0) {
      const group = L.featureGroup(drawnFeatures.map((f: any) => L.geoJSON(f)));
      mapRef.current.fitBounds(group.getBounds().pad(0.1));
    } else if (mapRef.current) {
      mapRef.current.setView([35.6892, 51.3890], 10);
    }
  };

  return (
    <>
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={zoom}
        style={{ height: '100%', width: '100%', background: GIS.background }}
        className="z-0"
        ref={mapRef}
        zoomControl={false}
      >
        <MapSync center={center} zoom={zoom} onCenterChange={onCenterChange} onZoomChange={onZoomChange} />
        <MapCursor drawingMode={drawingMode} />
        
        {/* ✅ This is the magic component that makes clicks work reliably */}
        <MapClickHandler 
          drawingMode={drawingMode}
          currentPoints={currentPoints}
          setCurrentPoints={setCurrentPoints}
          addMeasurement={addMeasurement}
          addFeature={addFeature}
          setDrawingMode={setDrawingMode}
        />
        
        {currentLayerConfig.type === 'wms' ? (
          <WMSTileLayer
            key={selectedLayer}
            url={currentLayerConfig.url}
            params={currentLayerConfig.params}
            attribution={currentLayerConfig.attribution}
          />
        ) : (
          <TileLayer
            key={selectedLayer}
            url={currentLayerConfig.url}
            attribution={currentLayerConfig.attribution}
          />
        )}
        
        {drawnFeatures.map((feature: any, idx: number) => (
          <GeoJSON
            key={idx}
            data={feature}
            style={{ color: CHART.emerald, weight: 2, fillOpacity: 0.3, fillColor: CHART.emerald }}
          >
            <Popup>
              <div className="text-right" dir="rtl">
                <strong>{feature.properties?.name || `مزرعه ${idx + 1}`}</strong>
                <br />
                مساحت: {feature.properties?.area_hectares?.toFixed(2) || 0} هکتار
                <br />
                محیط: {feature.properties?.perimeter?.toFixed(0) || 0} متر
                {feature.properties?.crop_type && <><br />محصول: {feature.properties.crop_type}</>}
              </div>
            </Popup>
          </GeoJSON>
        ))}
        
        {currentPoints.length > 0 && (
          <>
            {drawingMode === 'line' && currentPoints.length >= 2 && (
              <Polyline positions={currentPoints} color={CHART.blue} weight={3} />
            )}
            {drawingMode === 'polygon' && currentPoints.length >= 2 && (
              <Polygon positions={currentPoints} color={CHART.emerald} weight={2} fillOpacity={0.2} />
            )}
            {currentPoints.map((point, idx) => (
              <Marker key={idx} position={point}>
                <Popup>نقطه {idx + 1}</Popup>
              </Marker>
            ))}
          </>
        )}
        
        {/* Zoom Controls */}
        <div className="absolute top-4 right-4 flex flex-col gap-2 z-[1000]">
          <Button size="icon" variant="secondary" className="bg-slate-900/90 border border-slate-700 hover:bg-slate-800 shadow-lg" onClick={handleZoomIn}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button size="icon" variant="secondary" className="bg-slate-900/90 border border-slate-700 hover:bg-slate-800 shadow-lg" onClick={handleZoomOut}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button size="icon" variant="secondary" className="bg-slate-900/90 border border-slate-700 hover:bg-slate-800 shadow-lg" onClick={handleFitBounds}>
            <Maximize className="w-4 h-4" />
          </Button>
        </div>

        {/* Drawing Controls */}
        <div className="absolute top-4 left-4 bg-slate-900/95 border border-slate-700 rounded-lg p-2 z-[1000] flex flex-col gap-2 shadow-lg">
          <Button
            size="sm"
            variant={drawingMode === 'polygon' ? 'default' : 'outline'}
            onClick={() => {
              setDrawingMode(drawingMode === 'polygon' ? null : 'polygon');
              setCurrentPoints([]);
            }}
            className="gap-2"
          >
            <Edit3 className="w-4 h-4" />
            رسم مزرعه
          </Button>
          
          <Button
            size="sm"
            variant={drawingMode === 'line' ? 'default' : 'outline'}
            onClick={() => {
              setDrawingMode(drawingMode === 'line' ? null : 'line');
              setCurrentPoints([]);
            }}
            className="gap-2"
          >
            <Ruler className="w-4 h-4" />
            اندازه‌گیری
          </Button>
          
          {drawingMode === 'polygon' && currentPoints.length >= 3 && (
            <Button size="sm" variant="default" onClick={finishPolygon} className="gap-2 bg-emerald-600 hover:bg-emerald-700">
              <Check className="w-4 h-4" />
              ثبت مزرعه ({currentPoints.length})
            </Button>
          )}
          
          {drawingMode && (
            <Button size="sm" variant="destructive" onClick={cancelDrawing} className="gap-2">
              <X className="w-4 h-4" />
              لغو
            </Button>
          )}
          
          {drawingMode && (
            <div className="text-xs text-slate-400 text-center px-2 py-1 bg-slate-800 rounded mt-1">
              {drawingMode === 'polygon' ? 'روی نقشه کلیک کنید' : 'دو نقطه انتخاب کنید'}
            </div>
          )}
        </div>
      </MapContainer>
    </>
  );
}
