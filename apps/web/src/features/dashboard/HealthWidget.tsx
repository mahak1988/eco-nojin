import { useApiHealth } from "../../hooks/useHealth";
import { Badge } from "../../components/ui/Badge";

export function HealthWidget() {
  const { data, isFetching } = useApiHealth();
  const ok = data?.status === "healthy" || data?.status === "ok";

  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-stone-700">API health</h3>
        <Badge color={ok ? "green" : "red"}>{data?.status ?? (isFetching ? "…" : "down")}</Badge>
      </div>
      <p className="mt-2 text-xs text-stone-500">
        {data?.version ? `v${data.version}` : "—"}
        {data?.environment ? ` · ${data.environment}` : ""}
      </p>
    </div>
  );
}
