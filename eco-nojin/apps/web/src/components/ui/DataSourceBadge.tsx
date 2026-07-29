import { Badge } from "./Badge";
import type { DataSource } from "../../types/common";

export function DataSourceBadge({ source }: { source: DataSource }) {
  if (source === "api") return <Badge color="green">API · live</Badge>;
  if (source === "cache") return <Badge color="blue">cache</Badge>;
  return <Badge color="amber">offline · sample</Badge>;
}
