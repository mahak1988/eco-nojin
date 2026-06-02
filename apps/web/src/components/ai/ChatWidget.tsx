"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { aiService } from "@/lib/api";
import { useTranslations, useLocale } from "next-intl";
import { usePathname } from "next/navigation";

type Msg = { role: "user" | "bot"; text: string };

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [loading, setLoading] = useState(false);
  const t = useTranslations();
  const locale = useLocale();
  const pathname = usePathname();
  const module = pathname.split("/")[1] || "general";

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: userMsg }]);
    setLoading(true);
    try {
      const res = await aiService.chat(userMsg, locale, module);
      setMsgs((m) => [
        ...m,
        { role: "bot", text: res.reply },
      ]);
    } catch {
      setMsgs((m) => [
        ...m,
        { role: "bot", text: locale === "en" ? "API offline" : "API در دسترس نیست" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <motion.button
        type="button"
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 left-6 z-50 h-14 w-14 rounded-full bg-gradient-to-br from-sky-600 to-emerald-600 shadow-lg flex items-center justify-center text-white"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 left-6 z-50 w-[min(100vw-3rem,380px)] h-[480px] rounded-2xl border border-slate-700 bg-slate-950/95 backdrop-blur-xl shadow-2xl flex flex-col overflow-hidden"
          >
            <div className="p-4 border-b border-slate-800 flex items-center gap-2">
              <Bot className="h-5 w-5 text-sky-400" />
              <span className="font-semibold text-sm">Econojin AI</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {msgs.length === 0 && (
                <p className="text-xs text-slate-500 text-center mt-8">
                  {locale === "en"
                    ? "Ask about weather, farmers, EcoCoin, simulations..."
                    : "درباره هواشناسی، کشاورزان، EcoCoin و شبیه‌سازی بپرسید"}
                </p>
              )}
              {msgs.map((m, i) => (
                <div
                  key={i}
                  className={`text-sm p-3 rounded-xl max-w-[90%] ${
                    m.role === "user"
                      ? "bg-sky-600/20 text-sky-100 mr-auto"
                      : "bg-slate-800 text-slate-200 ml-auto"
                  }`}
                >
                  {m.text}
                </div>
              ))}
              {loading && (
                <div className="text-xs text-slate-500 animate-pulse">...</div>
              )}
            </div>
            <div className="p-3 border-t border-slate-800 flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder={t("chat.placeholder")}
                className="border-slate-700 bg-slate-900"
              />
              <Button size="icon" onClick={send} disabled={loading}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
