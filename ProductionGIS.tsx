"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Circle,
  Popup,
  Polyline,
  Polygon,
  Marker,
  ScaleControl,
  useMapEvents,
  useMap,
  ZoomControl,
} from "react-leaflet";
import type { LeafletMouseEvent, Map as LeafletMap } from "leaflet";
import {
  MapPin,
  Ruler,
  Square,
  Layers,
  Search,
  Download,
  Eye,
  EyeOff,
  Loader2,
  Save,
  Trash2,
  Navigation,
  Target,
  X,
  Check,
  Plus,
  FileText,
  Globe,
  Printer,
  Crosshair,
  Flame,
} from "lucide-react";
import { gisStorage, type SavedLocation } from "@/lib/gisStorage";

// ============ لایه‌های پایه ============
const BASE_LAYERS = {
  satellite_esri: {
    name: "🛰️ تصویر ماهواره‌ای (Esri)",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "&copy; Esri",
    maxZoom: 19,
  },
  osm: {
    name: "🗺️ OpenStreetMap",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap",
    maxZoom: 19,
  },
  terrain: {
    name: "⛰️ توپوگرافی",
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenTopoMap",
    maxZoom: 17,
  },
  dark: {
    name: "🌙 حالت تاریک",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution: "&copy; CARTO",
    maxZoom: 19,
  },
};

// ============ لایه‌های پوششی ============
const OVERLAY_LAYERS = {
  landcover: {
    name: "🌱 پوشش گیاهی",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Land_Cover/MapServer/tile/{z}/{y}/{x}",
    opacity: 0.6,
    color: "#10b981",
    description: "کاربری اراضی",
  },
  terrain_overlay: {
    name: "⛰️ مدل ارتفاعی",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
    opacity: 0.5,
    color: "#8b5cf6",
    description: "توپوگرافی",
  },
  hydro: {
    name: "💧 شبکه آبراهه‌ها",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Hydrography/MapServer/tile/{z}/{y}/{x}",
    opacity: 0.8,
    color: "#3b82f6",
    description: "رودخانه‌ها",
  },
  boundaries: {
    name: "🏛️ مرزها",
    url: "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    opacity: 0.9,
    color: "#ef4444",
    description: "مرزهای سیاسی",
  },
};

// ============ داده‌های نقشه حرارتی ============
const HEATMAP_DATA = [
  { lat: 36.3, lng: 59.6, intensity: 0.8, name: "مشهد" },
  { lat: 33.5, lng: 54.5, intensity: 0.3, name: "دشت کویر" },
  { lat: 31.5, lng: 51.5, intensity: 0.9, name: "زاگرس" },
  { lat: 28.5, lng: 60.5, intensity: 0.2, name: "بلوچستان" },
  { lat: 38.0, lng: 46.5, intensity: 0.7, name: "آذربایجان" },
  { lat: 29.6, lng: 52.5, intensity: 0.6, name: "فارس" },
  { lat: 35.7, lng: 51.4, intensity: 0.85, name: "تهران" },
  { lat: 32.6, lng: 51.7, intensity: 0.75, name: "اصفهان" },
  { lat: 36.8, lng: 50.6, intensity: 0.65, name: "گیلان" },
  { lat: 34.3, lng: 47.1, intensity: 0.55, name: "کرمانشاه" },
];

const LOCATION_CATEGORIES = {
  field: { label: "🌾 مزرعه", color: "#10b981" },
  structure: { label: "🏗️ سازه", color: "#3b82f6" },
  sample: { label: "🧪 نمونه", color: "#f59e0b" },
  observation: { label: "👁️ مشاهده", color: "#8b5cf6" },
  custom: { label: "📍 دلخواه", color: "#64748b" },
};

// ============ توابع کمکی ============
function createColoredIcon(color: string) {
  if (typeof window === "undefined") return null;
  try {
    const L = require("leaflet");
    return L.divIcon({
      className: "custom-marker",
      html: `<div style="background:${color};width:24px;height:24px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4);"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  } catch {
    return null;
  }
}

function getHeatColor(intensity: number): string {
  if (intensity < 0.2) return "#3b82f6";
  if (intensity < 0.4) return "#06b6d4";
  if (intensity < 0.6) return "#10b981";
  if (intensity < 0.8) return "#f59e0b";
  return "#ef4444";
}

// ============ کامپوننت‌های داخلی ============
function MapEventHandler({
  measureMode,
  onMapClick,
  onMouseMove,
}: {
  measureMode: string;
  onMapClick: (e: LeafletMouseEvent) => void;
  onMouseMove: (e: LeafletMouseEvent) => void;
}) {
  useMapEvents({
    click: onMapClick,
    mousemove: onMouseMove,
  });
  return null;
}

function MapUpdater({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
}

// ============ کامپوننت اصلی ============
export default function ProductionGIS() {
  const [isClient, setIsClient] = useState(false);
  const [baseLayer, setBaseLayer] = useState<keyof typeof BASE_LAYERS>("satellite_esri");
  const [overlays, setOverlays] = useState<Record<string, boolean>>({});
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showLayerPanel, setShowLayerPanel] = useState(false);
  const [showSavedPanel, setShowSavedPanel] = useState(false);

  const [measureMode, setMeasureMode] = useState<"none" | "distance" | "area" | "radius">("none");
  const [measurePoints, setMeasurePoints] = useState<[number, number][]>([]);
  const [measureResult, setMeasureResult] = useState("");

  const [mousePosition, setMousePosition] = useState<{ lat: number; lng: number } | null>(null);
  const [savedLocations, setSavedLocations] = useState<SavedLocation[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [pendingSavePoint, setPendingSavePoint] = useState<[number, number] | null>(null);
  const [saveForm, setSaveForm] = useState({
    name: "",
    description: "",
    category: "field" as keyof typeof LOCATION_CATEGORIES,
    notes: "",
    tags: "",
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const [mapCenter, setMapCenter] = useState<[number, number]>([32.5, 54.5]);
  const [zoom, setZoom] = useState(6);
  const mapRef = useRef<LeafletMap | null>(null);

  // Initialize
  useEffect(() => {
    setIsClient(true);
    setSavedLocations(gisStorage.getLocations());

    try {
      const L = require("leaflet");
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });
    } catch (e) {
      console.warn("Leaflet setup skipped:", e);
    }
  }, []);

  // ============ Measurement Functions ============
  const calculateDistance = useCallback((points: [number, number][]) => {
    if (points.length < 2) return { value: 0, formatted: "0 m" };
    let total = 0;
    for (let i = 1; i < points.length; i++) {
      const [lat1, lng1] = points[i - 1];
      const [lat2, lng2] = points[i];
      const R = 6371000;
      const dLat = ((lat2 - lat1) * Math.PI) / 180;
      const dLng = ((lng2 - lng1) * Math.PI) / 180;
      const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
      total += R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }
    return {
      value: total,
      formatted: total > 1000 ? `${(total / 1000).toFixed(2)} km` : `${total.toFixed(0)} m`,
    };
  }, []);

  const calculateArea = useCallback((points: [number, number][]) => {
    if (points.length < 3) return { value: 0, formatted: "0 m²" };
    let area = 0;
    const n = points.length;
    for (let i = 0; i < n; i++) {
      const [lat1, lng1] = points[i];
      const [lat2, lng2] = points[(i + 1) % n];
      area += (lng2 - lng1) * (2 + Math.sin((lat1 * Math.PI) / 180) + Math.sin((lat2 * Math.PI) / 180));
    }
    area = Math.abs((area * 6371000 * 6371000) / 2);
    return {
      value: area,
      formatted:
        area > 1000000
          ? `${(area / 1000000).toFixed(2)} km²`
          : area > 10000
          ? `${(area / 10000).toFixed(2)} ha`
          : `${area.toFixed(0)} m²`,
    };
  }, []);

  const calculateRadius = useCallback((points: [number, number][]) => {
    if (points.length < 2) return { value: 0, formatted: "0 m", area: 0 };
    const [lat1, lng1] = points[0];
    const [lat2, lng2] = points[1];
    const R = 6371000;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
    const distance = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const area = Math.PI * distance * distance;
    return {
      value: distance,
      area: area,
      formatted: `شعاع: ${distance > 1000 ? (distance / 1000).toFixed(2) + " km" : distance.toFixed(0) + " m"}`,
    };
  }, []);

  // ============ Map Event Handlers ============
  const handleMapClick = useCallback(
    (e: LeafletMouseEvent) => {
      if (measureMode === "none") return;

      const { lat, lng } = e.latlng;
      const newPoints = [...measurePoints, [lat, lng] as [number, number]];
      setMeasurePoints(newPoints);

      let result;
      if (measureMode === "distance" && newPoints.length >= 2) {
        result = calculateDistance(newPoints);
      } else if (measureMode === "area" && newPoints.length >= 3) {
        result = calculateArea(newPoints);
      } else if (measureMode === "radius" && newPoints.length >= 2) {
        result = calculateRadius(newPoints);
        if (newPoints.length > 2) {
          setMeasurePoints([newPoints[0], newPoints[newPoints.length - 1]]);
        }
      }

      if (result) setMeasureResult(result.formatted);
    },
    [measureMode, measurePoints, calculateDistance, calculateArea, calculateRadius]
  );

  const handleMouseMove = useCallback((e: LeafletMouseEvent) => {
    setMousePosition({ lat: e.latlng.lat, lng: e.latlng.lng });
  }, []);

  const startMeasure = (mode: "distance" | "area" | "radius") => {
    setMeasureMode(mode);
    setMeasurePoints([]);
    setMeasureResult("");
  };

  const resetMeasure = () => {
    if (measureResult && measurePoints.length >= 2) {
      gisStorage.saveMeasurement({
        type: measureMode as any,
        points: measurePoints,
        result: measurePoints.length,
        unit: measureMode === "area" ? "m²" : "m",
        formattedResult: measureResult,
      });
    }
    setMeasureMode("none");
    setMeasurePoints([]);
    setMeasureResult("");
  };

  const finishAndSaveMeasure = () => {
    if (measureResult && measurePoints.length >= 2) {
      gisStorage.saveMeasurement({
        type: measureMode as any,
        points: measurePoints,
        result: measurePoints.length,
        unit: measureMode === "area" ? "m²" : "m",
        formattedResult: measureResult,
      });
    }
    resetMeasure();
  };

  // ============ Location Functions ============
  const openSaveDialog = (point?: [number, number]) => {
    if (point) {
      setPendingSavePoint(point);
    } else if (mousePosition) {
      setPendingSavePoint([mousePosition.lat, mousePosition.lng]);
    } else {
      alert("لطفاً ابتدا روی نقشه کلیک کنید");
      return;
    }
    setSaveForm({ name: "", description: "", category: "field", notes: "", tags: "" });
    setShowSaveDialog(true);
  };

  const handleSaveLocation = () => {
    if (!pendingSavePoint || !saveForm.name.trim()) {
      alert("لطفاً نام مکان را وارد کنید");
      return;
    }

    gisStorage.saveLocation({
      name: saveForm.name,
      description: saveForm.description,
      category: saveForm.category,
      coordinates: pendingSavePoint,
      notes: saveForm.notes,
      tags: saveForm.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    });

    setSavedLocations(gisStorage.getLocations());
    setShowSaveDialog(false);
    setPendingSavePoint(null);
  };

  const handleDeleteLocation = (id: string) => {
    if (confirm("آیا از حذف این مکان مطمئن هستید؟")) {
      gisStorage.deleteLocation(id);
      setSavedLocations(gisStorage.getLocations());
    }
  };

  const flyToLocation = (loc: SavedLocation) => {
    setMapCenter(loc.coordinates);
    setZoom(loc.zoom || 15);
    setShowSavedPanel(false);
  };

  // ============ Search ============
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=5&accept-language=fa`
      );
      const data = await response.json();
      setSearchResults(data);
      if (data.length > 0) {
        setMapCenter([parseFloat(data[0].lat), parseFloat(data[0].lon)]);
        setZoom(12);
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  // ============ Export ============
  const exportGeoJSON = () => {
    const content = gisStorage.exportAsGeoJSON();
    gisStorage.downloadFile(content, `econojin_${Date.now()}.geojson`, "application/geo+json");
  };

  const exportKML = () => {
    const content = gisStorage.exportAsKML();
    gisStorage.downloadFile(content, `econojin_${Date.now()}.kml`, "application/vnd.google-earth.kml+xml");
  };

  const exportHTMLReport = () => {
    const locations = gisStorage.getLocations();
    const html = `<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<title>گزارش GIS اکو نوژین</title>
<style>
  body { font-family: Tahoma; padding: 30px; direction: rtl; background: #0f172a; color: #e2e8f0; }
  h1 { color: #10b981; }
  h2 { color: #3b82f6; margin-top: 30px; }
  table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #1e293b; }
  th, td { border: 1px solid #334155; padding: 12px; text-align: right; }
  th { background: #10b981; color: white; }
  @media print { body { background: white; color: black; } }
</style>
</head>
<body>
<h1>🌍 گزارش GIS اکو نوژین</h1>
<p>تاریخ: ${new Date().toLocaleDateString("fa-IR")}</p>
<h2>📍 مکان‌های ذخیره‌شده (${locations.length})</h2>
<table>
<tr><th>نام</th><th>دسته</th><th>مختصات</th></tr>
${locations
  .map(
    (l) => `<tr>
  <td><strong>${l.name}</strong></td>
  <td>${(LOCATION_CATEGORIES as any)[l.category]?.label || l.category}</td>
  <td style="direction:ltr;text-align:left">${l.coordinates[0].toFixed(5)}, ${l.coordinates[1].toFixed(5)}</td>
</tr>`
  )
  .join("")}
</table>
</body></html>`;

    gisStorage.downloadFile(html, `econojin_report_${Date.now()}.html`, "text/html");
  };

  const goToMyLocation = () => {
    if (!navigator.geolocation) {
      alert("مرورگر شما از موقعیت‌یابی پشتیبانی نمی‌کند");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setMapCenter([position.coords.latitude, position.coords.longitude]);
        setZoom(15);
      },
      (error) => alert("خطا: " + error.message)
    );
  };

  // SSR Prevention
  if (!isClient) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mb-4"></div>
          <p className="text-slate-400">در حال بارگذاری نقشه...</p>
        </div>
      </div>
    );
  }

  // ============ RENDER ============
  return (
    <div className="relative h-full">
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
        zoomControl={false}
        ref={(map: any) => {
          mapRef.current = map;
        }}
      >
        <MapEventHandler measureMode={measureMode} onMapClick={handleMapClick} onMouseMove={handleMouseMove} />
        <MapUpdater center={mapCenter} zoom={zoom} />

        {/* Zoom Control - سمت چپ */}
        <ZoomControl position="topleft" />

        {/* Base Layer */}
        <TileLayer
          key={baseLayer}
          url={BASE_LAYERS[baseLayer].url}
          attribution={BASE_LAYERS[baseLayer].attribution}
          maxZoom={BASE_LAYERS[baseLayer].maxZoom}
        />

        {/* Overlay Layers */}
        {Object.entries(overlays).map(([key, visible]) => {
          if (!visible) return null;
          const layer = OVERLAY_LAYERS[key as keyof typeof OVERLAY_LAYERS];
          return <TileLayer key={key} url={layer.url} opacity={layer.opacity} />;
        })}

        {/* Heatmap - با CircleMarker */}
        {showHeatmap &&
          HEATMAP_DATA.map((point, idx) => {
            const color = getHeatColor(point.intensity);
            const radius = 3000 + point.intensity * 20000;
            return (
              <Circle
                key={`heat-${idx}`}
                center={[point.lat, point.lng]}
                radius={radius}
                pathOptions={{
                  color: color,
                  fillColor: color,
                  fillOpacity: 0.35,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="p-2 text-slate-900">
                    <p className="font-bold">{point.name}</p>
                    <p className="text-sm">شدت: {(point.intensity * 100).toFixed(0)}%</p>
                    <p className="text-xs text-slate-600">
                      {point.lat.toFixed(3)}, {point.lng.toFixed(3)}
                    </p>
                  </div>
                </Popup>
              </Circle>
            );
          })}

        {/* Saved Locations */}
        {savedLocations.map((loc) => {
          const cat = LOCATION_CATEGORIES[loc.category];
          const icon = createColoredIcon(cat?.color || "#64748b");
          return (
            <Marker key={loc.id} position={loc.coordinates} icon={icon || undefined}>
              <Popup>
                <div className="p-2 text-slate-900 min-w-[200px]">
                  <h4 className="font-bold text-lg mb-1">{loc.name}</h4>
                  <p className="text-xs text-slate-600 mb-2">{cat?.label}</p>
                  {loc.description && <p className="text-sm mb-2">{loc.description}</p>}
                  {loc.notes && <p className="text-xs text-slate-500 mb-2">📝 {loc.notes}</p>}
                  <p className="text-xs text-slate-400" style={{ direction: "ltr" }}>
                    📍 {loc.coordinates[0].toFixed(5)}, {loc.coordinates[1].toFixed(5)}
                  </p>
                  <button
                    onClick={() => handleDeleteLocation(loc.id)}
                    className="mt-2 w-full px-2 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
                  >
                    حذف
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Measurement visualization */}
        {measurePoints.map((point, idx) => (
          <Circle
            key={idx}
            center={point}
            radius={
              measureMode === "radius" && idx === 0 && measurePoints.length === 2
                ? calculateRadius(measurePoints).area > 0
                  ? Math.sqrt(calculateRadius(measurePoints).area / Math.PI)
                  : 80
                : 80
            }
            pathOptions={{
              color: measureMode === "radius" && idx === 0 ? "#8b5cf6" : "#f59e0b",
              fillColor: measureMode === "radius" && idx === 0 ? "#8b5cf6" : "#f59e0b",
              fillOpacity: idx === 0 && measureMode === "radius" ? 0.2 : 0.8,
              weight: 2,
            }}
          />
        ))}

        {measureMode === "distance" && measurePoints.length >= 2 && (
          <Polyline positions={measurePoints} pathOptions={{ color: "#f59e0b", weight: 3, dashArray: "10, 10" }} />
        )}
        {measureMode === "area" && measurePoints.length >= 3 && (
          <Polygon
            positions={measurePoints}
            pathOptions={{ color: "#f59e0b", weight: 3, fillColor: "#f59e0b", fillOpacity: 0.3 }}
          />
        )}

        {pendingSavePoint && (
          <Marker position={pendingSavePoint} icon={createColoredIcon("#10b981") || undefined} />
        )}

        <ScaleControl position="bottomright" metric={true} imperial={false} />
      </MapContainer>

      {/* ============ TOP TOOLBAR ============ */}
      <div className="absolute top-4 left-20 right-4 z-[1000] flex flex-col md:flex-row gap-2">
        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex items-center gap-2 flex-1 max-w-xl">
          <Search className="h-4 w-4 text-slate-400 flex-shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            placeholder="جستجوی مکان..."
            className="flex-1 bg-transparent text-white text-sm focus:outline-none min-w-0"
          />
          {isSearching && <Loader2 className="h-4 w-4 animate-spin text-emerald-400 flex-shrink-0" />}
          <button
            onClick={handleSearch}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs rounded-lg font-bold"
          >
            جستجو
          </button>
        </div>

        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 flex items-center gap-2 font-mono">
          <Crosshair className="h-3 w-3 text-emerald-400" />
          {mousePosition ? (
            <>
              <span>{mousePosition.lat.toFixed(5)}</span>
              <span className="text-slate-600">|</span>
              <span>{mousePosition.lng.toFixed(5)}</span>
            </>
          ) : (
            <span className="text-slate-500">موقعیت ماوس</span>
          )}
        </div>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="absolute top-20 left-20 z-[1001] bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 max-w-xl w-full max-h-64 overflow-y-auto">
          {searchResults.map((result, idx) => (
            <button
              key={idx}
              onClick={() => {
                setMapCenter([parseFloat(result.lat), parseFloat(result.lon)]);
                setZoom(13);
                setSearchResults([]);
                setSearchQuery("");
              }}
              className="w-full text-right px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg border-b border-slate-800 last:border-0"
            >
              <div className="font-bold">{result.display_name.split(",")[0]}</div>
              <div className="text-xs text-slate-500 truncate">{result.display_name}</div>
            </button>
          ))}
        </div>
      )}

      {/* ============ LEFT TOOLBAR ============ */}
      <div className="absolute top-28 left-4 z-[1000] flex flex-col gap-2">
        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex flex-col gap-1">
          <button
            onClick={goToMyLocation}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-emerald-400"
            title="موقعیت من"
          >
            <Navigation className="h-4 w-4" />
          </button>
          <button
            onClick={() => {
              setMapCenter([32.5, 54.5]);
              setZoom(6);
            }}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-emerald-400"
            title="نمای ایران"
          >
            <Globe className="h-4 w-4" />
          </button>
        </div>

        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex flex-col gap-1">
          <button
            onClick={() => startMeasure("distance")}
            className={`p-2 rounded-lg ${
              measureMode === "distance" ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"
            }`}
            title="اندازه‌گیری مسافت"
          >
            <Ruler className="h-4 w-4" />
          </button>
          <button
            onClick={() => startMeasure("area")}
            className={`p-2 rounded-lg ${
              measureMode === "area" ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"
            }`}
            title="اندازه‌گیری مساحت"
          >
            <Square className="h-4 w-4" />
          </button>
          <button
            onClick={() => startMeasure("radius")}
            className={`p-2 rounded-lg ${
              measureMode === "radius" ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"
            }`}
            title="اندازه‌گیری شعاع"
          >
            <Target className="h-4 w-4" />
          </button>
          {measureMode !== "none" && (
            <>
              <div className="border-t border-slate-700 my-1" />
              <button
                onClick={finishAndSaveMeasure}
                className="p-2 rounded-lg text-emerald-400 hover:bg-slate-800"
                title="ذخیره"
              >
                <Check className="h-4 w-4" />
              </button>
              <button onClick={resetMeasure} className="p-2 rounded-lg text-red-400 hover:bg-slate-800" title="لغو">
                <X className="h-4 w-4" />
              </button>
            </>
          )}
        </div>

        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex flex-col gap-1">
          <button
            onClick={() => openSaveDialog()}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-emerald-400"
            title="ثبت مکان"
          >
            <Save className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowSavedPanel(!showSavedPanel)}
            className={`p-2 rounded-lg relative ${
              showSavedPanel ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"
            }`}
            title={`مکان‌های من (${savedLocations.length})`}
          >
            <MapPin className="h-4 w-4" />
            {savedLocations.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-emerald-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center">
                {savedLocations.length}
              </span>
            )}
          </button>
        </div>

        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex flex-col gap-1">
          <button
            onClick={() => setShowLayerPanel(!showLayerPanel)}
            className={`p-2 rounded-lg ${
              showLayerPanel ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"
            }`}
            title="لایه‌ها"
          >
            <Layers className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`p-2 rounded-lg ${
              showHeatmap ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"
            }`}
            title="نقشه حرارتی"
          >
            <Flame className="h-4 w-4" />
          </button>
          <button
            onClick={() => window.print()}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-emerald-400"
            title="چاپ"
          >
            <Printer className="h-4 w-4" />
          </button>
          <div className="relative group">
            <button className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-emerald-400 w-full">
              <Download className="h-4 w-4" />
            </button>
            <div className="absolute top-0 right-full mr-1 bg-slate-900 border border-slate-700 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-[1001] min-w-[180px]">
              <button
                onClick={exportGeoJSON}
                className="w-full px-3 py-2 text-right text-sm text-slate-300 hover:bg-slate-800 first:rounded-t-xl flex items-center gap-2"
              >
                <FileText className="h-4 w-4" /> GeoJSON
              </button>
              <button
                onClick={exportKML}
                className="w-full px-3 py-2 text-right text-sm text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              >
                <Globe className="h-4 w-4" /> KML
              </button>
              <button
                onClick={exportHTMLReport}
                className="w-full px-3 py-2 text-right text-sm text-slate-300 hover:bg-slate-800 last:rounded-b-xl flex items-center gap-2"
              >
                <FileText className="h-4 w-4" /> گزارش HTML
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ============ MEASUREMENT RESULT ============ */}
      {measureResult && (
        <div className="absolute bottom-20 left-4 z-[1000] bg-amber-500/95 backdrop-blur border border-amber-400 rounded-xl p-4 text-white min-w-[250px]">
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-xs text-amber-100 mb-1">
                {measureMode === "distance" ? "📏 مسافت" : measureMode === "area" ? "📐 مساحت" : "⭕ شعاع"}
              </p>
              <p className="text-2xl font-black">{measureResult}</p>
              <p className="text-xs text-amber-100 mt-1">نقاط: {measurePoints.length}</p>
            </div>
            <button onClick={resetMeasure} className="text-amber-100 hover:text-white">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* ============ MEASURE INSTRUCTIONS ============ */}
      {measureMode !== "none" && (
        <div className="absolute top-28 left-1/2 -translate-x-1/2 z-[1000] bg-amber-500/95 backdrop-blur border border-amber-400 rounded-xl p-4 text-white pointer-events-none">
          <p className="font-bold mb-1">
            {measureMode === "distance"
              ? "📏 اندازه‌گیری مسافت"
              : measureMode === "area"
              ? "📐 اندازه‌گیری مساحت"
              : "⭕ اندازه‌گیری شعاع"}
          </p>
          <p className="text-sm">
            {measureMode === "distance" && "حداقل ۲ نقطه کلیک کنید"}
            {measureMode === "area" && "حداقل ۳ نقطه کلیک کنید"}
            {measureMode === "radius" && "مرکز و یک نقطه روی محیط"}
          </p>
          <p className="text-xs mt-2 text-amber-100">نقاط: {measurePoints.length}</p>
        </div>
      )}

      {/* ============ LAYER PANEL ============ */}
      {showLayerPanel && (
        <div className="absolute top-4 right-4 z-[1000] bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-4 w-80 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="h-5 w-5 text-emerald-400" />
              لایه‌ها
            </h3>
            <button onClick={() => setShowLayerPanel(false)} className="text-slate-400 hover:text-white">
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="mb-4">
            <p className="text-xs text-slate-400 mb-2 uppercase font-bold">لایه پایه</p>
            <div className="space-y-1">
              {Object.entries(BASE_LAYERS).map(([key, layer]) => (
                <button
                  key={key}
                  onClick={() => setBaseLayer(key as keyof typeof BASE_LAYERS)}
                  className={`w-full text-right px-3 py-2 rounded-lg text-sm ${
                    baseLayer === key ? "bg-emerald-600 text-white" : "text-slate-300 hover:bg-slate-800"
                  }`}
                >
                  {layer.name}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase font-bold">لایه‌های پوششی</p>
            <div className="space-y-1">
              {Object.entries(OVERLAY_LAYERS).map(([key, layer]) => (
                <button
                  key={key}
                  onClick={() => setOverlays((prev) => ({ ...prev, [key]: !prev[key] }))}
                  className={`w-full text-right px-3 py-2 rounded-lg text-sm ${
                    overlays[key] ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: layer.color }} />
                        <span>{layer.name}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1 mr-5">{layer.description}</p>
                    </div>
                    {overlays[key] ? (
                      <Eye className="h-4 w-4 text-emerald-400" />
                    ) : (
                      <EyeOff className="h-4 w-4" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ============ SAVED LOCATIONS PANEL ============ */}
      {showSavedPanel && (
        <div className="absolute top-4 right-4 z-[1000] bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-4 w-80 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <MapPin className="h-5 w-5 text-emerald-400" />
              مکان‌های من ({savedLocations.length})
            </h3>
            <button onClick={() => setShowSavedPanel(false)} className="text-slate-400 hover:text-white">
              <X className="h-5 w-5" />
            </button>
          </div>

          <button
            onClick={() => openSaveDialog()}
            className="w-full mb-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-2"
          >
            <Plus className="h-4 w-4" /> ثبت مکان جدید
          </button>

          {savedLocations.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <MapPin className="h-12 w-12 mx-auto mb-2 opacity-30" />
              <p className="text-sm">هنوز مکانی ثبت نکرده‌اید</p>
            </div>
          ) : (
            <div className="space-y-2">
              {savedLocations.map((loc) => {
                const cat = LOCATION_CATEGORIES[loc.category];
                return (
                  <div key={loc.id} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cat?.color }} />
                          <h4 className="font-bold text-white text-sm">{loc.name}</h4>
                        </div>
                        <p className="text-xs text-slate-400">{cat?.label}</p>
                      </div>
                      <button
                        onClick={() => handleDeleteLocation(loc.id)}
                        className="text-slate-500 hover:text-red-400 p-1"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                    {loc.description && <p className="text-xs text-slate-300 mb-2">{loc.description}</p>}
                    <button
                      onClick={() => flyToLocation(loc)}
                      className="w-full py-1 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded text-xs font-bold"
                    >
                      نمایش روی نقشه
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ============ SAVE DIALOG ============ */}
      {showSaveDialog && pendingSavePoint && (
        <div className="absolute inset-0 z-[2000] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Save className="h-5 w-5 text-emerald-400" />
                ثبت مکان جدید
              </h3>
              <button onClick={() => setShowSaveDialog(false)} className="text-slate-400 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div
              className="bg-slate-800/50 rounded-lg p-3 mb-4 text-xs text-slate-400 font-mono"
              style={{ direction: "ltr" }}
            >
              📍 {pendingSavePoint[0].toFixed(5)}, {pendingSavePoint[1].toFixed(5)}
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-bold text-white mb-1">نام مکان *</label>
                <input
                  type="text"
                  value={saveForm.name}
                  onChange={(e) => setSaveForm({ ...saveForm, name: e.target.value })}
                  placeholder="مثال: مزرعه گندم شمالی"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:border-emerald-500 focus:outline-none"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-1">دسته‌بندی</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(LOCATION_CATEGORIES).map(([key, cat]) => (
                    <button
                      key={key}
                      onClick={() => setSaveForm({ ...saveForm, category: key as any })}
                      className={`px-3 py-2 rounded-lg text-xs font-bold ${
                        saveForm.category === key
                          ? "bg-emerald-600 text-white"
                          : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                      }`}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-1">توضیحات</label>
                <input
                  type="text"
                  value={saveForm.description}
                  onChange={(e) => setSaveForm({ ...saveForm, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-1">یادداشت‌ها</label>
                <textarea
                  value={saveForm.notes}
                  onChange={(e) => setSaveForm({ ...saveForm, notes: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:border-emerald-500 focus:outline-none resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-1">برچسب‌ها (با کاما)</label>
                <input
                  type="text"
                  value={saveForm.tags}
                  onChange={(e) => setSaveForm({ ...saveForm, tags: e.target.value })}
                  placeholder="گندم, آبیاری, شمالی"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-5">
              <button
                onClick={() => setShowSaveDialog(false)}
                className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm"
              >
                انصراف
              </button>
              <button
                onClick={handleSaveLocation}
                className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-2"
              >
                <Check className="h-4 w-4" /> ذخیره
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}