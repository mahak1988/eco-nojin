/**
 * ============================================================================
 *  Privacy.tsx — Privacy Policy (GDPR-Compliant & Human Rights-Based)
 * ============================================================================
 */
import { LegalLayout, LegalSection, LegalCallout } from "@/components/Legal/LegalLayout";
import { useLanguage } from "@/hooks/useLanguage";

export function Privacy(): JSX.Element {
  const { t } = useLanguage();
  const toc = [
    { id: "introduction", title: t("privacy.toc.introduction") }, { id: "principles", title: t("privacy.toc.principles") },
    { id: "data-collected", title: t("privacy.toc.dataCollected") }, { id: "legal-basis", title: t("privacy.toc.legalBasis") },
    { id: "your-rights", title: t("privacy.toc.yourRights") }, { id: "security", title: t("privacy.toc.security") },
    { id: "sharing", title: t("privacy.toc.sharing") }, { id: "retention", title: t("privacy.toc.retention") },
    { id: "cookies", title: t("privacy.toc.cookies") }, { id: "children", title: t("privacy.toc.children") },
    { id: "international", title: t("privacy.toc.international") }, { id: "changes", title: t("privacy.toc.changes") },
    { id: "contact", title: t("privacy.toc.contact") },
  ];

  return (
    <LegalLayout title={t("privacy.title")} subtitle={t("privacy.subtitle")} lastUpdated={t("privacy.lastUpdated")} toc={toc}>
      <LegalSection id="introduction" icon="🔐" title={t("privacy.sections.introduction.title")}>
        <p>{t("privacy.sections.introduction.p1")}</p>
        <LegalCallout type="principle" title={t("privacy.sections.introduction.calloutTitle")}>{t("privacy.sections.introduction.calloutText")}</LegalCallout>
      </LegalSection>
      <LegalSection id="principles" icon="⚖️" title={t("privacy.sections.principles.title")}>
        <p>{t("privacy.sections.principles.intro")}</p>
        <ul className="list-none space-y-3 ps-0">
          {[{ icon: "🎯", title: t("privacy.sections.principles.minimization"), desc: t("privacy.sections.principles.minimizationDesc") },
            { icon: "🔍", title: t("privacy.sections.principles.transparency"), desc: t("privacy.sections.principles.transparencyDesc") },
            { icon: "🛡️", title: t("privacy.sections.principles.integrity"), desc: t("privacy.sections.principles.integrityDesc") },
            { icon: "👤", title: t("privacy.sections.principles.accountability"), desc: t("privacy.sections.principles.accountabilityDesc") }
          ].map((p, i) => <li key={i} className="flex gap-3"><span className="text-xl">{p.icon}</span><div><strong>{p.title}</strong><p className="mt-1 text-sm">{p.desc}</p></div></li>)}
        </ul>
      </LegalSection>
      <LegalSection id="data-collected" icon="📊" title={t("privacy.sections.dataCollected.title")}>
        <p>{t("privacy.sections.dataCollected.intro")}</p>
        <h3 className="mt-6 text-lg font-bold text-gray-900">{t("privacy.sections.dataCollected.personalTitle")}</h3>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.dataCollected.personal1")}</li><li>{t("privacy.sections.dataCollected.personal2")}</li><li>{t("privacy.sections.dataCollected.personal3")}</li><li>{t("privacy.sections.dataCollected.personal4")}</li></ul>
        <h3 className="mt-6 text-lg font-bold text-gray-900">{t("privacy.sections.dataCollected.technicalTitle")}</h3>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.dataCollected.technical1")}</li><li>{t("privacy.sections.dataCollected.technical2")}</li><li>{t("privacy.sections.dataCollected.technical3")}</li></ul>
        <h3 className="mt-6 text-lg font-bold text-gray-900">{t("privacy.sections.dataCollected.agriculturalTitle")}</h3>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.dataCollected.agricultural1")}</li><li>{t("privacy.sections.dataCollected.agricultural2")}</li><li>{t("privacy.sections.dataCollected.agricultural3")}</li></ul>
      </LegalSection>
      <LegalSection id="legal-basis" icon="📜" title={t("privacy.sections.legalBasis.title")}>
        <p>{t("privacy.sections.legalBasis.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li><strong>{t("privacy.sections.legalBasis.consent")}</strong>: {t("privacy.sections.legalBasis.consentDesc")}</li>
          <li><strong>{t("privacy.sections.legalBasis.contract")}</strong>: {t("privacy.sections.legalBasis.contractDesc")}</li>
          <li><strong>{t("privacy.sections.legalBasis.legitimate")}</strong>: {t("privacy.sections.legalBasis.legitimateDesc")}</li>
          <li><strong>{t("privacy.sections.legalBasis.legal")}</strong>: {t("privacy.sections.legalBasis.legalDesc")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="your-rights" icon="🛡️" title={t("privacy.sections.yourRights.title")}>
        <p>{t("privacy.sections.yourRights.intro")}</p>
        <LegalCallout type="success" title={t("privacy.sections.yourRights.calloutTitle")}>{t("privacy.sections.yourRights.calloutText")}</LegalCallout>
        <div className="grid gap-4 sm:grid-cols-2">
          {[{ icon: "👁️", title: t("privacy.sections.yourRights.right1Title"), desc: t("privacy.sections.yourRights.right1Desc") },
            { icon: "✏️", title: t("privacy.sections.yourRights.right2Title"), desc: t("privacy.sections.yourRights.right2Desc") },
            { icon: "🗑️", title: t("privacy.sections.yourRights.right3Title"), desc: t("privacy.sections.yourRights.right3Desc") },
            { icon: "📦", title: t("privacy.sections.yourRights.right4Title"), desc: t("privacy.sections.yourRights.right4Desc") },
            { icon: "🚫", title: t("privacy.sections.yourRights.right5Title"), desc: t("privacy.sections.yourRights.right5Desc") },
            { icon: "⚙️", title: t("privacy.sections.yourRights.right6Title"), desc: t("privacy.sections.yourRights.right6Desc") },
            { icon: "📢", title: t("privacy.sections.yourRights.right7Title"), desc: t("privacy.sections.yourRights.right7Desc") },
            { icon: "🤖", title: t("privacy.sections.yourRights.right8Title"), desc: t("privacy.sections.yourRights.right8Desc") }
          ].map((r, i) => (
            <div key={i} className="rounded-lg border border-gray-200 bg-white p-4">
              <div className="mb-2 flex items-center gap-2"><span className="text-2xl">{r.icon}</span><strong className="text-gray-900">{r.title}</strong></div>
              <p className="text-sm text-gray-600">{r.desc}</p>
            </div>
          ))}
        </div>
      </LegalSection>
      <LegalSection id="security" icon="🔒" title={t("privacy.sections.security.title")}>
        <p>{t("privacy.sections.security.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li><strong>{t("privacy.sections.security.encryption")}</strong>: {t("privacy.sections.security.encryptionDesc")}</li>
          <li><strong>{t("privacy.sections.security.access")}</strong>: {t("privacy.sections.security.accessDesc")}</li>
          <li><strong>{t("privacy.sections.security.audits")}</strong>: {t("privacy.sections.security.auditsDesc")}</li>
          <li><strong>{t("privacy.sections.security.breach")}</strong>: {t("privacy.sections.security.breachDesc")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="sharing" icon="🤝" title={t("privacy.sections.sharing.title")}>
        <p>{t("privacy.sections.sharing.intro")}</p>
        <LegalCallout type="warning" title={t("privacy.sections.sharing.calloutTitle")}>{t("privacy.sections.sharing.calloutText")}</LegalCallout>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.sharing.scenario1")}</li><li>{t("privacy.sections.sharing.scenario2")}</li><li>{t("privacy.sections.sharing.scenario3")}</li></ul>
      </LegalSection>
      <LegalSection id="retention" icon="⏱️" title={t("privacy.sections.retention.title")}>
        <p>{t("privacy.sections.retention.intro")}</p>
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="w-full text-sm">
            <thead className="bg-gray-50"><tr><th className="px-4 py-3 text-start font-semibold text-gray-900">{t("privacy.sections.retention.table.type")}</th><th className="px-4 py-3 text-start font-semibold text-gray-900">{t("privacy.sections.retention.table.period")}</th></tr></thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              <tr><td className="px-4 py-3">{t("privacy.sections.retention.table.account")}</td><td className="px-4 py-3">{t("privacy.sections.retention.table.accountPeriod")}</td></tr>
              <tr><td className="px-4 py-3">{t("privacy.sections.retention.table.logs")}</td><td className="px-4 py-3">{t("privacy.sections.retention.table.logsPeriod")}</td></tr>
              <tr><td className="px-4 py-3">{t("privacy.sections.retention.table.backups")}</td><td className="px-4 py-3">{t("privacy.sections.retention.table.backupsPeriod")}</td></tr>
            </tbody>
          </table>
        </div>
      </LegalSection>
      <LegalSection id="cookies" icon="🍪" title={t("privacy.sections.cookies.title")}>
        <p>{t("privacy.sections.cookies.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li><strong>{t("privacy.sections.cookies.essential")}</strong>: {t("privacy.sections.cookies.essentialDesc")}</li>
          <li><strong>{t("privacy.sections.cookies.analytics")}</strong>: {t("privacy.sections.cookies.analyticsDesc")}</li>
          <li><strong>{t("privacy.sections.cookies.preferences")}</strong>: {t("privacy.sections.cookies.preferencesDesc")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="children" icon="👶" title={t("privacy.sections.children.title")}>
        <p>{t("privacy.sections.children.intro")}</p>
      </LegalSection>
      <LegalSection id="international" icon="🌍" title={t("privacy.sections.international.title")}>
        <p>{t("privacy.sections.international.intro")}</p>
      </LegalSection>
      <LegalSection id="changes" icon="📝" title={t("privacy.sections.changes.title")}>
        <p>{t("privacy.sections.changes.intro")}</p>
      </LegalSection>
      <LegalSection id="contact" icon="📧" title={t("privacy.sections.contact.title")}>
        <p>{t("privacy.sections.contact.intro")}</p>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="font-semibold">{t("privacy.sections.contact.dpoLabel")}</p>
          <a href="mailto:privacy@econojin.com" className="text-emerald-700 hover:underline">privacy@econojin.com</a>
          <p className="mt-3 font-semibold">{t("privacy.sections.contact.responseLabel")}</p>
          <p className="text-sm">{t("privacy.sections.contact.responseTime")}</p>
        </div>
      </LegalSection>
    </LegalLayout>
  );
}
