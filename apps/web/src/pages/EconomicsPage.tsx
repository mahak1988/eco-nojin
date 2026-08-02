import { Link } from "react-router-dom";

export default function EconomicsPage() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Economics</h1>
      <p className="text-stone-600">NPV / IRR / break-even entry (API under /api/v1/economics).</p>
      <div className="grid gap-4 sm:grid-cols-3">
        {["npv-lab", "irr-lab", "break-even"].map((s) => (
          <Link
            key={s}
            to={`/hub/${s}`}
            className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm hover:border-emerald-300"
          >
            <p className="font-semibold capitalize">{s.replace(/-/g, " ")}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
