import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedLogo } from '../components/motion/AnimatedLogo';
import { FadeIn } from '../components/motion/FadeIn';
import { StaggerChildren } from '../components/motion/StaggerChildren';

// ── Types ──────────────────────────────────────────────────────
interface Simulator {
  id: string;
  name: string;
  category: string;
  description: string;
  version: string;
  parameters_count: number;
}

interface SimulatorParameter {
  name: string;
  label: string;
  type: string;
  default: any;
  description: string;
  unit: string;
  min_value?: number;
  max_value?: number;
  options?: string[];
  required: boolean;
}

interface SimulationResult {
  run_id: string;
  simulator_id: string;
  simulator_name: string;
  status: string;
  outputs: Record<string, any>;
  metrics: Record<string, number>;
  charts: Record<string, number[]>;
  error?: string;
  execution_time_ms: number;
}

// ── Category Icons ─────────────────────────────────────────────
const categoryIcons: Record<string, string> = {
  agriculture: '🌾',
  hydrology: '💧',
  'carbon-cycle': '🌿',
  economics: '💰',
  'ecosystem-services': '🌍',
  energy: '⚡',
  soil: '🪨',
  'water-quality': '🚰',
  biodiversity: '🦋',
  climate: '🌤️',
  urban: '🏙️',
};

const categoryColors: Record<string, string> = {
  agriculture: 'from-green-500 to-emerald-600',
  hydrology: 'from-blue-500 to-cyan-600',
  'carbon-cycle': 'from-teal-500 to-green-600',
  economics: 'from-amber-500 to-yellow-600',
  'ecosystem-services': 'from-emerald-500 to-teal-600',
  energy: 'from-orange-500 to-red-600',
  soil: 'from-stone-500 to-amber-600',
  'water-quality': 'from-sky-500 to-blue-600',
  biodiversity: 'from-purple-500 to-pink-600',
  climate: 'from-yellow-500 to-orange-600',
  urban: 'from-gray-500 to-slate-600',
};

// ── Simulation Dashboard Component ─────────────────────────────
const SimulationDashboard: React.FC = () => {
  const [simulators, setSimulators] = useState<Simulator[]>([]);
  const [categories, setCategories] = useState<Record<string, { count: number; simulators: string[] }>>({});
  const [selectedSim, setSelectedSim] = useState<Simulator | null>(null);
  const [parameters, setParameters] = useState<SimulatorParameter[]>([]);
  const [paramValues, setParamValues] = useState<Record<string, any>>({});
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch simulators on mount
  useEffect(() => {
    fetchSimulators();
  }, []);

  const fetchSimulators = async () => {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const [simRes, catRes] = await Promise.all([
        fetch(`${baseUrl}/api/v1/simulation/simulators`),
        fetch(`${baseUrl}/api/v1/simulation/categories`),
      ]);
      const simData = await simRes.json();
      const catData = await catRes.json();
      setSimulators(simData.simulators || []);
      setCategories(catData.categories || {});
    } catch (err) {
      console.error('Failed to fetch simulators:', err);
    }
  };

  const selectSimulator = async (sim: Simulator) => {
    setSelectedSim(sim);
    setResult(null);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/v1/simulation/simulators/${sim.id}`);
      const data = await res.json();
      setParameters(data.parameters || []);
      // Set default values
      const defaults: Record<string, any> = {};
      (data.parameters || []).forEach((p: SimulatorParameter) => {
        defaults[p.name] = p.default ?? '';
      });
      setParamValues(defaults);
    } catch (err) {
      console.error('Failed to fetch parameters:', err);
    }
  };

  const runSimulation = async () => {
    if (!selectedSim) return;
    setLoading(true);
    setResult(null);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/v1/simulation/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulator_id: selectedSim.id,
          parameters: paramValues,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setResult({
        run_id: '',
        simulator_id: selectedSim.id,
        simulator_name: selectedSim.name,
        status: 'failed',
        outputs: {},
        metrics: {},
        charts: {},
        error: err.message,
        execution_time_ms: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredSimulators = simulators.filter((sim) => {
    const matchesCategory = !activeCategory || sim.category === activeCategory;
    const matchesSearch = !searchQuery || 
      sim.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sim.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-green-50" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-green-100">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <AnimatedLogo size="md" />
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              {simulators.length} شبیه‌ساز
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6">
        {/* Sidebar - Categories */}
        <aside className="w-64 shrink-0">
          <FadeIn>
            <div className="bg-white rounded-xl shadow-sm border border-green-100 p-4">
              <h3 className="font-bold text-gray-800 mb-3">دسته‌بندی‌ها</h3>
              <button
                onClick={() => setActiveCategory(null)}
                className={`w-full text-right px-3 py-2 rounded-lg mb-1 transition ${
                  !activeCategory ? 'bg-green-100 text-green-800' : 'hover:bg-gray-50'
                }`}
              >
                همه شبیه‌سازها
              </button>
              {Object.entries(categories).map(([cat, info]) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`w-full text-right px-3 py-2 rounded-lg mb-1 transition flex items-center justify-between ${
                    activeCategory === cat ? 'bg-green-100 text-green-800' : 'hover:bg-gray-50'
                  }`}
                >
                  <span>
                    {categoryIcons[cat] || '📦'} {cat}
                  </span>
                  <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full">
                    {info.count}
                  </span>
                </button>
              ))}
            </div>
          </FadeIn>
        </aside>

        {/* Main Content */}
        <main className="flex-1">
          {/* Search */}
          <FadeIn>
            <div className="mb-6">
              <input
                type="text"
                placeholder="جستجوی شبیه‌ساز..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-green-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition"
              />
            </div>
          </FadeIn>

          {/* Simulator Grid */}
          <StaggerChildren>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <AnimatePresence>
                {filteredSimulators.map((sim) => (
                  <motion.div
                    key={sim.id}
                    layout
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    whileHover={{ y: -4 }}
                    onClick={() => selectSimulator(sim)}
                    className={`bg-white rounded-xl shadow-sm border-2 cursor-pointer overflow-hidden transition ${
                      selectedSim?.id === sim.id
                        ? 'border-green-500 shadow-md'
                        : 'border-gray-100 hover:border-green-200'
                    }`}
                  >
                    <div className={`h-2 bg-gradient-to-r ${categoryColors[sim.category] || 'from-green-500 to-emerald-500'}`} />
                    <div className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">{categoryIcons[sim.category] || '📦'}</span>
                        <h3 className="font-bold text-gray-800 text-sm">{sim.name}</h3>
                      </div>
                      <p className="text-xs text-gray-500 line-clamp-2 mb-3">{sim.description}</p>
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span>{sim.parameters_count} پارامتر</span>
                        <span className="bg-gray-100 px-2 py-0.5 rounded">{sim.category}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </StaggerChildren>

          {/* Selected Simulator Panel */}
          <AnimatePresence>
            {selectedSim && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="mt-8 bg-white rounded-xl shadow-sm border border-green-100 p-6"
              >
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">{categoryIcons[selectedSim.category] || '📦'}</span>
                  <div>
                    <h2 className="text-xl font-bold text-gray-800">{selectedSim.name}</h2>
                    <p className="text-sm text-gray-500">{selectedSim.description}</p>
                  </div>
                </div>

                {/* Parameters Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {parameters.map((param) => (
                    <div key={param.name}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {param.label}
                        {param.required && <span className="text-red-500 mr-1">*</span>}
                        {param.unit && <span className="text-gray-400 text-xs mr-1">({param.unit})</span>}
                      </label>
                      {param.type === 'select' ? (
                        <select
                          value={paramValues[param.name] || ''}
                          onChange={(e) => setParamValues({ ...paramValues, [param.name]: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:border-green-500 outline-none"
                        >
                          <option value="">انتخاب کنید</option>
                          {(param.options || []).map((opt) => (
                            <option key={opt} value={opt}>{opt}</option>
                          ))}
                        </select>
                      ) : param.type === 'boolean' ? (
                        <input
                          type="checkbox"
                          checked={paramValues[param.name] || false}
                          onChange={(e) => setParamValues({ ...paramValues, [param.name]: e.target.checked })}
                          className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                        />
                      ) : (
                        <input
                          type={param.type === 'int' ? 'number' : param.type === 'float' ? 'number' : 'text'}
                          step={param.type === 'float' ? '0.01' : '1'}
                          min={param.min_value}
                          max={param.max_value}
                          value={paramValues[param.name] || ''}
                          onChange={(e) => setParamValues({ ...paramValues, [param.name]: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:border-green-500 outline-none"
                          placeholder={param.description}
                        />
                      )}
                      {param.description && (
                        <p className="text-xs text-gray-400 mt-1">{param.description}</p>
                      )}
                    </div>
                  ))}
                </div>

                {/* Run Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={runSimulation}
                  disabled={loading}
                  className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-bold shadow-lg hover:shadow-xl disabled:opacity-50 transition"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      در حال اجرا...
                    </span>
                  ) : (
                    '▶ اجرای شبیه‌سازی'
                  )}
                </motion.button>

                {/* Results */}
                <AnimatePresence>
                  {result && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-6"
                    >
                      <div className={`p-4 rounded-xl ${
                        result.status === 'completed' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                      }`}>
                        <div className="flex items-center gap-2 mb-3">
                          <span className={`text-lg ${result.status === 'completed' ? 'text-green-600' : 'text-red-600'}`}>
                            {result.status === 'completed' ? '✅' : '❌'}
                          </span>
                          <span className={`font-bold ${result.status === 'completed' ? 'text-green-800' : 'text-red-800'}`}>
                            {result.status === 'completed' ? 'شبیه‌سازی با موفقیت انجام شد' : 'خطا در اجرای شبیه‌سازی'}
                          </span>
                          <span className="text-xs text-gray-400 mr-auto">
                            {(result.execution_time_ms / 1000).toFixed(2)} ثانیه
                          </span>
                        </div>

                        {result.error && (
                          <p className="text-sm text-red-600 mb-3">{result.error}</p>
                        )}

                        {/* Metrics */}
                        {Object.keys(result.metrics).length > 0 && (
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                            {Object.entries(result.metrics).map(([key, value]) => (
                              <div key={key} className="bg-white rounded-lg p-3 shadow-sm">
                                <div className="text-xs text-gray-500 mb-1">{key}</div>
                                <div className="text-lg font-bold text-green-700">{value.toFixed(2)}</div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Outputs */}
                        {Object.keys(result.outputs).length > 0 && (
                          <div className="bg-white rounded-lg p-4">
                            <h4 className="font-bold text-gray-700 mb-2">خروجی‌ها</h4>
                            <pre className="text-xs text-gray-600 overflow-auto max-h-60">
                              {JSON.stringify(result.outputs, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};

export default SimulationDashboard;