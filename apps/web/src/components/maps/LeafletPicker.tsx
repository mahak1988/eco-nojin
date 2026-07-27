import { useEffect, useRef } from "react";

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

export function LeafletPicker({
  lat,
  lng,
  onPick,
  height = 320,
}: {
  lat: number | null;
  lng: number | null;
  onPick: (lat: number, lng: number) => void;
  height?: number;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<{
    map: { setView: (c: [number, number], z: number) => void; remove: () => void };
    marker: { setLatLng: (c: [number, number]) => void } | null;
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const L = await loadLeaflet();
      if (cancelled || !containerRef.current) return;
      const center: [number, number] = [lat ?? 32.4279, lng ?? 53.688];
      const map = L.map(containerRef.current).setView(center, lat && lng ? 12 : 6);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap",
        maxZoom: 19,
      }).addTo(map);
      let marker: ReturnType<typeof L.marker> | null = null;
      if (lat != null && lng != null) {
        marker = L.marker([lat, lng]).addTo(map);
      }
      map.on("click", (e: { latlng: { lat: number; lng: number } }) => {
        const { lat: a, lng: b } = e.latlng;
        onPick(Number(a.toFixed(5)), Number(b.toFixed(5)));
        if (marker) marker.setLatLng([a, b]);
        else marker = L.marker([a, b]).addTo(map);
      });
      mapRef.current = { map: map as never, marker: marker as never };
    })().catch(console.error);
    return () => {
      cancelled = true;
      mapRef.current?.map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!mapRef.current || lat == null || lng == null) return;
    mapRef.current.map.setView([lat, lng], 12);
    if (mapRef.current.marker) mapRef.current.marker.setLatLng([lat, lng]);
  }, [lat, lng]);

  return (
    <div
      ref={containerRef}
      className="z-0 w-full overflow-hidden rounded-2xl border border-emerald-200 shadow-inner"
      style={{ height }}
    />
  );
}
