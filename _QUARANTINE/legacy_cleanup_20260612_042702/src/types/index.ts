// ... (کدهای قبلی را نگه دارید)

// ساختار داده‌های اقتصادی ورودی
export interface EconomicInputs {
  area: number;
  yieldPerHa: number;
  pricePerTon: number;
  waterCost: number;
  laborCost: number;
}

// ساختار داده‌های نمودار NDVI
export interface NdviDataPoint {
  date: string;
  ndvi: number;
}

// ساختار داده‌های نمودار سود
export interface ProfitDataPoint {
  item: string;
  value: number;
  color: string;
}

// به‌روزرسانی RealtimeEvent برای پشتیبانی از دیتای پیچیده
export interface RealtimeEvent {
  event_type: 'start' | 'processing' | 'final' | 'error';
  timestamp: number;
  message: string;
  data?: any; // ساختار تو در تو از بک‌اند
}