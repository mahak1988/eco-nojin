import React from 'react';
import { MapContainer, TileLayer, Circle, Popup, Tooltip } from "react-leaflet";
import { useState, useEffect } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// رفع باگ آیکون‌های پیش‌فرض Leaflet در React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// داده‌های نمونه زیرحوزه‌های خراسان (بعداً از API دریافت می‌شود)
const SUBZONES = [
  { id: 1, name: "سبزوار", lat: 36.214, lon: 57.683, ndvi: 0.62, erosion: 12 },
  { id: 2, name: "نیشابور", lat: 36.214, lon: 58.800, ndvi: 0.48, erosion: 28 },
  { id: 3, name: "مشهد", lat: 36.297, lon: 59.606, ndvi: 0.55, erosion: 18 },
  { id: 4, name: "تربت حیدریه", lat: 35.274, lon: 59.215, ndvi: 0.38, erosion: 42 },
  { id: 5, name: "قائنات", lat: 33.726, lon: 59.178, ndvi: 0.22, erosion: 55 },
];

function getNdviColor(v: number) { return v > 0.5 ? "#10b981" : v > 0.3 ? "#f59e0b" : "#ef4444"; }
function getErosionColor(v: number) { return v < 20 ? "#10b981" : v < 40 ? "#f59e0b" : "#ef4444"; }

function MapPanel() {
  const [mode, setMode] = useState<"ndvi" | "erosion">("ndvi");

  return (
    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-bold text-sky-300">🗺️ نقشه مکانی زیرحوزه‌ها</h4>
        <div className="flex gap-2 bg-slate-700 p-1 rounded-lg">
          <button onClick={() => setMode("ndvi")} className={`px-3 py-1 text-xs rounded ${mode === "ndvi" ? "bg-sky-600 text-white" : "text-slate-300"}`}>NDVI</button>
          <button onClick={() => setMode("erosion")} className={`px-3 py-1 text-xs rounded ${mode === "erosion" ? "bg-orange-600 text-white" : "text-slate-300"}`}>فرسایش</button>
        </div>
      </div>

      <div className="h-[280px] rounded-lg overflow-hidden border border-slate-600">
        <MapContainer center={[35.5, 58.5]} zoom={7} scrollWheelZoom={false} className="h-full w-full">
          <TileLayer
            attribution='&copy; OpenStreetMap'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {SUBZONES.map(z => (
            <Circle
              key={z.id}
              center={[z.lat, z.lon]}
              pathOptions={{ color: mode === "ndvi" ? getNdviColor(z.ndvi) : getErosionColor(z.erosion), fillColor: mode === "ndvi" ? getNdviColor(z.ndvi) : getErosionColor(z.erosion), fillOpacity: 0.6 }}
              radius={15000}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={0.9} permanent>
                {z.name}
              </Tooltip>
              <Popup>
                <div className="text-slate-800 font-sans">
                  <strong className="text-lg">{z.name}</strong><br/>
                  NDVI: <span className="font-bold">{z.ndvi}</span><br/>
                  فرسایش: <span className="font-bold">{z.erosion} تن/هکتار</span>
                </div>
              </Popup>
            </Circle>
          ))}
        </MapContainer>
      </div>
      
      <div className="flex justify-center gap-4 mt-3 text-xs text-slate-400">
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-green-500"></div> عالی</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-yellow-500"></div> متوسط</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-red-500"></div> بحرانی</div>
      </div>
    </div>
  );
}

export default React.memo(MapPanel);
