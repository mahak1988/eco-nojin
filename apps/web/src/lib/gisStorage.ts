// lib/gisStorage.ts - مدیریت ذخیره‌سازی داده‌های GIS
export interface SavedLocation {
  id: string;
  name: string;
  description?: string;
  category: "field" | "structure" | "sample" | "observation" | "custom";
  coordinates: [number, number]; // [lat, lng]
  zoom?: number;
  notes?: string;
  tags?: string[];
  createdAt: string;
  updatedAt: string;
  userId?: string;
  shared?: boolean;
}

export interface Measurement {
  id: string;
  type: "distance" | "area" | "radius";
  points: [number, number][];
  result: number;
  unit: string;
  formattedResult: string;
  createdAt: string;
}

const STORAGE_KEYS = {
  LOCATIONS: "econojin_gis_locations",
  MEASUREMENTS: "econojin_gis_measurements",
  PREFERENCES: "econojin_gis_preferences",
  HISTORY: "econojin_gis_history",
};

export const gisStorage = {
  // ============ Locations ============
  getLocations(): SavedLocation[] {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem(STORAGE_KEYS.LOCATIONS);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  },

  saveLocation(location: Omit<SavedLocation, "id" | "createdAt" | "updatedAt">): SavedLocation {
    const locations = this.getLocations();
    const newLocation: SavedLocation = {
      ...location,
      id: `loc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    locations.push(newLocation);
    localStorage.setItem(STORAGE_KEYS.LOCATIONS, JSON.stringify(locations));
    this.addToHistory(`Saved location: ${newLocation.name}`);
    return newLocation;
  },

  updateLocation(id: string, updates: Partial<SavedLocation>): SavedLocation | null {
    const locations = this.getLocations();
    const index = locations.findIndex(l => l.id === id);
    if (index === -1) return null;
    
    locations[index] = {
      ...locations[index],
      ...updates,
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEYS.LOCATIONS, JSON.stringify(locations));
    return locations[index];
  },

  deleteLocation(id: string): boolean {
    const locations = this.getLocations();
    const filtered = locations.filter((l: any) => l.id !== id);
    if (filtered.length === locations.length) return false;
    localStorage.setItem(STORAGE_KEYS.LOCATIONS, JSON.stringify(filtered));
    return true;
  },

  // ============ Measurements ============
  getMeasurements(): Measurement[] {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem(STORAGE_KEYS.MEASUREMENTS);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  },

  saveMeasurement(measurement: Omit<Measurement, "id" | "createdAt">): Measurement {
    const measurements = this.getMeasurements();
    const newMeasurement: Measurement = {
      ...measurement,
      id: `meas_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString(),
    };
    measurements.push(newMeasurement);
    localStorage.setItem(STORAGE_KEYS.MEASUREMENTS, JSON.stringify(measurements.slice(-50))); // Keep last 50
    return newMeasurement;
  },

  clearMeasurements(): void {
    localStorage.removeItem(STORAGE_KEYS.MEASUREMENTS);
  },

  // ============ History ============
  getHistory(): string[] {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem(STORAGE_KEYS.HISTORY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  },

  addToHistory(action: string): void {
    const history = this.getHistory();
    history.unshift(`[${new Date().toLocaleTimeString("fa-IR")}] ${action}`);
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history.slice(0, 100)));
  },

  // ============ Export/Import ============
  exportAll(): string {
    return JSON.stringify({
      locations: this.getLocations(),
      measurements: this.getMeasurements(),
      exportedAt: new Date().toISOString(),
      version: "1.0",
    }, null, 2);
  },

  exportAsGeoJSON(): string {
    const locations = this.getLocations();
    const geojson = {
      type: "FeatureCollection",
      features: locations.map((loc: any) => ({
        type: "Feature",
        properties: {
          name: loc.name,
          description: loc.description,
          category: loc.category,
          notes: loc.notes,
          tags: loc.tags,
          createdAt: loc.createdAt,
        },
        geometry: {
          type: "Point",
          coordinates: [loc.coordinates[1], loc.coordinates[0]],
        },
      })),
    };
    return JSON.stringify(geojson, null, 2);
  },

  exportAsKML(): string {
    const locations = this.getLocations();
    const placemarks = locations.map((loc: any) => `
    <Placemark>
      <name>${this.escapeXml(loc.name)}</name>
      <description>${this.escapeXml(loc.description || "")}</description>
      <Point>
        <coordinates>${loc.coordinates[1]},${loc.coordinates[0]},0</coordinates>
      </Point>
    </Placemark>`).join("");
    
    return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Econojin GIS Export</name>${placemarks}
  </Document>
</kml>`;
  },

  escapeXml(str: string): string {
    return str.replace(/[<>&'"]/g, c => ({
      "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;"
    }[c] || c));
  },

  downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};
