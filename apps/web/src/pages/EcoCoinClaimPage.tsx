/**
 * Phase 4 — Submit impact claim (geo + evidence note).
 * Route: /ecocoin/claims/new
 * Educational pilot only — no speculative rewards promised.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, MapPin, Loader2, Leaf } from "lucide-react";
import {
  createClaim,
  type AssuranceLevel,
  type ClaimCreateBody,
} from "../lib/ecocoinLedgerApi";

const CATEGORIES = [
  { value: "TREE_PLANT", label: "Tree planting / reforestation" },
  { value: "SOIL_RESTO", label: "Soil restoration" },
  { value: "WATER_CONS", label: "Water conservation" },
  { value: "BIODIV", label: "Biodiversity action" },
  { value: "WASTE_RED", label: "Waste reduction" },
  { value: "EDUCATE", label: "Education / awareness (L1)" },
  { value: "STEWARD", label: "Ongoing stewardship" },
] as const;

const LEVELS: { value: AssuranceLevel; label: string; hint: string }[] = [
  { value: "L1", label: "L1 — Education / self-report", hint: "Quizzes, workshops, awareness" },
  { value: "L2", label: "L2 — Peer-verified action", hint: "Photo + peer votes" },
  { value: "L3", label: "L3 — Field / expert package", hint: "Structured evidence package" },
  { value: "L4", label: "L4 — Institutional / sensor", hint: "Third-party or IoT-backed" },
];

export default function EcoCoinClaimPage() {
  const navigate = useNavigate();
  const [userId, setUserId] = useState("pilot-user-1");
  const [category, setCategory] = useState<string>("EDUCATE");
  const [level, setLevel] = useState<AssuranceLevel>("L1");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [evidenceNote, setEvidenceNote] = useState("");
  const [geoLat, setGeoLat] = useState<number | "">("");
  const [geoLng, setGeoLng] = useState<number | "">("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [okUid, setOkUid] = useState<string | null>(null);

  function captureGeo() {
    if (!navigator.geolocation) {
      setError("Geolocation not available in this browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGeoLat(Number(pos.coords.latitude.toFixed(6)));
        setGeoLng(Number(pos.coords.longitude.toFixed(6)));
        setError(null);
      },
      (err) => setError(`Geo: ${err.message}`),
      { enableHighAccuracy: true, timeout: 15000 }
    );
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setOkUid(null);
    try {
      const body: ClaimCreateBody = {
        user_id: userId.trim(),
        category,
        level,
        title: title.trim() || undefined,
        description: description.trim() || undefined,
        submit: true,
        metadata: evidenceNote.trim()
          ? { evidence_note: evidenceNote.trim() }
          : undefined,
      };
      if (geoLat !== "" && geoLng !== "") {
        body.geo_lat = Number(geoLat);
        body.geo_lng = Number(geoLng);
      }
      const claim = await createClaim(body);
      setOkUid(claim.claim_uid);
      setTimeout(() => navigate("/ecocoin/claims"), 1200);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900">
      <div className="mx-auto max-w-xl px-4 py-8">
        <Link
          to="/ecocoin"
          className="mb-6 inline-flex items-center gap-2 text-sm text-emerald-700 hover:underline"
        >
          <ArrowLeft className="h-4 w-4" /> Back to EcoCoin
        </Link>

        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-xl bg-emerald-100 p-3">
            <Leaf className="h-6 w-6 text-emerald-700" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Submit impact claim</h1>
            <p className="text-sm text-stone-600">
              Educational pilot · impact-only mint · no energy mining
            </p>
          </div>
        </div>

        <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
          Rewards are issued only after verification (L1–L4). This is not a
          carbon registry and does not promise financial returns.
        </div>

        <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border bg-white p-5 shadow-sm">
          <label className="block text-sm">
            <span className="font-medium">User ID (pilot)</span>
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              required
            />
          </label>

          <label className="block text-sm">
            <span className="font-medium">Category</span>
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            <span className="font-medium">Assurance level</span>
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={level}
              onChange={(e) => setLevel(e.target.value as AssuranceLevel)}
            >
              {LEVELS.map((l) => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-stone-500">
              {LEVELS.find((l) => l.value === level)?.hint}
            </p>
          </label>

          <label className="block text-sm">
            <span className="font-medium">Title (optional)</span>
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={256}
              placeholder="e.g. Completed soil health module"
            />
          </label>

          <label className="block text-sm">
            <span className="font-medium">Description</span>
            <textarea
              className="mt-1 w-full rounded-lg border px-3 py-2"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What did you do? Where / when?"
            />
          </label>

          <label className="block text-sm">
            <span className="font-medium">Evidence note (photo ref / hash later)</span>
            <textarea
              className="mt-1 w-full rounded-lg border px-3 py-2"
              rows={2}
              value={evidenceNote}
              onChange={(e) => setEvidenceNote(e.target.value)}
              placeholder="Describe photo or attach hash in next release"
            />
          </label>

          <div className="rounded-lg border border-dashed border-stone-300 p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-medium">Location (optional)</span>
              <button
                type="button"
                onClick={captureGeo}
                className="inline-flex items-center gap-1 rounded-md bg-stone-100 px-2 py-1 text-xs text-stone-700 hover:bg-stone-200"
              >
                <MapPin className="h-3 w-3" /> Use my location
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                step="any"
                className="rounded-lg border px-3 py-2 text-sm"
                placeholder="Latitude"
                value={geoLat}
                onChange={(e) =>
                  setGeoLat(e.target.value === "" ? "" : Number(e.target.value))
                }
              />
              <input
                type="number"
                step="any"
                className="rounded-lg border px-3 py-2 text-sm"
                placeholder="Longitude"
                value={geoLng}
                onChange={(e) =>
                  setGeoLng(e.target.value === "" ? "" : Number(e.target.value))
                }
              />
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
              {error}
            </div>
          )}
          {okUid && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900">
              Submitted · claim_uid: <code className="font-mono">{okUid}</code>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Submitting…
              </>
            ) : (
              "Submit claim"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
