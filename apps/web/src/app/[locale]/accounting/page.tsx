"use client";

import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";
import { accountingService } from "@/lib/api";

export default function AccountingPage() {
  return (
    <ModuleDashboard
      config={MODULE_REGISTRY.accounting}
      fetchData={async () => {
        const [summary, tx] = await Promise.all([
          accountingService.summary(),
          accountingService.transactions(15),
        ]);
        return {
          stats: [
            { title: "درآمد (ریال)", value: Math.round(summary.total_income / 1_000_000) },
            { title: "هزینه (میلیون)", value: Math.round(summary.total_expense / 1_000_000) },
            { title: "سود خالص (میلیون)", value: Math.round(summary.net_profit / 1_000_000) },
            { title: "تراکنش‌ها", value: tx.transactions.length },
          ],
          rows: tx.transactions,
          chartData: tx.transactions.map((t) => ({
            id: t.id,
            name: t.type,
            amount: t.amount,
          })),
        };
      }}
    />
  );
}
