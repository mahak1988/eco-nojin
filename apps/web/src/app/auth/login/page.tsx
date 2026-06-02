"use client";

import { useState } from "react";

const API_BASE = "http://localhost:8000";

export default function LoginPage() {
  const [fid, setFid] = useState("F001");
  const [phone, setPhone] = useState("+989123456789");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fid, phone }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || `Login failed (${res.status})`);

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("farmer_id", data.farmer_id);

      window.location.href = "/auth/profile";
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Login failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-6 max-w-xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Auth Login</h1>

      <div className="space-y-2">
        <label htmlFor="fid" className="block text-sm text-gray-600">
          Farmer ID
        </label>
        <input
          id="fid"
          title="Farmer ID"
          placeholder="F001"
          className="w-full border rounded px-3 py-2"
          value={fid}
          onChange={(e: any) => setFid(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="phone" className="block text-sm text-gray-600">
          Phone
        </label>
        <input
          id="phone"
          title="Phone"
          placeholder="+989123456789"
          className="w-full border rounded px-3 py-2"
          value={phone}
          onChange={(e: any) => setPhone(e.target.value)}
        />
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          ❌ {error}
        </div>
      )}

      <button
        onClick={handleLogin}
        disabled={loading}
        className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50"
      >
        {loading ? "Logging in..." : "Login"}
      </button>
    </main>
  );
}
