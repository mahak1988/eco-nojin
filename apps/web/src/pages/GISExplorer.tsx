import { useState, useCallback } from 'react'
import { MapContainer, TileLayer, Polygon, Polyline, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import {
  X, ZoomIn, ZoomOut, Locate, PenLine, BarChart2, Map
} from 'lucide-react'
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer,
  Tooltip, XAxis, YAxis
} from 'recharts'
import MapController from '../components/MapController'
import { useMapFix } from '../hooks/useMapFix'

/* ══════════════════════════════════════════════════════════════
   DATA
══════════════════════════════════════════════════════════════ */
type LL     = [number, number]
type Status = 'Growing' | 'Harvest Ready' | 'Planted' | 'Fallow'

const STATUS_COLOR: Record<Status, { fill: string; stroke: string }> = {
  'Growing':       { fill: '#4ade80', stroke: '#15803d' },
  'Harvest Ready': { fill: '#d4a017', stroke: '#92400e' },
  'Planted':       { fill: '#22c55e', stroke: '#166534' },
  'Fallow':        { fill: '#c4c9c6', stroke: '#6b7280' },
}

const B_LAT = -6.3100, B_LNG = 108.3050
const C_LAT = 0.0045,  C_LNG = 0.0055, GAP = 0.0003

function cell(row: number, col: number): LL[] {
  const lat0 = B_LAT - row * C_LAT, lng0 = B_LNG + col * C_LNG
  return [
    [lat0,               lng0 + GAP],
    [lat0,               lng0 + C_LNG - GAP],
    [lat0 - C_LAT + GAP, lng0 + C_LNG - GAP],
    [lat0 - C_LAT + GAP, lng0 + GAP],
  ]
}

type Field = {
  id: string; location: string; area: number; owner: string; operator: string
  crop: string; plantDate: string; harvestDate: string; irrigation: string
  village: string; status: Status; health: number; positions: LL[]
}

const RAW: { r:number; c:number; id:string; st:Status; owner:string; loc:string; village:string }[] = [
  {r:0,c:1,id:'F-2025-0012',st:'Growing',      owner:'Ahmad Hidayat',  loc:'Desa Karangampel', village:'Karangampel'},
  {r:0,c:2,id:'F-2025-0013',st:'Growing',      owner:'Sri Aminah',     loc:'Desa Tarangkerta', village:'Tarangkerta'},
  {r:0,c:3,id:'F-2025-0014',st:'Harvest Ready',owner:'Budi Santoso',   loc:'Desa Leles',       village:'Leles'},
  {r:0,c:4,id:'F-2025-0015',st:'Growing',      owner:'Dedi Kurniawan', loc:'Desa Patrol',      village:'Patrol'},
  {r:1,c:0,id:'F-2025-0016',st:'Planted',      owner:'Eni Nurhayati',  loc:'Desa Bonges',      village:'Bonges'},
  {r:1,c:1,id:'F-2025-0017',st:'Growing',      owner:'Rudi Hartono',   loc:'Desa Kandanghaur', village:'Kandanghaur'},
  {r:1,c:2,id:'F-2025-0018',st:'Harvest Ready',owner:'Siti Rahayu',    loc:'Desa Karangampel', village:'Karangampel'},
  {r:1,c:3,id:'F-2025-0019',st:'Growing',      owner:'Hendra Wijaya',  loc:'Desa Leles',       village:'Leles'},
  {r:1,c:4,id:'F-2025-0020',st:'Growing',      owner:'Agus Santoso',   loc:'Desa Patrol',      village:'Patrol'},
  {r:1,c:5,id:'F-2025-0021',st:'Fallow',       owner:'Dewi Lestari',   loc:'Desa Bonges',      village:'Bonges'},
  {r:2,c:0,id:'F-2025-0022',st:'Growing',      owner:'Joko Purnomo',   loc:'Desa Tarangkerta', village:'Tarangkerta'},
  {r:2,c:1,id:'F-2025-0023',st:'Harvest Ready',owner:'Rina Susanti',   loc:'Desa Karangampel', village:'Karangampel'},
  {r:2,c:2,id:'F-2025-0024',st:'Growing',      owner:'Bambang W',      loc:'Desa Leles',       village:'Leles'},
  {r:2,c:3,id:'F-2025-0025',st:'Harvest Ready',owner:'Wati Rahayu',    loc:'Desa Patrol',      village:'Patrol'},
  {r:2,c:4,id:'F-2025-0026',st:'Planted',      owner:'Surya Darma',    loc:'Desa Bonges',      village:'Bonges'},
  {r:2,c:5,id:'F-2025-0027',st:'Growing',      owner:'Fitri H',        loc:'Desa Kandanghaur', village:'Kandanghaur'},
  {r:3,c:0,id:'F-2025-0028',st:'Fallow',       owner:'Teguh Santoso',  loc:'Desa Karangampel', village:'Karangampel'},
  {r:3,c:1,id:'F-2025-0029',st:'Growing',      owner:'Linda Sari',     loc:'Desa Tarangkerta', village:'Tarangkerta'},
  {r:3,c:2,id:'F-2025-0030',st:'Growing',      owner:'Wahyu Prabowo',  loc:'Desa Leles',       village:'Leles'},
  {r:3,c:3,id:'F-2025-0031',st:'Growing',      owner:'Mulyadi',        loc:'Desa Patrol',      village:'Patrol'},
  {r:3,c:4,id:'F-2025-0032',st:'Harvest Ready',owner:'Endang S',       loc:'Desa Bonges',      village:'Bonges'},
  {r:3,c:5,id:'F-2025-0033',st:'Growing',      owner:'Sunarto',        loc:'Desa Kandanghaur', village:'Kandanghaur'},
  {r:4,c:1,id:'F-2025-0034',st:'Growing',      owner:'Triyono',        loc:'Desa Karangampel', village:'Karangampel'},
  {r:4,c:2,id:'F-2025-0035',st:'Harvest Ready',owner:'Sunarti',        loc:'Desa Leles',       village:'Leles'},
  {r:4,c:3,id:'F-2025-0036',st:'Growing',      owner:'Bintoro',        loc:'Desa Patrol',      village:'Patrol'},
  {r:4,c:4,id:'F-2025-0037',st:'Growing',      owner:'Kartini',        loc:'Desa Bonges',      village:'Bonges'},
  {r:5,c:1,id:'F-2025-0038',st:'Planted',      owner:'Sarwono',        loc:'Desa Karangampel', village:'Karangampel'},
  {r:5,c:2,id:'F-2025-0039',st:'Growing',      owner:'Marsudi',        loc:'Desa Tarangkerta', village:'Tarangkerta'},
  {r:5,c:3,id:'F-2025-0040',st:'Fallow',       owner:'Sutrisno',       loc:'Desa Leles',       village:'Leles'},
  {r:5,c:4,id:'F-2025-0041',st:'Growing',      owner:'Rahayu',         loc:'Desa Patrol',      village:'Patrol'},
]

const CROPS   = ['Rice', 'Corn', 'Soybean', 'Chili']
const IRRIG   = ['Irrigation Canal', 'Deep Well', 'Rain-fed', 'Pump Irrigation']
const FIELDS: Field[] = RAW.map((g, i) => ({
  id: g.id, location: g.loc, village: g.village, owner: g.owner,
  area: +(1.5 + (i % 5) * 0.35).toFixed(2),
  operator: 'Kelompok Tani Maju',
  crop: CROPS[i % 4], irrigation: IRRIG[i % 4],
  plantDate: '2025-03-12', harvestDate: '2025-07-20',
  status: g.st, health: 65 + (i * 7) % 30,
  positions: cell(g.r, g.c),
}))

const WATER_SRCS: LL[] = [
  [B_LAT - 0.5*C_LAT, B_LNG + 0.5*C_LNG],
  [B_LAT - 1.5*C_LAT, B_LNG + 3.5*C_LNG],
  [B_LAT - 3.0*C_LAT, B_LNG + 5.5*C_LNG],
  [B_LAT - 4.0*C_LAT, B_LNG + 2.5*C_LNG],
]
const CHANNELS: LL[][] = [
  [[B_LAT-2.5*C_LAT, B_LNG-0.2*C_LNG],[B_LAT-2.5*C_LAT, B_LNG+6.2*C_LNG]],
  [[B_LAT+0.2*C_LAT, B_LNG+2.5*C_LNG],[B_LAT-5.8*C_LAT, B_LNG+2.5*C_LNG]],
]

const waterIcon = L.divIcon({
  html: `<div style="width:18px;height:18px;background:#3b82f6;border-radius:50%;border:2.5px solid white;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>`,
  className: '', iconSize:[18,18], iconAnchor:[9,9],
})

/* Production history sparkline */
const PROD_HISTORY = [
  {m:'Jun',v:55},{m:'Jul',v:68},{m:'Aug',v:72},{m:'Sep',v:65},{m:'Oct',v:70},
  {m:'Nov',v:62},{m:'Dec',v:58},
]

const STATUS_BADGE: Record<string, string> = {
  'Growing':      'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  'Harvest Ready':'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  'Planted':      'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  'Fallow':       'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
}
const STATUS_DOT: Record<string, string> = {
  'Growing':'bg-green-500','Harvest Ready':'bg-yellow-500','Planted':'bg-blue-500','Fallow':'bg-gray-400',
}

const CENTER: LL = [B_LAT - 2.5*C_LAT, B_LNG + 2.75*C_LNG]

/* ══════════════════════════════════════════════════════════════
   COMPONENT
══════════════════════════════════════════════════════════════ */
export default function GISExplorer() {
  const [layers, setLayers] = useState({
    fields: true, irrigation: true, water: true, boundaries: true,
    grid: true, heatmap: false,
  })
  const [baseMap,     setBaseMap]     = useState<'Satellite'|'Vector'|'Terrain'>('Satellite')
  const [colorBy,     setColorBy]     = useState<'Status'|'Crop'>('Status')
  const [selected,    setSelected]    = useState<Field | null>(null)
  const { setContainerRef, onMapReady, invalidate } = useMapFix()

  const toggleLayer = useCallback((k: keyof typeof layers) => {
    setLayers(s => ({ ...s, [k]: !s[k] }))
    setTimeout(invalidate, 50); setTimeout(invalidate, 200)
  }, [invalidate])

  const selectField = useCallback((f: Field | null) => {
    setSelected(f)
    setTimeout(invalidate, 50); setTimeout(invalidate, 200)
  }, [invalidate])

  const totalArea   = FIELDS.reduce((a, f) => a + f.area, 0).toFixed(0)
  const avgHealth   = Math.round(FIELDS.reduce((a, f) => a + f.health, 0) / FIELDS.length)

  return (
    <div className="flex h-full overflow-hidden bg-gray-50 dark:bg-gray-900">

      {/* ── LEFT SIDEBAR ─────────────────────────────────────── */}
      <aside className="w-60 shrink-0 flex flex-col bg-white dark:bg-gray-950 border-r border-gray-100 dark:border-gray-800 overflow-y-auto">

        {/* Title */}
        <div className="px-5 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800">
          <div className="flex items-center gap-2 mb-1">
            <Map className="w-4 h-4 text-green-600" />
            <span className="text-sm font-bold text-gray-900 dark:text-white">GIS Explorer</span>
          </div>
          <p className="text-[11px] text-gray-400">Digital twin &middot; {FIELDS.length} fields mapped</p>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">

          {/* BASE MAP */}
          <div>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Base Map</p>
            <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
              {(['Vector','Satellite','Terrain'] as const).map(m => (
                <button key={m} onClick={() => setBaseMap(m)}
                  className={`flex-1 py-1.5 rounded-lg text-[11px] font-semibold transition-colors ${baseMap===m ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-400 dark:text-gray-500 hover:text-gray-600'}`}>
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* COLOR FIELDS BY */}
          <div>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Color Fields By</p>
            <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
              {(['Status','Crop'] as const).map(c => (
                <button key={c} onClick={() => setColorBy(c)}
                  className={`flex-1 py-1.5 rounded-lg text-[11px] font-semibold transition-colors ${colorBy===c ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-400 dark:text-gray-500 hover:text-gray-600'}`}>
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* LAYERS */}
          <div>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Layers</p>
            <div className="space-y-1">
              {[
                { k:'fields'     as const, label:'Agricultural Fields',  icon:'🌾' },
                { k:'irrigation' as const, label:'Irrigation Channels',  icon:'💧' },
                { k:'water'      as const, label:'Water Sources',        icon:'💧' },
                { k:'boundaries' as const, label:'Admin Boundaries',     icon:'📍' },
                { k:'grid'       as const, label:'Coordinate Grid',      icon:'⊞' },
              ].map(({ k, label, icon }) => (
                <div key={k} className="flex items-center justify-between py-2 px-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm leading-none">{icon}</span>
                    <span className="text-xs text-gray-700 dark:text-gray-300 font-medium">{label}</span>
                  </div>
                  <button onClick={() => toggleLayer(k)}
                    className={`relative w-9 h-5 rounded-full transition-colors duration-200 shrink-0 ${layers[k] ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'}`}>
                    <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-200 ${layers[k] ? 'left-[18px]' : 'left-0.5'}`} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* ANALYSIS */}
          <div>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Analysis</p>
            <div className="flex items-center justify-between py-2 px-1 bg-gray-50 dark:bg-gray-800/60 rounded-xl px-3">
              <div className="flex items-center gap-2.5">
                <BarChart2 className="w-4 h-4 text-gray-400" />
                <span className="text-xs text-gray-700 dark:text-gray-300 font-medium">Productivity Heatmap</span>
              </div>
              <button onClick={() => toggleLayer('heatmap')}
                className={`relative w-9 h-5 rounded-full transition-colors duration-200 shrink-0 ${layers.heatmap ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'}`}>
                <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-200 ${layers.heatmap ? 'left-[18px]' : 'left-0.5'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Draw button */}
        <div className="px-4 py-4 border-t border-gray-100 dark:border-gray-800 shrink-0">
          <button className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            <PenLine className="w-3.5 h-3.5" /> Draw / Edit Polygon
          </button>
        </div>
      </aside>

      {/* ── MAP + RIGHT PANEL ────────────────────────────────── */}
      <div className="flex-1 flex min-w-0 overflow-hidden">

        {/* MAP */}
        <div className="flex-1 relative min-w-0 min-h-0">

          {/* Stats bar — floats at top of map */}
          <div className="absolute top-3 left-3 z-[1000] flex items-center gap-px">
            {[
              { label: 'MAPPED FIELDS', value: String(FIELDS.length) },
              { label: 'TOTAL AREA',    value: `${totalArea} ha` },
              { label: 'AVG HEALTH',    value: String(avgHealth) },
            ].map(({ label, value }, i) => (
              <div key={label}
                className={`bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm px-4 py-2 border border-gray-200 dark:border-gray-700 ${i===0?'rounded-l-xl':''}${i===2?'rounded-r-xl':''}`}>
                <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest">{label}</p>
                <p className="text-base font-bold text-gray-900 dark:text-white leading-tight">{value}</p>
              </div>
            ))}
          </div>

          {/* Zoom controls — top right */}
          <div className="absolute top-3 right-3 z-[1000] flex flex-col gap-1.5">
            <button className="w-9 h-9 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 shadow-card flex items-center justify-center hover:bg-white transition-colors">
              <ZoomIn className="w-4 h-4 text-gray-600" />
            </button>
            <button className="w-9 h-9 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 shadow-card flex items-center justify-center hover:bg-white transition-colors">
              <ZoomOut className="w-4 h-4 text-gray-600" />
            </button>
            <button className="w-9 h-9 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 shadow-card flex items-center justify-center hover:bg-white transition-colors">
              <Locate className="w-4 h-4 text-gray-600" />
            </button>
          </div>

          {/* Map canvas — absolute inset for correct Leaflet sizing */}
          <div ref={setContainerRef} style={{ position:'absolute', inset:0 }}>
            <MapContainer
              center={CENTER} zoom={13}
              scrollWheelZoom zoomControl={false} attributionControl={false}
              style={{ width:'100%', height:'100%' }}
            >
              <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                maxZoom={19} maxNativeZoom={19}
              />

              {layers.fields && FIELDS.map(f => {
                const c = STATUS_COLOR[f.status]
                return (
                  <Polygon key={f.id} positions={f.positions}
                    pathOptions={{ color:c.stroke, fillColor:c.fill, fillOpacity:0.52, weight:1.5 }}
                    eventHandlers={{ click: () => selectField(f) }}>
                    <Popup>
                      <strong>{f.id}</strong><br/>
                      <span style={{ color:c.stroke, fontWeight:600 }}>{f.status}</span>
                    </Popup>
                  </Polygon>
                )
              })}

              {layers.irrigation && CHANNELS.map((ch,i) => (
                <Polyline key={i} positions={ch}
                  pathOptions={{ color:'#60a5fa', weight:2.5, opacity:0.85, dashArray:'6 3' }}/>
              ))}

              {layers.water && WATER_SRCS.map((pos,i) => (
                <Marker key={i} position={pos} icon={waterIcon}>
                  <Popup>Water Source {i+1}</Popup>
                </Marker>
              ))}

              <MapController onReady={onMapReady} />
            </MapContainer>
          </div>
        </div>

        {/* ── RIGHT PANEL: Field Details ─────────────────────── */}
        {selected ? (
          <div className="w-72 shrink-0 flex flex-col bg-white dark:bg-gray-950 border-l border-gray-100 dark:border-gray-800 overflow-hidden">

            {/* Header */}
            <div className="px-5 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800 shrink-0">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-lg font-bold text-gray-900 dark:text-white leading-tight">{selected.id}</p>
                  <p className="text-sm text-gray-400 mt-0.5">{selected.crop}</p>
                </div>
                <button onClick={() => selectField(null)}
                  className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors mt-0.5">
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
              <div className="flex items-center gap-2 mt-3">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${STATUS_BADGE[selected.status]}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT[selected.status]}`}/>
                  {selected.status}
                </span>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                  Health {selected.health}
                </span>
              </div>
            </div>

            {/* Field details */}
            <div className="flex-1 overflow-y-auto">
              <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Field Details</p>
                <div className="space-y-0">
                  {[
                    ['Area',       `${selected.area} ha`],
                    ['Owner',      selected.owner],
                    ['Operator',   selected.operator],
                    ['Crop',       selected.crop],
                    ['Planted',    selected.plantDate],
                    ['Harvest',    selected.harvestDate],
                    ['Irrigation', selected.irrigation],
                    ['Village',    selected.village],
                  ].map(([label, value]) => (
                    <div key={label} className="flex items-center justify-between py-2.5 border-b border-gray-50 dark:border-gray-800/50 last:border-0">
                      <span className="text-xs text-gray-400 dark:text-gray-500">{label}</span>
                      <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 text-right max-w-[150px] truncate">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Production history chart */}
              <div className="px-5 py-4">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Production History</p>
                <ResponsiveContainer width="100%" height={120}>
                  <AreaChart data={PROD_HISTORY} margin={{ top:4, right:4, left:-24, bottom:0 }}>
                    <defs>
                      <linearGradient id="gph" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#16a34a" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false}/>
                    <XAxis dataKey="m" tick={{ fontSize:10, fill:'#9ca3af' }} axisLine={false} tickLine={false}/>
                    <YAxis domain={[0,100]} tick={{ fontSize:10, fill:'#9ca3af' }} axisLine={false} tickLine={false}
                      ticks={[0,25,50,75,100]}/>
                    <Tooltip contentStyle={{ borderRadius:10, border:'none', fontSize:11, boxShadow:'0 4px 12px rgba(0,0,0,0.08)' }}/>
                    <Area type="monotone" dataKey="v" stroke="#16a34a" strokeWidth={2}
                      fill="url(#gph)" dot={false}/>
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* CTA */}
            <div className="px-5 py-4 border-t border-gray-100 dark:border-gray-800 shrink-0">
              <button className="w-full py-2.5 bg-green-700 hover:bg-green-800 text-white text-sm font-semibold rounded-xl transition-colors">
                Open Full Profile
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
