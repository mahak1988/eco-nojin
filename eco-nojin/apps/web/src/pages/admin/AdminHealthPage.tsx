import { useApiHealth } from "../../hooks/useHealth";

export default function AdminHealthPage() {
  const { data, isFetching, refetch } = useApiHealth();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl text-stone-800">Health</h1>
        <button
          type="button"
          onClick={() => refetch()}
          className="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-bold text-stone-700 hover:bg-stone-50"
        >
          Refresh{isFetching ? "…" : ""}
        </button>
      </div>
      <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
        <p className="text-sm">
          Status:{" "}
          <span className="font-bold text-emerald-700">{data?.status ?? "—"}</span>
        </p>
        <pre className="mt-3 overflow-auto rounded-xl bg-stone-50 p-3 text-xs">{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  );
}
