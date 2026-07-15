/**
 * ============================================================================
 *  EcoCoin Wallet — balance + transactions (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";

interface Tx { id: string; type: "credit" | "debit"; descKey: string; amount: number; date: string; }
const TXS: readonly Tx[] = [
  { id: "1", type: "credit", descKey: "ecoCoin.txReward", amount: 50, date: "2024-07-10" },
  { id: "2", type: "debit", descKey: "ecoCoin.txPurchase", amount: 30, date: "2024-07-08" },
  { id: "3", type: "credit", descKey: "ecoCoin.txMining", amount: 15, date: "2024-07-05" },
  { id: "4", type: "credit", descKey: "ecoCoin.txChallenge", amount: 100, date: "2024-07-01" },
] as const;

export function Wallet(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.wallet")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.walletSubtitle")}</p>
      </header>

      <div className="mb-6 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 p-6 text-white">
        <p className="text-sm text-emerald-100">{t("ecoCoin.balance")}</p>
        <p className="mt-2 text-4xl font-bold">{formatNumber(1250, language)} ECO</p>
      </div>

      <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-5 py-3">
          <h3 className="text-sm font-semibold text-gray-900">{t("ecoCoin.recentTransactions")}</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-start text-sm">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-5 py-3 font-medium">{t("accounting.tableDescription")}</th>
                <th className="px-5 py-3 font-medium">{t("accounting.tableAmount")}</th>
                <th className="px-5 py-3 font-medium">{t("accounting.tableDate")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {TXS.map((tx) => (
                <tr key={tx.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium text-gray-900">{t(tx.descKey)}</td>
                  <td className={cn("px-5 py-3 font-medium", tx.type === "credit" ? "text-emerald-600" : "text-gray-700")}>
                    {tx.type === "credit" ? "+" : "−"}{formatNumber(tx.amount, language)} ECO
                  </td>
                  <td className="px-5 py-3 text-gray-500" dir="ltr">{tx.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
