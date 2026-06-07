"use client";

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAIChat, useSoilAnalysis, useWeatherAnalysis } from '@/hooks/ai/useAI';
import { Brain, Send, Leaf, Cloud } from 'lucide-react';

export function AIDashboard() {
  const [message, setMessage] = useState('');
  const chatMutation = useAIChat();
  const soilAnalysis = useSoilAnalysis({ ph: 6.5, organic_carbon: 2.5, nitrogen: 0.15 });
  const weatherAnalysis = useWeatherAnalysis({ temperature: 28, humidity: 45, rainfall: 0 });

  const handleSend = () => {
    if (message.trim()) {
      chatMutation.mutate(message);
      setMessage('');
    }
  };

  return (
    <div className="space-y-6">
      <Card className="bg-slate-900/50 border-slate-800 p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          دستیار هوشمند کشاورزی
        </h3>
        
        <div className="space-y-4">
          <div className="bg-slate-800/50 rounded-lg p-4 min-h-[100px]">
            {chatMutation.data ? (
              <p className="text-white">{chatMutation.data.response}</p>
            ) : chatMutation.isPending ? (
              <p className="text-slate-400 animate-pulse">در حال تحلیل...</p>
            ) : (
              <p className="text-slate-400">سوال خود را بپرسید...</p>
            )}
          </div>
          
          <div className="flex gap-2">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="مثلاً: چگونه آبیاری را بهینه کنم؟"
              className="bg-slate-800 border-slate-700 text-white"
            />
            <Button onClick={handleSend} className="bg-purple-600 hover:bg-purple-700">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {soilAnalysis.data && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Leaf className="w-5 h-5 text-emerald-400" />
            تحلیل هوشمند خاک
          </h3>
          <div className="space-y-2">
            {soilAnalysis.data.insights?.map((insight: string, idx: number) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-3 text-white">
                {insight}
              </div>
            ))}
          </div>
        </Card>
      )}

      {weatherAnalysis.data && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Cloud className="w-5 h-5 text-blue-400" />
            تحلیل هوشمند هوا
          </h3>
          <div className="space-y-2">
            {weatherAnalysis.data.insights?.map((insight: string, idx: number) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-3 text-white">
                {insight}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
