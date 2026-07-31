/**
 * Phase 4 — List my claims (filter by user_id).
 * Route: /ecocoin/claims
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Loader2, FileText } from "lucide-react";
import { listClaims, type ClaimOut } from "../lib/ecocoinLedgerApi";

export default function EcoCoinClaimsListPage() {
  const [userId, setUserId] = useState("pilot-user-1");
  const [items, setItems] = useState<ClaimOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await listClaims({ user_id: userId, page: 1, size: 50 });
      setItems(res.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-stone-50 px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <Link to="/ecocoin" className="mb-4 inline-flex items-center gap-2 text-sm text-emerald-700">
          <ArrowLeft className="h-4 w-4" /> EcoCoin
        </Link>
        <h1 className="mb-4 text-2xl font-bold">My claims</h1>
        <div className="mb-4 flex gap-2">
          <input
            className="flex-1 rounded-lg border px-3 py-2 text-sm"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
          <button
            type="button"
            onClick={() => void load()}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white"
          >
            Refresh
          </button>
          <Link
            to="/ecocoin/claims/new"
            className="rounded-lg border border-emerald-600 px-4 py-2 text-sm text-emerald-700"
          >
            New
          </Link>
        </div>
        {loading && <Loader2 className="mx-auto h-6 w-6 animate-spin text-emerald-600" />}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <ul className="space-y-2">
          {items.map((c) => (
            <li
              key={c.claim_uid}
              className="flex items-start gap-3 rounded-xl border bg-white p-4 shadow-sm"
            >
              <FileText className="mt-0.5 h-5 w-5 text-emerald-600" />
              <div className="min-w-0 flex-1">
                <p className="font-medium">{c.title || c.category}</p>
                <p className="font-mono text-xs text-stone-500 truncate">{c.claim_uid}</p>
                <p className="text-xs text-stone-600">
                  {c.status} · {c.level}
                  {c.reward_amount ? ` · reward ${c.reward_amount}` : ""}
                </p>
              </div>
            </li>
          ))}
        </ul>
        {!loading && items.length === 0 && !error && (
          <p className="text-center text-sm text-stone-500">No claims yet.</p>
        )}
      </div>
    </div>
  );
}
