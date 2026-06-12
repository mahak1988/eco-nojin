"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/hooks/useTranslation';
import { useAIChat, useSoilAnalysis, useWeatherAnalysis, useVegetationAnalysis } from '@/hooks/ai/useAI';
import { 
  Brain, Send, Leaf, Cloud, Sun, MessageCircle,
  TrendingUp, Lightbulb, Sparkles, Bot, Zap, Activity
} from 'lucide-react';

export default function AIPage() {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');
  const [displayedText, setDisplayedText] = useState('');
  const chatMutation = useAIChat();
  const soilAnalysis = useSoilAnalysis({ ph: 6.5, organic_carbon: 2.5, nitrogen: 0.15 });
  const weatherAnalysis = useWeatherAnalysis({ temperature: 28, humidity: 45, rainfall: 0 });
  const vegetationAnalysis = useVegetationAnalysis(0.65, 0.58);

  // Typing animation برای پاسخ‌های AI
  useEffect(() => {
    if (chatMutation.data?.response) {
      setDisplayedText('');
      let i = 0;
      const text = chatMutation.data.response;
      const interval = setInterval(() => {
        if (i < text.length) {
          setDisplayedText(text.substring(0, i + 1));
          i++;
        } else {
          clearInterval(interval);
        }
      }, 20);
      return () => clearInterval(interval);
    }
  }, [chatMutation.data]);

  const handleSend = () => {
    if (message.trim()) {
      chatMutation.mutate(message);
      setMessage('');
    }
  };

  const quickQuestions = [
    { text: 'چگونه آبیاری را بهینه کنم؟', icon: '💧' },
    { text: 'بهترین زمان کوددهی کی است؟', icon: '🌱' },
    { text: 'چگونه از آفات جلوگیری کنم؟', icon: '🐛' },
    { text: 'چقدر کربن جذب شده؟', icon: '🌿' }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Ambient Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div 
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `
              radial-gradient(at 20% 20%, rgba(139, 92, 246, 0.2) 0px, transparent 50%),
              radial-gradient(at 80% 80%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
              radial-gradient(at 50% 50%, rgba(59, 130, 246, 0.1) 0px, transparent 50%)
            `
          }}
        />
      </div>

      <div className="container mx-auto px-6 py-12 relative">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full text-purple-300 text-xs font-medium mb-6">
            <Bot className="w-3 h-3" />
            دستیار هوشمند کشاورزی
          </div>
          <h1 className="text-5xl sm:text-6xl font-black text-white mb-4 tracking-tight">
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-emerald-400 bg-clip-text text-transparent">
              هوش مصنوعی
            </span>
            <br />
            در خدمت کشاورزی
          </h1>
          <p className="text-lg text-zinc-400 max-w-2xl font-light">{t('ai.subtitle')}</p>
        </motion.div>

        {/* Chat Interface */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 p-8 shadow-2xl">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <div className="p-2 rounded-xl bg-purple-500/20">
                <MessageCircle className="w-6 h-6 text-purple-400" />
              </div>
              چت با دستیار هوشمند
            </h3>
            
            {/* Chat Messages */}
            <div className="bg-black/30 backdrop-blur-xl border border-white/5 rounded-2xl p-6 min-h-[200px] mb-6">
              <AnimatePresence mode="wait">
                {chatMutation.data ? (
                  <motion.div
                    key="response"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    <div className="flex gap-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-purple-500 rounded-full blur-lg opacity-50" />
                        <div className="relative w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                          <Brain className="w-5 h-5 text-white" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-purple-400 mb-2 font-medium">دستیار AI</div>
                        <p className="text-white leading-relaxed">{displayedText}</p>
                      </div>
                    </div>
                  </motion.div>
                ) : chatMutation.isPending ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-4"
                  >
                    <div className="relative">
                      <div className="absolute inset-0 bg-purple-500 rounded-full blur-lg opacity-50 animate-pulse" />
                      <div className="relative w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                        <Brain className="w-5 h-5 text-white animate-pulse" />
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                      <p className="text-zinc-400">در حال تحلیل...</p>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-12"
                  >
                    <div className="relative inline-block mb-4">
                      <div className="absolute inset-0 bg-purple-500 rounded-full blur-2xl opacity-30" />
                      <Sparkles className="relative w-16 h-16 mx-auto text-purple-400 opacity-50" />
                    </div>
                    <p className="text-zinc-400 text-lg">{t('ai.ask_question')}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {/* Input */}
            <div className="flex gap-3 mb-6">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="مثلاً: چگونه آبیاری را بهینه کنم؟"
                className="flex-1 bg-black/30 backdrop-blur-xl border-white/10 text-white placeholder-zinc-500 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 rounded-xl py-3"
              />
              <Button 
                onClick={handleSend} 
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 rounded-xl shadow-[0_0_30px_rgba(139,92,246,0.3)] hover:shadow-[0_0_40px_rgba(139,92,246,0.5)]"
                disabled={chatMutation.isPending}
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>

            {/* Quick Questions */}
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((q, idx) => (
                <Button
                  key={idx}
                  size="sm"
                  variant="outline"
                  onClick={() => setMessage(q.text)}
                  className="text-xs bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20 rounded-xl"
                >
                  <span className="mr-1">{q.icon}</span>
                  {q.text}
                </Button>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* AI Analyses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Soil Analysis */}
          {soilAnalysis.data && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 p-6 h-full shadow-2xl">
                <h3 className="text-xl font-bold text-white mb-5 flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-emerald-500/20">
                    <Leaf className="w-5 h-5 text-emerald-400" />
                  </div>
                  تحلیل هوشمند خاک
                </h3>
                <div className="space-y-3">
                  {soilAnalysis.data.insights?.map((insight: string, idx: number) => (
                    <motion.div 
                      key={idx} 
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + idx * 0.1 }}
                      className="bg-black/30 backdrop-blur-xl border border-white/5 rounded-xl p-4 flex gap-3"
                    >
                      <Lightbulb className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-white leading-relaxed">{insight}</p>
                    </motion.div>
                  ))}
                </div>
                {soilAnalysis.data.recommendations?.length > 0 && (
                  <div className="mt-5 pt-5 border-t border-white/10">
                    <div className="text-sm font-medium text-emerald-400 mb-3">توصیه‌ها:</div>
                    {soilAnalysis.data.recommendations.slice(0, 2).map((rec: any, idx: number) => (
                      <div key={idx} className="text-sm text-zinc-300 mb-2 flex gap-2">
                        <span className="text-emerald-400">•</span>
                        <span><strong>{rec.title}:</strong> {rec.description}</span>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </motion.div>
          )}

          {/* Weather Analysis */}
          {weatherAnalysis.data && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 p-6 h-full shadow-2xl">
                <h3 className="text-xl font-bold text-white mb-5 flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-blue-500/20">
                    <Cloud className="w-5 h-5 text-blue-400" />
                  </div>
                  تحلیل هوشمند هوا
                </h3>
                <div className="space-y-3">
                  {weatherAnalysis.data.insights?.map((insight: string, idx: number) => (
                    <motion.div 
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + idx * 0.1 }}
                      className="bg-black/30 backdrop-blur-xl border border-white/5 rounded-xl p-4 flex gap-3"
                    >
                      <Sun className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-white leading-relaxed">{insight}</p>
                    </motion.div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}
        </div>

        {/* Vegetation Analysis */}
        {vegetationAnalysis.data && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-8"
          >
            <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 p-6 shadow-2xl">
              <h3 className="text-xl font-bold text-white mb-5 flex items-center gap-3">
                <div className="p-2 rounded-xl bg-green-500/20">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                </div>
                تحلیل پوشش گیاهی
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { label: "وضعیت سلامت", value: vegetationAnalysis.data.results?.health_status, color: "text-green-400" },
                  { label: "امتیاز vigor", value: vegetationAnalysis.data.results?.vigor_score, color: "text-white" },
                  { label: "اطمینان", value: `${(vegetationAnalysis.data.confidence * 100).toFixed(0)}%`, color: "text-purple-400" }
                ].map((stat, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6 + idx * 0.1 }}
                    className="bg-black/30 backdrop-blur-xl border border-white/5 rounded-2xl p-5 text-center hover:bg-black/40 transition-all"
                  >
                    <div className="text-sm text-zinc-400 mb-2">{stat.label}</div>
                    <div className={`text-3xl font-black ${stat.color} tabular-nums`}>
                      {stat.value}
                    </div>
                  </motion.div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: Brain, title: "تحلیل هوشمند", desc: "ترکیب داده‌های خاک، هوا و ماهواره", color: "#8b5cf6" },
            { icon: Zap, title: "توصیه‌های تخصصی", desc: "بر اساس استانداردهای FAO و IPCC", color: "#10b981" },
            { icon: Activity, title: "یادگیری مداوم", desc: "بهبود توصیه‌ها با داده‌های جدید", color: "#3b82f6" }
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + idx * 0.1 }}
              >
                <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 p-5 hover:bg-white/[0.05] hover:border-white/20 transition-all h-full">
                  <div 
                    className="p-3 rounded-xl inline-block mb-3"
                    style={{ backgroundColor: `${item.color}15` }}
                  >
                    <Icon className="w-6 h-6" style={{ color: item.color }} />
                  </div>
                  <h4 className="font-bold text-white mb-2">{item.title}</h4>
                  <p className="text-sm text-zinc-400">{item.desc}</p>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}