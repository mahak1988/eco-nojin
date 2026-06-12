// Sentinel-2 Simulator
export class SentinelSimulator {
  static async verify(latitude: number, longitude: number, date: Date, activityType?: string) {
    return {
      verified: true,
      confidence: 0.85,
      ndvi: 0.65,
      ndwi: -0.1,
      timestamp: new Date().toISOString(),
      activityType
    };
  }
}

export default new SentinelSimulator();