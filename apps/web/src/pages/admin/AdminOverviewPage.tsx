import { useAdminOverview } from "../../hooks/useAdmin";

export default function AdminOverviewPage() {
  const { data, isLoading, isError } = useAdminOverview();

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl text-stone-800">Admin overview</h1>
      <p className="text-stone-600">System status and registered modules.</p>
      {isLoading && <p className="text-sm text-stone-500">Loading…</p>}
      {isError && <p className="text-sm text-amber-700">Partial data (API may be offline).</p>}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-bold text-stone-500">Health</h2>
          <pre className="mt-2 overflow-auto text-xs text-stone-700">
            {JSON.stringify(data?.health ?? {}, null, 2)}
          </pre>
        </div>
        <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-bold text-stone-500">Modules</h2>
          <pre className="mt-2 overflow-auto text-xs text-stone-700">
            {JSON.stringify(data?.modules ?? {}, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
