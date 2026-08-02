import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    L?: typeof import("leaflet");
  }
}

function loadLeaflet(): Promise<NonNullable<Window["L"]>> {
  return new Promise((resolve, reject) => {
    if (window.L) {
      resolve(window.L);
      return;
    }
    if (!document.querySelector('link[data-leaflet]')) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      link.dataset.leaflet = "1";
      document.head.appendChild(link);
    }
    const existing = document.querySelector("script[data-leaflet]") as HTMLScriptElement | null;
    if (existing) {
      existing.addEventListener("load", () => resolve(window.L!));
      existing.addEventListener("error", () => reject(new Error("Leaflet load failed")));
      return;
    }
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.async = true;
    script.dataset.leaflet = "1";
    script.onload = () => resolve(window.L!);
    script.onerror = () => reject(new Error("Failed to load Leaflet"));
    document.body.appendChild(script);
  });
}

export type MapMarker = { lat: number; lng: number; label?: string };

export function LeafletPicker({
  lat,
  lng,
  onPick,
  height = 320,
  showSatellite = true,
  extraMarkers = [],
  enableGeolocate = true,
}: {
  lat: number | null;
  lng: number | null;
  onPick: (lat: number, lng: number) => void;
  height?: number;
  /** Esri World Imagery (free public tiles) for satellite view */
  showSatellite?: boolean;
  extraMarkers?: MapMarker[];
  enableGeolocate?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<{
    map: {
      setView: (c: [number, number], z: number) => void;
      remove: () => void;
      invalidateSize: () => void;
    };
    marker: { setLatLng: (c: [number, number]) => void } | null;
    L: NonNullable<Window["L"]>;
    layerGroup: { clearLayers: () => void; addLayer: (x: unknown) => void };
  } | null>(null);
  const [basemap, setBasemap] = useState<"osm" | "sat">("sat");
  const [geoError, setGeoError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const L = await loadLeaflet();
      if (cancelled || !containerRef.current) return;
      const center: [number, number] = [lat ?? 32.4279, lng ?? 53.688];
      const map = L.map(containerRef.current).setView(center, lat && lng ? 12 : 6);

      const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap",
        maxZoom: 19,
      });
      const sat = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        {
          attribution: "Tiles &copy; Esri",
          maxZoom: 19,
        },
      );
      (showSatellite ? sat : osm).addTo(map);

      const layerGroup = L.layerGroup().addTo(map);
      let marker: ReturnType<typeof L.marker> | null = null;
      if (lat != null && lng != null) {
        marker = L.marker([lat, lng]).addTo(map);
      }
      map.on("click", (e: { latlng: { lat: number; lng: number } }) => {
        const { lat: a, lng: b } = e.latlng;
        onPick(Number(a.toFixed(6)), Number(b.toFixed(6)));
        if (marker) marker.setLatLng([a, b]);
        else marker = L.marker([a, b]).addTo(map);
      });

      mapRef.current = {
        map: map as never,
        marker: marker as never,
        L,
        layerGroup: layerGroup as never,
      };
      // store tile refs on map for toggle
      (map as unknown as { _ecoOsm: unknown; _ecoSat: unknown })._ecoOsm = osm;
      (map as unknown as { _ecoOsm: unknown; _ecoSat: unknown })._ecoSat = sat;
      setReady(true);
      setTimeout(() => map.invalidateSize(), 100);
    })().catch((e) => console.error(e));
    return () => {
      cancelled = true;
      mapRef.current?.map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!mapRef.current || lat == null || lng == null) return;
    mapRef.current.map.setView([lat, lng], 13);
    if (mapRef.current.marker) mapRef.current.marker.setLatLng([lat, lng]);
  }, [lat, lng]);

  useEffect(() => {
    const ctx = mapRef.current;
    if (!ctx) return;
    ctx.layerGroup.clearLayers();
    for (const m of extraMarkers) {
      const mk = ctx.L.marker([m.lat, m.lng]);
      if (m.label) mk.bindPopup(m.label);
      ctx.layerGroup.addLayer(mk);
    }
  }, [extraMarkers, ready]);

  function toggleBasemap(mode: "osm" | "sat") {
    setBasemap(mode);
    const map = mapRef.current?.map as unknown as {
      removeLayer: (x: unknown) => void;
      addLayer: (x: unknown) => void;
      _ecoOsm: unknown;
      _ecoSat: unknown;
    };
    if (!map?._ecoOsm) return;
    if (mode === "sat") {
      map.removeLayer(map._ecoOsm);
      map.addLayer(map._ecoSat);
    } else {
      map.removeLayer(map._ecoSat);
      map.addLayer(map._ecoOsm);
    }
  }

  function geolocate() {
    setGeoError(null);
    if (!navigator.geolocation) {
      setGeoError("Geolocation not supported in this browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const a = Number(pos.coords.latitude.toFixed(6));
        const b = Number(pos.coords.longitude.toFixed(6));
        onPick(a, b);
        mapRef.current?.map.setView([a, b], 14);
      },
      (err) => setGeoError(err.message || "Location permission denied"),
      { enableHighAccuracy: true, timeout: 15000 },
    );
  }

  return (
    <div className="relative">
      <div className="absolute end-2 top-2 z-[500] flex flex-wrap gap-1">
        {showSatellite && (
          <>
            <button
              type="button"
              onClick={() => toggleBasemap("sat")}
              className={`rounded-lg px-2 py-1 text-[11px] font-bold shadow ${
                basemap === "sat" ? "bg-emerald-600 text-white" : "bg-white text-stone-700"
              }`}
            >
              Satellite
            </button>
            <button
              type="button"
              onClick={() => toggleBasemap("osm")}
              className={`rounded-lg px-2 py-1 text-[11px] font-bold shadow ${
                basemap === "osm" ? "bg-emerald-600 text-white" : "bg-white text-stone-700"
              }`}
            >
              Map
            </button>
          </>
        )}
        {enableGeolocate && (
          <button
            type="button"
            onClick={geolocate}
            className="rounded-lg bg-indigo-600 px-2 py-1 text-[11px] font-bold text-white shadow"
          >
            My location
          </button>
        )}
      </div>
      {geoError && (
        <p className="absolute bottom-2 start-2 z-[500] max-w-[90%] rounded bg-rose-600/90 px-2 py-1 text-[11px] text-white">
          {geoError}
        </p>
      )}
      <div
        ref={containerRef}
        className="z-0 w-full overflow-hidden rounded-2xl border border-emerald-200 shadow-inner"
        style={{ height }}
      />
    </div>
  );
}
