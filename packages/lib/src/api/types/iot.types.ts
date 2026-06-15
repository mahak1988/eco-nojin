/**
 * IoT Domain Types
 * تعاریف تایپ مرتبط با اینترنت اشیاء
 */

export interface IoTDevice {
  id: string;
  name: string;
  type: DeviceType;
  location: {
    lat: number;
    lon: number;
  };
  status: 'ONLINE' | 'OFFLINE' | 'MAINTENANCE';
  last_seen: string;
  battery_level?: number;
}

export type DeviceType = 
  | 'SOIL_MOISTURE_SENSOR'
  | 'WEATHER_STATION'
  | 'WATER_LEVEL_SENSOR'
  | 'AIR_QUALITY_SENSOR'
  | 'CAMERA';

export interface SensorReading {
  device_id: string;
  timestamp: string;
  metrics: Record<string, number>;
  quality: 'GOOD' | 'SUSPICIOUS' | 'BAD';
}

export interface MQTTMessage {
  topic: string;
  payload: Record<string, unknown>;
  qos: 0 | 1 | 2;
  timestamp: string;
}
