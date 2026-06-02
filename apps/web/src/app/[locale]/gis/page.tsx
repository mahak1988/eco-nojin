"use client";

import dynamic from "next/dynamic";
import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";
import { gisService } from "@/lib/api";
import { useTranslations } from "next-intl";

const GisMap = dynamic(
  () => import("@/components/gis/GisMap").then((m) => m.GisMap),
  { ssr: false, loading: () => <div className="h-[420px] rounded-2xl bg-slate-900 animate-pulse" /> }
);

export default function GisPage() {
  const t = useTranslations();

  return (
    <ModuleDashboard
      config={{ ...MODULE_REGISTRY.gis, title: t("gis.title") }}
      fetchData={async () => {
        const ndvi = await gisService.getLayers();
        return {
          stats: [
            { title: "لایه OSM", value: 1 },
            { title: "لایه ماهواره", value: 1 },
            { title: "NDVI", value: 62 },
            { title: "Zoom", value: 10 },
          ],
          rows: [{ id: 1, name: "Tehran basin", status: "active" }],
          chartData: [{ id: 1, name: "NDVI", amount: 0.62 }],
          raw: ndvi,
        };
      }}
    >
      <GisMap />
    </ModuleDashboard>
  );
}
