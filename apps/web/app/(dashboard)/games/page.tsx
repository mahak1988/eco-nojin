"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Gamepad2, Trophy, Clock, Users, Star,
  Filter, X, Maximize2, RotateCcw, BookOpen, TrendingUp
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/games";

const CATEGORIES = [
  { id: "all", name: "همه بازی‌ها", icon: "🎮", color: "#8b5cf6" },
  { id: "ENVIRONMENT", name: "محیط زیست", icon: "🌍", color: "#10b981" },
  { id: "AGRICULTURE", name: "کشاورزی", icon: "🌾", color: "#84cc16" },
  { id: "CLIMATE", name: "تغییر اقلیم", icon: "🌡️", color: "#f59e0b" },
  { id: "WATER", name: "مدیریت آب", icon: "💧", color: "#3b82f6" },
  { id: "PUZZLE", name: "پازل و منطق", icon: "🧩", color: "#8b5cf6" },
  { id: "SCIENCE", name: "علوم پایه", icon: "🔬", color: "#ec4899" },
  { id: "MATH", name: "ریاضیات", icon: "📐", color: "#6366f1" },
  { id: "STRATEGY", name: "استراتژی", icon: "♟️", color: "#f97316" },
];

export default function GamesPage() {
  const [games, setGames] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedGame, setSelectedGame] = useState(null);
  const [showIframe, setShowIframe] = useState(false);
  const [userProgress, setUserProgress] = useState(null);
  const [stats, setStats] = useState(null);
  const iframeRef = useRef(null);

  useEffect(() => {
    loadGames();
    loadStats();
  }, [selectedCategory]);

  const loadGames = async () => {
    const params = selectedCategory !== "all" ? `?category=${selectedCategory}` : "";
    const res = await fetch(`${API_BASE}/list${params}`);
    const data = await res.json();
    setGames(data.games || []);
  };

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      } else {
        setStats({ total_games: 0, total_plays: 0, categories_count: 8 });
      }
    } catch (error) {
      console.error("Failed to load stats:", error);
      setStats({ total_games: 0, total_plays: 0, categories_count: 8 });
    }
  };

  const startGame = async (game) => {
    setSelectedGame(game);
    setShowIframe(true);
    // ثبت شروع بازی
    await fetch(`${API_BASE}/progress`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1, game_id: game.id, time_spent_minutes: 0 })
    });
  };

  const closeGame = () => {
    setShowIframe(false);
    setSelectedGame(null);
    loadGames(); // به‌روزرسانی آمار
  };

  const getCategoryColor = (catId) => {
    const cat = CATEGORIES.find(c => c.id === catId);
    return cat?.color || "#8b5cf6";
  };

  const getCategoryIcon = (catId) => {
    const cat = CATEGORIES.find(c => c.id === catId);
    return cat?.icon || "🎮";
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600 to-pink-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-2xl">
                <Gamepad2 className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-purple-400 text-sm font-medium mb-1">یادگیری از طریق بازی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">بازی‌های آموزشی اکو نوژین</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  30+ بازی آموزشی تعاملی در حوزه محیط زیست، کشاورزی پایدار، تغییر اقلیم و علوم پایه
                </p>
              </div>
            </div>

            {/* Stats */}
            {stats && (
              <div className="flex gap-6 mt-6">
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                  <Gamepad2 className="h-5 w-5 text-purple-400" />
                  <span className="text-white font-bold">{(stats?.total_games || 0)}</span>
                  <span className="text-slate-400 text-sm">بازی آموزشی</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                  <Trophy className="h-5 w-5 text-amber-400" />
                  <span className="text-white font-bold">{(stats?.total_plays || 0).toLocaleString()}</span>
                  <span className="text-slate-400 text-sm">بازی انجام‌شده</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                  <BookOpen className="h-5 w-5 text-emerald-400" />
                  <span className="text-white font-bold">8</span>
                  <span className="text-slate-400 text-sm">دسته‌بندی</span>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Game Player Modal */}
      <AnimatePresence>
        {showIframe && selectedGame && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-6xl h-[90vh] flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedGame.title}</h2>
                  <p className="text-sm text-slate-400">{selectedGame.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => iframeRef.current?.requestFullscreen()}
                    className="p-2 text-slate-400 hover:text-white transition-colors"
                    title="تمام صفحه"
                  >
                    <Maximize2 className="h-5 w-5" />
                  </button>
                  <button
                    onClick={closeGame}
                    className="p-2 text-slate-400 hover:text-white transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              {/* Iframe */}
              <div className="flex-1 bg-black">
                <iframe
                  ref={iframeRef}
                  src={selectedGame.embed_url}
                  className="w-full h-full border-0"
                  allow="fullscreen"
                  allowFullScreen
                  title={selectedGame.title}
                />
              </div>
              
              {/* Footer */}
              <div className="p-4 border-t border-slate-800 bg-slate-900">
                <div className="flex items-center justify-between text-sm text-slate-400">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {selectedGame.duration_minutes} دقیقه
                    </span>
                    <span className="flex items-center gap-1">
                      <Trophy className="h-4 w-4" />
                      سطح: {selectedGame.difficulty === "easy" ? "آسان" : selectedGame.difficulty === "medium" ? "متوسط" : "سخت"}
                    </span>
                  </div>
                  <button onClick={closeGame} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold">
                    پایان بازی
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <section className="container mx-auto px-6 py-8">
        {/* Categories Filter */}
        <div className="flex gap-3 mb-8 overflow-x-auto pb-2 scrollbar-hide">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                selectedCategory === cat.id
                  ? "text-white shadow-lg"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={selectedCategory === cat.id ? { backgroundColor: cat.color } : {}}
            >
              <span>{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* Games Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {games.map((game, idx) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-purple-500/50 transition-all group cursor-pointer"
              onClick={() => startGame(game)}
            >
              {/* Thumbnail */}
              <div className="relative h-48 bg-slate-800 overflow-hidden">
                {game.thumbnail_url ? (
                  <img
                    src={game.thumbnail_url}
                    alt={game.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-6xl">
                    {getCategoryIcon(game.category)}
                  </div>
                )}
                <div
                  className="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-bold text-white"
                  style={{ backgroundColor: getCategoryColor(game.category) }}
                >
                  {getCategoryIcon(game.category)} {game.category}
                </div>
              </div>

              {/* Content */}
              <div className="p-5">
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                  {game.title}
                </h3>
                <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                  {game.description}
                </p>

                {/* Meta Info */}
                <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {game.duration_minutes} دقیقه
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {game.play_count.toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <Star className="h-3 w-3 text-amber-400" />
                    {game.rating_average || "جدید"}
                  </span>
                </div>

                {/* Difficulty Badge */}
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-1 rounded text-xs font-bold ${
                      game.difficulty === "easy"
                        ? "bg-emerald-500/20 text-emerald-300"
                        : game.difficulty === "medium"
                        ? "bg-amber-500/20 text-amber-300"
                        : "bg-red-500/20 text-red-300"
                    }`}
                  >
                    {game.difficulty === "easy" ? "آسان" : game.difficulty === "medium" ? "متوسط" : "سخت"}
                  </span>
                  <button onClick={() => console.log("Button clicked")}  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-bold transition-colors">
                    شروع بازی
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {games.length === 0 && (
          <div className="text-center py-20">
            <Gamepad2 className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">هیچ بازی‌ای در این دسته‌بندی یافت نشد</p>
          </div>
        )}
      </section>
    </div>
  );
}