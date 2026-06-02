"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, Polygon } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { gisService } from "@/lib/api";

const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

type LayerInfo = {
  base: { url: string; attribution: string; max_zoom: number };
  default_center: [number, number];
  default_zoom: number;
};

function ClickCapture({
  onPoint,
}: {
  onPoint: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      onPoint(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export function GisMap() {
  const [layers, setLayers] = useState<LayerInfo | null>(null);
  const [points, setPoints] = useState<[number, number][]>([]);
  const [area, setArea] = useState<number | null>(null);
  const [satellite, setSatellite] = useState(false);

  useEffect(() => {
    gisService.getLayers().then(setLayers).catch(() => {
      setLayers({
        base: {
          url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
          attribution: "OSM",
          max_zoom: 19,
        },
        default_center: [36.3, 59.6],
        default_zoom: 10,
      });
    });
  }, []);

  const addPoint = (lat: number, lng: number) => {
    setPoints((p) => [...p, [lat, lng]]);
  };

  const calcArea = async () => {
    if (points.length < 3) return;
    const coords = points.map(([lat, lng]) => [lng, lat] as [number, number]);
    const res = (await gisService.calculateArea(coords)) as { area_km2?: number };
    setArea(res.area_km2 ?? null);
  };

  if (!layers) {
    return <div className="h-[420px] rounded-2xl bg-slate-900 animate-pulse" />;
  }

  const center = layers.default_center;
  const tile = satellite
    ? {
        url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attribution: "Esri",
      }
    : layers.base;

  return (
    <div className="space-y-3">
      <div className="flex gap-2 flex-wrap">
        <button
          type="button"
          className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700"
          onClick={() => setSatellite(false)}
        >
          OSM
        </button>
        <button
          type="button"
          className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700"
          onClick={() => setSatellite(true)}
        >
          ماهواره
        </button>
        <button
          type="button"
          className="text-xs px-3 py-1.5 rounded-lg bg-violet-600"
          onClick={calcArea}
        >
          محاسبه مساحت ({points.length} نقطه)
        </button>
        {area != null && (
          <span className="text-xs text-emerald-400 self-center">
            {area.toFixed(3)} km²
          </span>
        )}
      </div>
      <div className="h-[420px] rounded-2xl overflow-hidden border border-slate-800 z-0">
        <MapContainer
          center={center}
          zoom={layers.default_zoom}
          className="h-full w-full"
          scrollWheelZoom
        >
          <TileLayer url={tile.url} attribution={tile.attribution} maxZoom={19} />
          <ClickCapture onPoint={addPoint} />
          {points.map((p, i) => (
            <Marker key={i} position={p} icon={icon}>
              <Popup>
                {p[0].toFixed(4)}, {p[1].toFixed(4)}
              </Popup>
            </Marker>
          ))}
          {points.length >= 3 && (
            <Polygon positions={points} pathOptions={{ color: "#8b5cf6" }} />
          )}
        </MapContainer>
      </div>
      <p className="text-xs text-slate-500">روی نقشه کلیک کنید تا رئوس polygon اضافه شود</p>
    </div>
  );
}
