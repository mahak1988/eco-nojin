"use client";

import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";
import { ecominingService } from "@/lib/api";

export default function EcominingPage() {
  return (
    <ModuleDashboard
      config={MODULE_REGISTRY.ecomining}
      fetchData={async () => {
        const balance = (await ecominingService.getBalance()) as {
          balance?: number;
          eco_coins?: number;
        };
        const mined = (await ecominingService.mine(
          "organic_farming",
          5,
          "iran",
          12,
          500
        )) as { tokens_earned?: number };
        const coins =
          (balance.balance ?? balance.eco_coins ?? 0) + (mined.tokens_earned ?? 0);
        return {
          stats: [
            { title: "EcoCoin", value: coins },
            { title: "ماین امروز", value: 12 },
            { title: "پاداش", value: 340 },
            { title: "رتبه", value: 42 },
          ],
          rows: [{ id: 1, name: "کیف پول", status: `${coins} ECO` }],
          chartData: [{ id: 1, name: "موجودی", amount: coins }],
        };
      }}
    />
  );
}
