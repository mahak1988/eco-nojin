import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Loader2, MapPin } from "lucide-react";
import { farmsApi } from "../lib/farmsApi";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

export default function FarmNewPage() {
  const navigate = useNavigate();
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [region, setRegion] = useState("");
  const [areaHa, setAreaHa] = useState("");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const farm = await farmsApi.create({
        name: name.trim(),
        description: description.trim() || undefined,
        region: region.trim() || undefined,
        area_ha: areaHa ? Number(areaHa) : undefined,
        latitude: lat ? Number(lat) : undefined,
        longitude: lng ? Number(lng) : undefined,
      });
      navigate(`/farms/${farm.id}`, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : tx("farm_create_failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-6 p-5 sm:p-8">
      <Link to="/farms" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500 hover:text-stone-800">
        <ArrowLeft className="h-4 w-4" />
        {tx("farm_all")}
      </Link>

      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50">
          <MapPin className="h-5 w-5 text-emerald-700" />
        </div>
        <div>
          <h1 className="font-display text-2xl text-stone-800">{tx("farm_new_title")}</h1>
          <p className="text-sm text-stone-500">{tx("farm_new_sub")}</p>
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>
        )}
        <label className="block text-sm">
          <span className="font-medium text-stone-600">{tx("farm_name_req")}</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-stone-600">{tx("farm_description")}</span>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
          />
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-sm">
            <span className="font-medium text-stone-600">{tx("farm_region")}</span>
            <input
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-stone-600">{tx("farm_area_ha")}</span>
            <input
              type="number"
              min={0}
              step="0.1"
              value={areaHa}
              onChange={(e) => setAreaHa(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-stone-600">{tx("farm_lat")}</span>
            <input
              type="number"
              step="any"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-stone-600">{tx("farm_lng")}</span>
            <input
              type="number"
              step="any"
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          {loading ? tx("farm_saving") : tx("farm_create")}
        </button>
      </form>
    </div>
  );
}
