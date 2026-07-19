import { MapContainer, TileLayer, Polygon, Polyline, Marker, Popup } from "react-leaflet"
import L from "leaflet"
import { useMapFix } from "@/hooks/useMapFix"

// Status types for agricultural land
type LandStatus = "کاشت" | "آماده برداشت" | "رشد" | "بدون فعالیت"

// Status colors - زیبا و رنگارنگ برای نقشه
const STATUS_COLOR: Record<LandStatus, { fill: string; stroke: string }> = {
  "کاشت": { fill: "#4ade80", stroke: "#15803d" },
  "آمادت برداشت": { fill: "#f59e0b", stroke: "#92400e" },
  "رشد": { fill: "#22c55e", stroke: "#166534" },
  "بدون فعالیت": { fill: "#c4c9c6", stroke: "#6b7280" },
}

// مختصات شمالی و شرقی ایران (تقریباً)
const BASE_LAT = 35.7, BASE_LNG = 51.4
const DELTA_LAT = 0.01, DELTA_LNG = 0.01, GAP = 0.0003

// ساختن خانه‌های نقشه
function cell(row: number, col: number): [number, number][] {
  const lat0 = BASE_LAT - row * DELTA_LAT, lng0 = BASE_LNG + col * DELTA_LNG
  return [
    [lat0, lng0 + GAP],
    [lat0, lng0 + DELTA_LNG - GAP],
    [lat0 - DELTA_LAT + GAP, lng0 + DELTA_LNG - GAP],
    [lat0 - DELTA_LAT + GAP, lng0 + GAP],
  ]
}

// داده‌های نمونه - می‌توانید از API بارگیری کنید
const GRID: { r: number; c: number; st: LandStatus }[] = [
  { r: 0, c: 1, st: "کاشت" },
  { r: 0, c: 2, st: "کاشت" },
  { r: 0, c: 3, st: "آماده برداشت" },
  { r: 0, c: 4, st: "رشد" },
  { r: 1, c: 0, st: "کاشت" },
  { r: 1, c: 1, st: "رشد" },
  { r: 1, c: 2, st: "آماده برداشت" },
  { r: 1, c: 3, st: "کاشت" },
  { r: 2, c: 0, st: "بدون فعالیت" },
  { r: 2, c: 1, st: "کاشت" },
  { r: 2, c: 2, st: "آماده برداشت" },
]

// منابع آب
const WATER_SOURCES: [number, number][] = [
  [BASE_LAT - 1.0, BASE_LNG + 1.5],
  [BASE_LAT - 2.5, BASE_LNG + 3.5],
]

// کانال‌های آبیاری
const CHANNELS: [number, number][][] = [
  [[BASE_LAT - 2.0, BASE_LNG - 0.5], [BASE_LAT - 2.0, BASE_LNG + 4.0]],
]

// اقلام راهنما
const LEGEND = [
  { label: "کاشت", color: "#4ade80", type: "rect" },
  { label: "آماده برداشت", color: "#f59e0b", type: "rect" },
  { label: "رشد", color: "#22c55e", type: "rect" },
  { label: "بدون فعالیت", color: "#c4c9c6", type: "rect" },
  { label: "منبع آب", color: "#3b82f6", type: "drop" },
  { label: "کانال آبیاری", color: "#60a5fa", type: "line" },
]

const waterIcon = L.divIcon({
  html: `<div style="width:20px;height:20px;background:white;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;">
    <svg width="11" height="11" viewBox="0 0 24 24" fill="#3b82f6">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15v-4H7l5-8v4h4l-5 8z"/>
    </svg></div>`,
  className: "",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
})

const CENTER: [number, number] = [BASE_LAT - 2.5 * DELTA_LAT, BASE_LNG + 2.0]

interface EcoDashboardMapProps {
  height?: string
}

export default function EcoDashboardMap({ height = "400px" }: EcoDashboardMapProps) {
  const { setContainerRef } = useMapFix()

  return (
    <div style={{ position: "relative", width: "100%", height }} className="rounded-xl overflow-hidden border">
      <div ref={setContainerRef} style={{ position: "absolute", inset: 0 }}>
        <MapContainer
          center={CENTER}
          zoom={13}
          scrollWheelZoom={false}
          zoomControl={false}
          attributionControl={false}
          style={{ width: "100%", height: "100%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />

          {GRID.map((g, i) => {
            const c = STATUS_COLOR[g.st]
            return (
              <Polygon key={i} positions={cell(g.r, g.c)} pathOptions={{ color: c.stroke, fillColor: c.fill, fillOpacity: 0.5, weight: 1.5 }}>
                <Popup><span className="text-xs font-semibold">{g.st}</span></Popup>
              </Polygon>
            )
          })}

          {CHANNELS.map((ch, i) => (
            <Polyline key={i} positions={ch} pathOptions={{ color: "#60a5fa", weight: 2, opacity: 0.8, dashArray: "5 3" }} />
          ))}

          {WATER_SOURCES.map((pos, i) => (
            <Marker key={i} position={pos} icon={waterIcon}>
              <Popup>منبع آب {i + 1}</Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Legend */}
        <div style={{ position: "absolute", bottom: 10, right: 10, zIndex: 1000 }} className="bg-white/95 backdrop-blur-sm rounded-xl shadow border p-3">
          <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-2">راهنما</p>
          {LEGEND.map(({ label, color, type }) => (
            <div key={label} className="flex items-center gap-2 mb-1.5 last:mb-0">
              {type === "rect" && <span className="w-3 h-3 rounded-sm shrink-0" style={{ background: color, opacity: 0.85 }} />}
              {type === "drop" && (
                <span className="w-3 flex justify-center shrink-0">
                  <svg width="8" height="11" viewBox="0 0 9 12" fill={color}>
                    <path d="M4.5 0C4.5 0 0 5.5 0 8a4.5 4.5 0 009 0C9 5.5 4.5 0 4.5 0z" />
                  </svg>
                </span>
              )}
              {type === "line" && <span className="w-3 block shrink-0" style={{ borderTop: `2px dashed ${color}` }} />}
              <span className="text-[10px] text-gray-600 whitespace-nowrap">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}