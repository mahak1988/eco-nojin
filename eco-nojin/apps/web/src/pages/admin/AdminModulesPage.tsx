import { useAdminOverview } from "../../hooks/useAdmin";

export default function AdminModulesPage() {
  const { data, isLoading } = useAdminOverview();
  const modules = (data?.modules as { modules?: string[] })?.modules ?? [];

  return (
    <div className="space-y-4">
      <h1 className="font-display text-3xl text-stone-800">API modules</h1>
      {isLoading && <p className="text-sm text-stone-500">Loading…</p>}
      <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {modules.map((m) => (
          <li key={m} className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-stone-800">
            {m}
          </li>
        ))}
        {!modules.length && !isLoading && (
          <li className="text-sm text-stone-500">No modules reported (start API).</li>
        )}
      </ul>
    </div>
  );
}
