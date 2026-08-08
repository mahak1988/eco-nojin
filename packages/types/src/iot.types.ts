// IoT device and sensor type definitions
export interface IoTDevice {
  id: string;
  name: string;
  type: IoTDeviceType;
  status: IoTDeviceStatus;
  location?: { lat: number; lng: number };
  farm_id?: string;
  lastReading?: string;
  battery?: number;
  firmware?: string;
}

export type IoTDeviceType = 'soil_moisture' | 'weather_station' | 'water_meter' | 'camera' | 'drone' | 'gateway';

export type IoTDeviceStatus = 'online' | 'offline' | 'maintenance' | 'error';

export interface SensorReading {
  device_id: string;
  timestamp: string;
  type: string;
  value: number;
  unit: string;
}

export interface IoTAlert {
  id: string;
  device_id: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}