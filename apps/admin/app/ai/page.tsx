"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminAiPage() {
  const [msg, setMsg] = useState("");
  const [reply, setReply] = useState("");

  const send = async () => {
    const res = await fetch(`${API}/api/v1/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, locale: "fa", module: "admin" }),
    });
    const data = await res.json();
    setReply(data.reply);
  };

  return (
    <div className="space-y-4 max-w-xl">
      <h1 className="text-2xl font-bold">ایجنت AI</h1>
      <textarea
        className="w-full h-24 p-3 rounded-lg bg-slate-900 border border-slate-700"
        value={msg}
        onChange={(e) => setMsg(e.target.value)}
      />
      <button onClick={send} className="px-4 py-2 rounded-lg bg-sky-600">
        ارسال
      </button>
      {reply && <pre className="text-sm p-4 bg-slate-900 rounded-lg">{reply}</pre>}
    </div>
  );
}
