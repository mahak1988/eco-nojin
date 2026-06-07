// lib/spectralCalculations.ts
// محاسبات شاخص‌های طیفی برای تحلیل پوشش گیاهی و محیط زیست

export interface SpectralBands {
  blue?: number;
  green?: number;
  red?: number;
  nir?: number;
  swir1?: number;
  swir2?: number;
}

export interface SpectralIndex {
  name: string;
  fullName: string;
  formula: string;
  value: number;
  interpretation: string;
  color: string;
  category: "vegetation" | "water" | "soil" | "fire" | "temperature";
}

// ============ شاخص‌های پوشش گیاهی ============

export function calculateNDVI(bands: SpectralBands): number {
  // Normalized Difference Vegetation Index
  // NDVI = (NIR - Red) / (NIR + Red)
  if (!bands.nir || !bands.red) return 0;
  const numerator = bands.nir - bands.red;
  const denominator = bands.nir + bands.red;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateEVI(bands: SpectralBands): number {
  // Enhanced Vegetation Index
  // EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
  if (!bands.nir || !bands.red || !bands.blue) return 0;
  const numerator = 2.5 * (bands.nir - bands.red);
  const denominator = bands.nir + 6 * bands.red - 7.5 * bands.blue + 1;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateSAVI(bands: SpectralBands, L: number = 0.5): number {
  // Soil Adjusted Vegetation Index
  // SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)
  if (!bands.nir || !bands.red) return 0;
  const numerator = bands.nir - bands.red;
  const denominator = bands.nir + bands.red + L;
  if (denominator === 0) return 0;
  return (numerator / denominator) * (1 + L);
}

export function calculateMSAVI2(bands: SpectralBands): number {
  // Modified Soil Adjusted Vegetation Index 2
  // MSAVI2 = (2*NIR + 1 - sqrt((2*NIR + 1)^2 - 8*(NIR - Red))) / 2
  if (!bands.nir || !bands.red) return 0;
  const term1 = 2 * bands.nir + 1;
  const term2 = Math.sqrt(term1 * term1 - 8 * (bands.nir - bands.red));
  return (term1 - term2) / 2;
}

// ============ شاخص‌های آب ============

export function calculateNDWI(bands: SpectralBands): number {
  // Normalized Difference Water Index
  // NDWI = (Green - NIR) / (Green + NIR)
  if (!bands.green || !bands.nir) return 0;
  const numerator = bands.green - bands.nir;
  const denominator = bands.green + bands.nir;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateMNDWI(bands: SpectralBands): number {
  // Modified Normalized Difference Water Index
  // MNDWI = (Green - SWIR1) / (Green + SWIR1)
  if (!bands.green || !bands.swir1) return 0;
  const numerator = bands.green - bands.swir1;
  const denominator = bands.green + bands.swir1;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

// ============ شاخص‌های خاک ============

export function calculateNDSI(bands: SpectralBands): number {
  // Normalized Difference Soil Index
  // NDSI = (SWIR1 - NIR) / (SWIR1 + NIR)
  if (!bands.swir1 || !bands.nir) return 0;
  const numerator = bands.swir1 - bands.nir;
  const denominator = bands.swir1 + bands.nir;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateBI(bands: SpectralBands): number {
  // Brightness Index
  // BI = sqrt((Red^2 + Green^2 + NIR^2) / 3)
  if (!bands.red || !bands.green || !bands.nir) return 0;
  return Math.sqrt((bands.red * bands.red + bands.green * bands.green + bands.nir * bands.nir) / 3);
}

// ============ شاخص‌های آتش‌سوزی ============

export function calculateNBR(bands: SpectralBands): number {
  // Normalized Burn Ratio
  // NBR = (NIR - SWIR2) / (NIR + SWIR2)
  if (!bands.nir || !bands.swir2) return 0;
  const numerator = bands.nir - bands.swir2;
  const denominator = bands.nir + bands.swir2;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateBAI(bands: SpectralBands): number {
  // Burned Area Index
  // BAI = 1 / ((0.1 - Red)^2 + (0.06 - NIR)^2)
  if (!bands.red || !bands.nir) return 0;
  const term1 = Math.pow(0.1 - bands.red, 2);
  const term2 = Math.pow(0.06 - bands.nir, 2);
  if (term1 + term2 === 0) return 0;
  return 1 / (term1 + term2);
}

// ============ توابع کمکی ============

export function interpretNDVI(value: number): { text: string; color: string } {
  if (value < -0.1) return { text: "آب، برف، یا ابر", color: "#1e40af" };
  if (value < 0.1) return { text: "خاک برهنه یا منطقه شهری", color: "#92400e" };
  if (value < 0.2) return { text: "پوشش گیاهی بسیار کم", color: "#fbbf24" };
  if (value < 0.4) return { text: "پوشش گیاهی کم", color: "#f59e0b" };
  if (value < 0.6) return { text: "پوشش گیاهی متوسط", color: "#84cc16" };
  if (value < 0.8) return { text: "پوشش گیاهی متراکم", color: "#22c55e" };
  return { text: "جنگل متراکم", color: "#15803d" };
}

export function interpretNDWI(value: number): { text: string; color: string } {
  if (value < -0.3) return { text: "خاک خشک", color: "#92400e" };
  if (value < 0) return { text: "پوشش گیاهی یا خاک مرطوب", color: "#ca8a04" };
  if (value < 0.3) return { text: "رطوبت سطحی", color: "#0ea5e9" };
  if (value < 0.6) return { text: "آب کم‌عمق", color: "#0284c7" };
  return { text: "آب عمیق", color: "#1e40af" };
}

export function interpretNBR(value: number): { text: string; color: string } {
  if (value < -0.25) return { text: "سوختگی شدید", color: "#7f1d1d" };
  if (value < -0.1) return { text: "سوختگی متوسط-شدید", color: "#dc2626" };
  if (value < 0.1) return { text: "سوختگی کم-متوسط", color: "#f59e0b" };
  if (value < 0.27) return { text: "منطقه نسوخته", color: "#84cc16" };
  if (value < 0.44) return { text: "پوشش گیاهی متراکم", color: "#22c55e" };
  return { text: "جنگل متراکم", color: "#15803d" };
}

export function calculateAllIndices(bands: SpectralBands): SpectralIndex[] {
  return [
    {
      name: "NDVI",
      fullName: "Normalized Difference Vegetation Index",
      formula: "(NIR - Red) / (NIR + Red)",
      value: calculateNDVI(bands),
      interpretation: interpretNDVI(calculateNDVI(bands)).text,
      color: interpretNDVI(calculateNDVI(bands)).color,
      category: "vegetation"
    },
    {
      name: "EVI",
      fullName: "Enhanced Vegetation Index",
      formula: "2.5×(NIR-Red)/(NIR+6Red-7.5Blue+1)",
      value: calculateEVI(bands),
      interpretation: "حساس‌تر در مناطق با پوشش متراکم",
      color: "#10b981",
      category: "vegetation"
    },
    {
      name: "SAVI",
      fullName: "Soil Adjusted Vegetation Index",
      formula: "((NIR-Red)/(NIR+Red+0.5))×1.5",
      value: calculateSAVI(bands),
      interpretation: "مناسب برای مناطق با خاک نمایان",
      color: "#84cc16",
      category: "vegetation"
    },
    {
      name: "NDWI",
      fullName: "Normalized Difference Water Index",
      formula: "(Green - NIR) / (Green + NIR)",
      value: calculateNDWI(bands),
      interpretation: interpretNDWI(calculateNDWI(bands)).text,
      color: interpretNDWI(calculateNDWI(bands)).color,
      category: "water"
    },
    {
      name: "NBR",
      fullName: "Normalized Burn Ratio",
      formula: "(NIR - SWIR2) / (NIR + SWIR2)",
      value: calculateNBR(bands),
      interpretation: interpretNBR(calculateNBR(bands)).text,
      color: interpretNBR(calculateNBR(bands)).color,
      category: "fire"
    }
  ];
}

// ============ تولید داده‌های نمونه برای نقشه حرارتی ============

export function generateHeatmapData(
  center: [number, number],
  radius: number,
  indexType: "NDVI" | "EVI" | "SAVI" | "NDWI" | "NBR",
  resolution: number = 20
): Array<{ lat: number; lng: number; value: number }> {
  const data: Array<{ lat: number; lng: number; value: number }> = [];
  
  for (let i = 0; i < resolution; i++) {
    for (let j = 0; j < resolution; j++) {
      const lat = center[0] + (i - resolution/2) * (radius / resolution) / 111000;
      const lng = center[1] + (j - resolution/2) * (radius / resolution) / (111000 * Math.cos(center[0] * Math.PI / 180));
      
      // تولید مقدار بر اساس نوع شاخص
      let value: number;
      const distance = Math.sqrt(Math.pow(i - resolution/2, 2) + Math.pow(j - resolution/2, 2)) / (resolution/2);
      const noise = (Math.random() - 0.5) * 0.2;
      
      switch (indexType) {
        case "NDVI":
          value = 0.8 - distance * 0.6 + noise;
          break;
        case "EVI":
          value = 0.6 - distance * 0.5 + noise;
          break;
        case "SAVI":
          value = 0.7 - distance * 0.55 + noise;
          break;
        case "NDWI":
          value = -0.3 + distance * 0.8 + noise;
          break;
        case "NBR":
          value = 0.5 - distance * 0.7 + noise;
          break;
        default:
          value = 0.5 + noise;
      }
      
      // محدود کردن مقدار
      value = Math.max(-1, Math.min(1, value));
      
      data.push({ lat, lng, value });
    }
  }
  
  return data;
}

// ============ رنگ‌بندی نقشه حرارتی ============

export function getHeatmapColor(value: number, indexType: string): string {
  // نرمال‌سازی مقدار به بازه 0-1
  const normalized = (value + 1) / 2;
  
  switch (indexType) {
    case "NDVI":
    case "EVI":
    case "SAVI":
      // قرمز (کم) → زرد → سبز (زیاد)
      if (normalized < 0.3) return `rgba(220, 38, 38, ${0.3 + normalized})`;
      if (normalized < 0.5) return `rgba(251, 191, 36, ${0.4 + normalized * 0.5})`;
      if (normalized < 0.7) return `rgba(132, 204, 22, ${0.5 + normalized * 0.4})`;
      return `rgba(34, 197, 94, ${0.6 + normalized * 0.3})`;
    
    case "NDWI":
      // قهوه‌ای (خشک) → آبی (تر)
      if (normalized < 0.3) return `rgba(146, 64, 14, ${0.3 + normalized})`;
      if (normalized < 0.5) return `rgba(202, 138, 4, ${0.4 + normalized * 0.5})`;
      if (normalized < 0.7) return `rgba(14, 165, 233, ${0.5 + normalized * 0.4})`;
      return `rgba(30, 64, 175, ${0.6 + normalized * 0.3})`;
    
    case "NBR":
      // قرمز (سوخته) → سبز (سالم)
      if (normalized < 0.3) return `rgba(127, 29, 29, ${0.3 + normalized})`;
      if (normalized < 0.5) return `rgba(220, 38, 38, ${0.4 + normalized * 0.5})`;
      if (normalized < 0.7) return `rgba(245, 158, 11, ${0.5 + normalized * 0.4})`;
      return `rgba(34, 197, 94, ${0.6 + normalized * 0.3})`;
    
    default:
      return `rgba(100, 116, 139, ${0.5 + normalized * 0.4})`;
  }
}
