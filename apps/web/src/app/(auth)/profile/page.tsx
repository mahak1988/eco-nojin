"use client";

import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      setError("No token found. Please login.");
      return;
    }

    const run = async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/profile`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data?.detail || `Error (${res.status})`);
        setProfile(data);
      } catch (e: any) {
        setError(e?.message || "Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, []);

  return (
    <main className="p-6 max-w-xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Farmer Profile</h1>

      {loading && <div className="text-sm text-gray-500">Loading...</div>}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          ❌ {error}
          <div className="mt-2">
            <a className="text-blue-600 underline" href="/auth/login">
              Go to login
            </a>
          </div>
        </div>
      )}

      {profile && (
        <div className="p-4 border rounded space-y-2 bg-white">
          <div>
            <div className="text-sm text-gray-500">Fid</div>
            <div className="font-semibold">{profile.fid}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Name</div>
            <div className="font-semibold">{profile.name}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Phone</div>
            <div className="font-semibold">{profile.phone}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Registered at</div>
            <div className="text-sm">{profile.registered_at}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Wallet</div>
            <div className="text-sm">{profile.wallet_address || "—"}</div>
          </div>
          <div className="pt-2">
            <a className="text-green-700 underline" href="/farmer/simulate">
              Go to simulation →
            </a>
          </div>
        </div>
      )}
    </main>
  );
}