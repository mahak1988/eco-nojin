"use client";

import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAIChat, useSoilAnalysis, useWeatherAnalysis, useVegetationAnalysis } from '@/hooks/ai/useAI';
import { 
  Brain, Send, Leaf, Cloud, Sun, MessageCircle,
  TrendingUp, Lightbulb, Sparkles
} from 'lucide-react';

export default function AIPage() {
  const { t } = useTranslation();
  const [message, setMessage] = useState('');
  const chatMutation = useAIChat();
  const soilAnalysis = useSoilAnalysis({ ph: 6.5, organic_carbon: 2.5, nitrogen: 0.15 });
  const weatherAnalysis = useWeatherAnalysis({ temperature: 28, humidity: 45, rainfall: 0 });
  const vegetationAnalysis = useVegetationAnalysis(0.65, 0.58);

  const handleSend = () => {
    if (message.trim()) {
      chatMutation.mutate(message);
      setMessage('');
    }
  };

  const quickQuestions = [
    'چگونه آبیاری را بهینه کنم؟',
    'بهترین زمان کوددهی کی است؟',
    'چگونه از آفات جلوگیری کنم؟',
    'چقدر کربن جذب شده؟'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Brain className="w-10 h-10 text-purple-400" />
            دستیار هوشمند کشاورزی
          </h1>
          <p className="text-slate-400">{t('ai.subtitle')}</p>
        </div>

        {/* Chat Interface */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-purple-400" />
            چت با دستیار هوشمند
          </h3>
          
          <div className="bg-slate-800/50 rounded-lg p-4 min-h-[150px] mb-4">
            {chatMutation.data ? (
              <div className="space-y-3">
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm text-purple-400 mb-1">دستیار AI</div>
                    <p className="text-white">{chatMutation.data.response}</p>
                  </div>
                </div>
              </div>
            ) : chatMutation.isPending ? (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Brain className="w-4 h-4 text-white animate-pulse" />
                </div>
                <p className="text-slate-400 animate-pulse">در حال تحلیل...</p>
              </div>
            ) : (
              <div className="text-slate-400 text-center py-8">
                <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>{t('ai.ask_question')}</p>
              </div>
            )}
          </div>
          
          <div className="flex gap-2 mb-4">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="مثلاً: چگونه آبیاری را بهینه کنم؟"
              className="bg-slate-800 border-slate-700 text-white"
            />
            <Button 
              onClick={handleSend} 
              className="bg-purple-600 hover:bg-purple-700"
              disabled={chatMutation.isPending}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((q, idx) => (
              <Button
                key={idx}
                size="sm"
                variant="outline"
                onClick={() => {
                  setMessage(q);
                }}
                className="text-xs"
              >
                {q}
              </Button>
            ))}
          </div>
        </Card>

        {/* AI Analyses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Soil Analysis */}
          {soilAnalysis.data && (
            <Card className="bg-slate-900/50 border-slate-800 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Leaf className="w-5 h-5 text-emerald-400" />
                تحلیل هوشمند خاک
              </h3>
              <div className="space-y-3">
                {soilAnalysis.data.insights?.map((insight: string, idx: number) => (
                  <div key={idx} className="bg-slate-800/50 rounded-lg p-3 flex gap-3">
                    <Lightbulb className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-white">{insight}</p>
                  </div>
                ))}
              </div>
              {soilAnalysis.data.recommendations?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="text-sm font-medium text-emerald-400 mb-2">توصیه‌ها:</div>
                  {soilAnalysis.data.recommendations.slice(0, 2).map((rec: any, idx: number) => (
                    <div key={idx} className="text-sm text-slate-300 mb-1">
                      • {rec.title}: {rec.description}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}

          {/* Weather Analysis */}
          {weatherAnalysis.data && (
            <Card className="bg-slate-900/50 border-slate-800 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Cloud className="w-5 h-5 text-blue-400" />
                تحلیل هوشمند هوا
              </h3>
              <div className="space-y-3">
                {weatherAnalysis.data.insights?.map((insight: string, idx: number) => (
                  <div key={idx} className="bg-slate-800/50 rounded-lg p-3 flex gap-3">
                    <Sun className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-white">{insight}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Vegetation Analysis */}
        {vegetationAnalysis.data && (
          <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              تحلیل پوشش گیاهی
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">وضعیت سلامت</div>
                <div className="text-2xl font-bold text-green-400">
                  {vegetationAnalysis.data.results?.health_status}
                </div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">امتیاز vigor</div>
                <div className="text-2xl font-bold text-white">
                  {vegetationAnalysis.data.results?.vigor_score}
                </div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">اطمینان</div>
                <div className="text-2xl font-bold text-purple-400">
                  {(vegetationAnalysis.data.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">تحلیل هوشمند</h4>
            <p className="text-sm text-slate-400">ترکیب داده‌های خاک، هوا و ماهواره</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">توصیه‌های تخصصی</h4>
            <p className="text-sm text-slate-400">بر اساس استانداردهای FAO و IPCC</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">یادگیری مداوم</h4>
            <p className="text-sm text-slate-400">بهبود توصیه‌ها با داده‌های جدید</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
