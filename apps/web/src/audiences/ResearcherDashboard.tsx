/**
 * ============================================================================
 *  ResearcherDashboard — dashboard for researcher audience (i18n-aware)
 * ============================================================================
 */


import { useLanguage } from "@/hooks/useLanguage";

export function ResearcherDashboard(): JSX.Element {
  const { t, dir } = useLanguage();

  // TODO: kpis not used - implement or remove
  
  
  const citations = {
      "kpis": [
        { labelKey: "audiences.researcher.kpiDatasets", value: "۲۸۴", icon: "📊", trend: "دانلود" },
        { labelKey: "audiences.researcher.kpiCitations", value: "۱۲", icon: "📝", trend: "مقاله" },
        { labelKey: "audiences.researcher.kpiDOIs", value: "۸", icon: "🔗", trend: "تولید" },
        { labelKey: "audiences.researcher.kpiDownloads", value: "۱.۵K", icon: "⬇️", trend: "این ماه" },
      ],
      "citations": [
        { title: "Climate change impacts on Iranian watersheds", authors: "Hosseini M. et al.", year: "2024", journal: "J. Environ. Sci.", doi: "10.1234/jes.2024.001" },
        { title: "Soil erosion modeling with RUSLE in semi-arid regions", authors: "Rezaei A. et al.", year: "2023", journal: "Catena", doi: "10.5678/cat.2023.045" },
        { title: "Biodiversity assessment using GEDI LiDAR", authors: "Karimi S. et al.", year: "2024", journal: "Remote Sens.", doi: "10.9012/rs.2024.089" },
      ]
    }["citations"];

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-rose-50 text-3xl">📚</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t("audiences.researcher.title")}</h1>
            <p className="mt-1 text-sm text-gray-600">{t("audiences.researcher.subtitle")}</p>
          </div>
        </div>
      </header>

      <div className="space-y-6">
        
      {/* Quick Charts */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.chartsTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">{t("audiences.' + role + '.chart1Title")}</h3>
            <div className="flex h-32 items-end justify-around">
              {[40, 65, 50, 80, 70, 90, 60].map((h, i) => (
                <div key={i} className="w-6 rounded-t bg-emerald-500" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
          <div className="rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">{t("audiences.' + role + '.chart2Title")}</h3>
            <div className="flex h-32 items-end justify-around">
              {[30, 45, 60, 75, 65, 80, 95].map((h, i) => (
                <div key={i} className="w-6 rounded-t bg-blue-500" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
        </div>
      </section>
      {/* Recent Citations */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.citationsTitle")}</h2>
        <div className="space-y-3">
          {citations.map((cit, i) => (
            <div key={i} className="border-s-2 border-emerald-500 ps-4">
              <p className="text-sm font-medium text-gray-900">{cit.title}</p>
              <p className="text-xs text-gray-500">{cit.authors} • {cit.year} • {cit.journal}</p>
              <code className="mt-1 block text-xs text-emerald-600">{cit.doi}</code>
            </div>
          ))}
        </div>
      </section>
      </div>
    </div>
  );
}
