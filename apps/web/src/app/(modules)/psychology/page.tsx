"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Brain, Leaf, Shield, Users, Briefcase, CheckCircle, ChevronRight, RotateCcw } from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const RadarChart = dynamic(() => import("recharts").then(m => m.RadarChart), { ssr: false });
const PolarGrid = dynamic(() => import("recharts").then(m => m.PolarGrid), { ssr: false });
const PolarAngleAxis = dynamic(() => import("recharts").then(m => m.PolarAngleAxis), { ssr: false });
const PolarRadiusAxis = dynamic(() => import("recharts").then(m => m.PolarRadiusAxis), { ssr: false });
const Radar = dynamic(() => import("recharts").then(m => m.Radar), { ssr: false });

const API_BASE = "http://localhost:8000/api/v1/psychology";
const CATEGORIES = [
  { id: "all", name: "همه آزمون‌ها", icon: <Brain className="h-5 w-5" /> },
  { id: "CLINICAL", name: "شخصیت و بالینی", icon: <Brain className="h-5 w-5" /> },
  { id: "ECO_PSYCHOLOGY", name: "طبیعت‌دوستی", icon: <Leaf className="h-5 w-5" /> },
  { id: "CLIMATE_RESILIENCE", name: "تاب‌آوری اقلیمی", icon: <Shield className="h-5 w-5" /> },
  { id: "PRO_SOCIAL", name: "همگرومی و اجتماعی", icon: <Users className="h-5 w-5" /> },
  { id: "OCCUPATIONAL", name: "شغلی و کشاورزی", icon: <Briefcase className="h-5 w-5" /> },
];

export default function PsychologyPage() {
  const [tests, setTests] = useState([]);
  const [activeCategory, setActiveCategory] = useState("all");
  const [currentTest, setCurrentTest] = useState(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/tests?category=${activeCategory === "all" ? "" : activeCategory}`)
      .then(res => res.json())
      .then(data => setTests(data.tests || []));
  }, [activeCategory]);

  const startTest = async (testCode) => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/tests/${testCode}`);
    const data = await res.json();
    setCurrentTest(data);
    setCurrentQIndex(0);
    setAnswers([]);
    setResult(null);
    setLoading(false);
  };

  const handleAnswer = (option) => {
    const newAnswers = [...answers, { question_id: currentTest.questions[currentQIndex].id, score_value: option.score_value }];
    setAnswers(newAnswers);
    if (currentQIndex < currentTest.questions.length - 1) {
      setCurrentQIndex(currentQIndex + 1);
    } else {
      submitAnswers(newAnswers);
    }
  };

  const submitAnswers = async (finalAnswers) => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1, test_code: currentTest.test.code, answers: finalAnswers })
    });
    const data = await res.json();
    setResult(data.result);
    setLoading(false);
  };

  const reset = () => { setCurrentTest(null); setResult(null); setAnswers([]); };

  if (loading && !currentTest) return <div className="min-h-screen flex items-center justify-center text-white">در حال بارگذاری...</div>;

  if (currentTest && !result) {
    const q = currentTest.questions[currentQIndex];
    const progress = ((currentQIndex + 1) / currentTest.questions.length) * 100;
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">{currentTest.test.title}</h2>
            <button onClick={reset} className="text-slate-400 hover:text-white"><RotateCcw className="h-5 w-5" /></button>
          </div>
          <div className="h-2 bg-slate-800 rounded-full mb-8"><div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${progress}%` }} /></div>
          <p className="text-2xl text-white mb-8 leading-relaxed">{q.text}</p>
          <div className="space-y-3">
            {q.options.map((opt, idx) => (
              <button key={idx} onClick={() => handleAnswer(opt)} className="w-full text-right p-4 bg-slate-800 hover:bg-emerald-600/20 hover:border-emerald-500 border border-slate-700 rounded-xl text-white transition-all">
                {opt.label}
              </button>
            ))}
          </div>
          <p className="text-center text-slate-500 mt-6">سؤال {currentQIndex + 1} از {currentTest.questions.length}</p>
        </div>
      </div>
    );
  }

  if (result) {
    const radarData = Object.entries(result.subscale_scores).map(([key, value]) => ({ subject: key, A: value, fullMark: 25 }));
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
          <CheckCircle className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
          <h2 className="text-3xl font-black text-white mb-2">نتیجه آزمون: {result.test_title}</h2>
          <div className="inline-block px-4 py-2 rounded-full text-white font-bold mb-6" style={{ backgroundColor: result.color }}>
            سطح شما: {result.level} ({result.percentage}٪)
          </div>
          
          {radarData.length > 1 && (
            <div className="h-80 w-full mb-6">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 25]} tick={false} axisLine={false} />
                  <Radar name="نمره شما" dataKey="A" stroke="#10b981" fill="#10b981" fillOpacity={0.4} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
          
          <div className="rounded-xl p-6 text-right mb-6 border-r-4 bg-slate-800/30" style={{ borderColor: result.color }}>
            <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: result.color }}></span>
              تحلیل علمی دقیق: {result.level}
            </h3>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-bold text-slate-300 mb-1">🔍 تفسیر بالینی/روانشناختی:</h4>
                <p className="text-slate-200 leading-relaxed text-justify">{result.analysis}</p>
              </div>
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                <h4 className="text-sm font-bold text-emerald-400 mb-1">💡 توصیه مداخله‌ای و عملی:</h4>
                <p className="text-slate-300 leading-relaxed text-justify">{result.advice}</p>
              </div>
              <div className="text-xs text-slate-500 text-left mt-2">
                نمره کسب شده: {result.total_score} از {result.max_score || 25}
              </div>
            </div>
          </div>
          
          <button onClick={reset} className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold">بازگشت به لیست آزمون‌ها</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="container mx-auto px-6 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 mb-8"><ArrowRight className="h-4 w-4" /> بازگشت</Link>
        <h1 className="text-4xl font-black text-white mb-8">مرکز آزمون‌های روانشناسی و اکو-روانشناسی</h1>
        
        <div className="flex gap-3 mb-8 overflow-x-auto pb-2">
          {CATEGORIES.map(cat => (
            <button key={cat.id} onClick={() => setActiveCategory(cat.id)} className={`px-5 py-3 rounded-xl font-bold flex items-center gap-2 whitespace-nowrap ${activeCategory === cat.id ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"}`}>
              {cat.icon} {cat.name}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tests.map((test, idx) => (
            <motion.div key={test.code} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all cursor-pointer group"
              onClick={() => startTest(test.code)}>
              <div className="flex justify-between items-start mb-4">
                <span className="px-3 py-1 text-xs rounded-full font-bold" style={{ backgroundColor: (test.category === "CLINICAL" ? "#6366f120" : test.category === "ECO_PSYCHOLOGY" ? "#10b98120" : test.category === "CLIMATE_RESILIENCE" ? "#06b6d420" : test.category === "PRO_SOCIAL" ? "#f59e0b20" : "#78716c20"), color: (test.category === "CLINICAL" ? "#818cf8" : test.category === "ECO_PSYCHOLOGY" ? "#34d399" : test.category === "CLIMATE_RESILIENCE" ? "#22d3ee" : test.category === "PRO_SOCIAL" ? "#fbbf24" : "#a8a29e") }}>{test.category}</span>
                <span className="text-slate-500 text-sm">{test.duration_minutes} دقیقه</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-400 transition-colors">{test.title}</h3>
              <div className="flex items-center text-emerald-400 text-sm font-bold mt-4">شروع آزمون <ChevronRight className="h-4 w-4" /></div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}