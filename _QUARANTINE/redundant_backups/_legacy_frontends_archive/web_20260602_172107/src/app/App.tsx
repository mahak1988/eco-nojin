import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { MapContainer, TileLayer, Circle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

// Types
interface Analysis {
  id: string;
  region: string;
  crop: string;
  ndvi: number;
  profit: number;
  created_at: string;
}

interface Region {
  name: string;
  lat: number;
  lon: number;
  climate: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function App() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>('خراسان رضوی');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    fetchRegions();
    fetchAnalyses();
  }, []);

  useEffect(() => {
    if (sessionId) {
      connectWebSocket(sessionId);
    }
  }, [sessionId]);

  const fetchRegions = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/regions');
      const data = await res.json();
      setRegions(data.regions);
    } catch (err) {
      console.error('Error fetching regions:', err);
    }
  };

  const fetchAnalyses = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyses');
      const data = await res.json();
      setAnalyses(data.analyses);
    } catch (err) {
      console.error('Error fetching analyses:', err);
    }
  };

  const connectWebSocket = (sid: string) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/analyze/${sid}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
      
      if (data.event_type === 'final') {
        setTimeout(() => fetchAnalyses(), 1000);
      }
    };

    ws.onclose = () => {
      setSessionId(null);
    };
  };

  const startAnalysis = async () => {
    setLoading(true);
    setEvents([]);
    
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'تحلیل جامع اقتصادی و محیط‌زیستی',
          region: selectedRegion,
          crop: 'گندم',
          area_ha: 10
        })
      });
      
      const data = await res.json();
      setSessionId(data.session_id);
    } catch (err) {
      console.error('Error starting analysis:', err);
      setLoading(false);
    }
  };

  const ndviData = analyses.map(a => ({
    name: a.region,
    ndvi: a.ndvi,
    profit: a.profit / 1000000
  }));

  const regionDistribution = regions.map(r => ({
    name: r.name,
    value: analyses.filter(a => a.region === r.name).length
  })).filter(r => r.value > 0);

  return (
    <div className="app" dir="rtl">
      <header className="header">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="title"
        >
          🛰️ Econojin Advanced
        </motion.h1>
        <p className="subtitle">پلتفرم پیشرفته تصمیمیار کشاورزی و پایش محیط زیست</p>
      </header>

      <div className="dashboard">
        {/* Control Panel */}
        <motion.div 
          className="control-panel"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2>🎛️ پنل کنترل</h2>
          
          <div className="form-group">
            <label>انتخاب منطقه:</label>
            <select 
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="select-input"
            >
              {regions.map(region => (
                <option key={region.name} value={region.name}>
                  {region.name}
                </option>
              ))}
            </select>
          </div>

          <motion.button
            className="analyze-btn"
            onClick={startAnalysis}
            disabled={loading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {loading ? '⏳ در حال تحلیل...' : '🚀 شروع تحلیل'}
          </motion.button>

          {/* Real-time Events */}
          <AnimatePresence>
            {events.length > 0 && (
              <motion.div 
                className="events-log"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <h3>📡 رویدادهای بلادرنگ</h3>
                {events.slice(-5).map((event, idx) => (
                  <motion.div 
                    key={idx}
                    className={`event-item ${event.event_type}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <span className="event-time">
                      {new Date(event.timestamp * 1000).toLocaleTimeString('fa-IR')}
                    </span>
                    <span className="event-message">{event.message}</span>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Charts Section */}
        <div className="charts-section">
          {/* NDVI Chart */}
          <motion.div 
            className="chart-card"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h3>📊 شاخص NDVI مناطق</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={ndviData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" stroke="#fff" angle={-45} textAnchor="end" height={100} />
                <YAxis stroke="#fff" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                <Legend />
                <Line type="monotone" dataKey="ndvi" stroke="#10b981" strokeWidth={3} name="NDVI" />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Profit Chart */}
          <motion.div 
            className="chart-card"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h3>💰 سود تخمینی (میلیون تومان)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ndviData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" stroke="#fff" angle={-45} textAnchor="end" height={100} />
                <YAxis stroke="#fff" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                <Bar dataKey="profit" fill="#3b82f6" name="سود (میلیون تومان)" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Region Distribution Pie Chart */}
          <motion.div 
            className="chart-card"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h3>🗺️ توزیع تحلیل‌ها بر اساس منطقه</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={regionDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {regionDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Map Section */}
        <motion.div 
          className="map-section"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
        >
          <h3> نقشه مناطق تحلیل‌شده</h3>
          <MapContainer center={[35.5, 53]} zoom={6} style={{ height: '400px', width: '100%' }}>
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {analyses.map((analysis, idx) => {
              const region = regions.find(r => r.name === analysis.region);
              if (!region) return null;
              
              return (
                <Circle
                  key={idx}
                  center={[region.lat, region.lon]}
                  pathOptions={{ 
                    color: analysis.ndvi > 0.5 ? '#10b981' : analysis.ndvi > 0.3 ? '#f59e0b' : '#ef4444',
                    fillColor: analysis.ndvi > 0.5 ? '#10b981' : analysis.ndvi > 0.3 ? '#f59e0b' : '#ef4444',
                    fillOpacity: 0.6
                  }}
                  radius={20000}
                >
                  <Popup>
                    <div className="popup-content">
                      <strong>{analysis.region}</strong><br />
                      محصول: {analysis.crop}<br />
                      NDVI: {analysis.ndvi}<br />
                      سود: {(analysis.profit / 1000000).toFixed(2)} میلیون تومان
                    </div>
                  </Popup>
                </Circle>
              );
            })}
          </MapContainer>
        </motion.div>

        {/* Analyses Table */}
        <motion.div 
          className="table-section"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <h3>📋 جدول تحلیل‌های انجام‌شده</h3>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>شناسه</th>
                  <th>منطقه</th>
                  <th>محصول</th>
                  <th>NDVI</th>
                  <th>سود (میلیون تومان)</th>
                  <th>تاریخ</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map((analysis) => (
                  <tr key={analysis.id}>
                    <td>{analysis.id}</td>
                    <td>{analysis.region}</td>
                    <td>{analysis.crop}</td>
                    <td>
                      <span className={`ndvi-badge ${analysis.ndvi > 0.5 ? 'good' : analysis.ndvi > 0.3 ? 'medium' : 'bad'}`}>
                        {analysis.ndvi.toFixed(3)}
                      </span>
                    </td>
                    <td>{(analysis.profit / 1000000).toFixed(2)}</td>
                    <td>{new Date(analysis.created_at).toLocaleDateString('fa-IR')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default App;