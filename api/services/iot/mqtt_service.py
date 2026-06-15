"""MQTT Service for IoT Device Communication

این سرویس ارتباط با دستگاه‌های IoT از طریق پروتکل MQTT را مدیریت می‌کند.
"""
import paho.mqtt.client as mqtt
import json
import ssl
from typing import Callable, Optional, Dict
from datetime import datetime
import threading
import os


class MQTTService:
    """سرویس MQTT برای ارتباط با حسگرهای IoT"""
    
    def __init__(
        self,
        broker_host: Optional[str] = None,
        broker_port: int = 1883,
        client_id: str = "econojin_iot_gateway"
    ):
        self.broker_host = broker_host or os.getenv('MQTT_BROKER_HOST', 'localhost')
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=self.client_id)
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        
        # تنظیمات امنیتی
        self.username = os.getenv('MQTT_USERNAME')
        self.password = os.getenv('MQTT_PASSWORD')
        
        # تنظیم callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback هنگام اتصال"""
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Subscribe به topics
            self.subscribe("econojin/sensors/+/telemetry")
            self.subscribe("econojin/sensors/+/status")
            self.subscribe("econojin/sensors/+/alert")
        else:
            print(f"❌ Failed to connect to MQTT broker, return code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback هنگام قطع اتصال"""
        self.connected = False
        print(f"⚠️  Disconnected from MQTT broker (rc={rc})")
    
    def _on_message(self, client, userdata, msg):
        """Callback هنگام دریافت پیام"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # استخراج device_id از topic
            parts = topic.split('/')
            if len(parts) >= 3:
                device_id = parts[2]
                payload['device_id'] = device_id
                payload['timestamp'] = datetime.utcnow().isoformat()
            
            # فراخوانی handler مناسب
            if topic in self.message_handlers:
                self.message_handlers[topic](payload)
            else:
                # فراخوانی handler عمومی
                if 'telemetry' in topic:
                    self._handle_telemetry(payload)
                elif 'status' in topic:
                    self._handle_status(payload)
                elif 'alert' in topic:
                    self._handle_alert(payload)
        
        except Exception as e:
            print(f"❌ Error processing MQTT message: {e}")
    
    def _handle_telemetry(self, payload: Dict):
        """پردازش داده‌های تلمتری"""
        print(f"📊 Telemetry from {payload.get('device_id')}: {payload.get('value')}")
        # اینجا باید به Repository متصل شود
    
    def _handle_status(self, payload: Dict):
        """پردازش تغییر وضعیت دستگاه"""
        print(f"🔄 Status update from {payload.get('device_id')}: {payload.get('status')}")
    
    def _handle_alert(self, payload: Dict):
        """پردازش هشدار از دستگاه"""
        print(f"🚨 Alert from {payload.get('device_id')}: {payload.get('message')}")
    
    def connect(self):
        """اتصال به broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"❌ Error connecting to MQTT broker: {e}")
    
    def disconnect(self):
        """قطع اتصال"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def subscribe(self, topic: str, qos: int = 1):
        """Subscribe به یک topic"""
        self.client.subscribe(topic, qos)
        print(f"📥 Subscribed to topic: {topic}")
    
    def publish(self, topic: str, payload: Dict, qos: int = 1):
        """انتشار پیام"""
        if not self.connected:
            print("❌ Not connected to MQTT broker")
            return False
        
        try:
            self.client.publish(topic, json.dumps(payload), qos)
            return True
        except Exception as e:
            print(f"❌ Error publishing message: {e}")
            return False
    
    def register_handler(self, topic: str, handler: Callable):
        """ثبت handler سفارشی برای یک topic"""
        self.message_handlers[topic] = handler
    
    def send_command(self, device_id: str, command: str, params: Dict = None):
        """ارسال فرمان به دستگاه"""
        topic = f"econojin/devices/{device_id}/command"
        payload = {
            'command': command,
            'params': params or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        return self.publish(topic, payload)
