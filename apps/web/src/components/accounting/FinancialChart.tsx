// apps/web/src/components/accounting/FinancialChart.tsx
import { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart, Line, AreaChart, Area,
  BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  Legend,
} from "recharts";
import { useLang } from "../eco/i18n";

type ChartType = "line" | "area" | "bar";

interface Props {
  data: Record<string, string | number>[];
  xKey: string;
  series: { key: string; color: string; label: string; labelFa: string }[];
  type?: ChartType;
  height?: number;
  className?: string;
  showGrid?: boolean;
}

const CHART_COMPONENTS = {
  line: LineChart,
  area: AreaChart,
  bar: BarChart,
};

export default function FinancialChart({
  data,
  xKey,
  series,
  type = "area",
  height = 300,
  className = "",
  showGrid = true,
}: Props) {
  const { lang } = useLang();
  const isRtl = lang === "fa";

  const ChartComponent = CHART_COMPONENTS[type];

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <ChartComponent data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
          <XAxis
            dataKey={xKey}
            fontSize={12}
            tick={{ fill: "#6b7280" }}
            reversed={isRtl}
          />
          <YAxis fontSize={12} tick={{ fill: "#6b7280" }} />
          <Tooltip
            contentStyle={{
              borderRadius: "12px",
              border: "1px solid #e5e7eb",
              backgroundColor: "#fff",
              fontSize: "12px",
            }}
          />
          <Legend
            formatter={(value: string) => {
              const s = series.find((s) => s.label === value || s.key === value);
              return (lang === "fa" && s?.labelFa) ? s.labelFa : (s?.label ?? value);
            }}
          />
          {series.map((s) => {
            if (type === "bar") {
              return (
                <Bar
                  key={s.key}
                  dataKey={s.key}
                  fill={s.color}
                  radius={[6, 6, 0, 0]}
                  name={s.label}
                />
              );
            }
            if (type === "area") {
              return (
                <Area
                  key={s.key}
                  type="monotone"
                  dataKey={s.key}
                  stroke={s.color}
                  fill={s.color}
                  fillOpacity={0.1}
                  strokeWidth={2}
                  name={s.label}
                />
              );
            }
            return (
              <Line
                key={s.key}
                type="monotone"
                dataKey={s.key}
                stroke={s.color}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                name={s.label}
              />
            );
          })}
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}
