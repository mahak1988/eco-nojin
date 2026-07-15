/**
 * ============================================================================
 *  Terms.tsx — Terms of Service (Human-Centered & Eco-Friendly)
 * ============================================================================
 */
import { LegalLayout, LegalSection, LegalCallout } from "@/components/Legal/LegalLayout";
import { useLanguage } from "@/hooks/useLanguage";

export function Terms(): JSX.Element {
  const { t } = useLanguage();
  const toc = [
    { id: "preamble", title: t("terms.toc.preamble") }, { id: "values", title: t("terms.toc.values") },
    { id: "acceptance", title: t("terms.toc.acceptance") }, { id: "user-rights", title: t("terms.toc.userRights") },
    { id: "user-obligations", title: t("terms.toc.userObligations") }, { id: "platform-commitments", title: t("terms.toc.platformCommitments") },
    { id: "environmental", title: t("terms.toc.environmental") }, { id: "intellectual-property", title: t("terms.toc.intellectualProperty") },
    { id: "liability", title: t("terms.toc.liability") }, { id: "termination", title: t("terms.toc.termination") },
    { id: "dispute-resolution", title: t("terms.toc.disputeResolution") }, { id: "governing-law", title: t("terms.toc.governingLaw") },
    { id: "amendments", title: t("terms.toc.amendments") }, { id: "contact", title: t("terms.toc.contact") },
  ];

  return (
    <LegalLayout title={t("terms.title")} subtitle={t("terms.subtitle")} lastUpdated={t("terms.lastUpdated")} toc={toc}>
      <LegalSection id="preamble" icon="📜" title={t("terms.sections.preamble.title")}>
        <p>{t("terms.sections.preamble.p1")}</p><p>{t("terms.sections.preamble.p2")}</p>
        <LegalCallout type="principle" title={t("terms.sections.preamble.calloutTitle")}>{t("terms.sections.preamble.calloutText")}</LegalCallout>
      </LegalSection>
      <LegalSection id="values" icon="🌍" title={t("terms.sections.values.title")}>
        <p>{t("terms.sections.values.intro")}</p>
        <ul className="list-none space-y-3 ps-0">
          {[{ icon: "🤝", title: t("terms.sections.values.humanDignity"), desc: t("terms.sections.values.humanDignityDesc") },
            { icon: "🌱", title: t("terms.sections.values.ecoStewardship"), desc: t("terms.sections.values.ecoStewardshipDesc") },
            { icon: "⚖️", title: t("terms.sections.values.transparency"), desc: t("terms.sections.values.transparencyDesc") },
            { icon: "🌐", title: t("terms.sections.values.inclusivity"), desc: t("terms.sections.values.inclusivityDesc") }
          ].map((v, i) => <li key={i} className="flex gap-3"><span className="text-xl">{v.icon}</span><div><strong>{v.title}</strong><p className="mt-1 text-sm">{v.desc}</p></div></li>)}
        </ul>
      </LegalSection>
      <LegalSection id="acceptance" icon="✅" title={t("terms.sections.acceptance.title")}>
        <p>{t("terms.sections.acceptance.p1")}</p><p>{t("terms.sections.acceptance.p2")}</p>
      </LegalSection>
      <LegalSection id="user-rights" icon="🛡️" title={t("terms.sections.userRights.title")}>
        <p>{t("terms.sections.userRights.intro")}</p>
        <ol className="list-decimal space-y-2 ps-6">
          <li>{t("terms.sections.userRights.right1")}</li><li>{t("terms.sections.userRights.right2")}</li>
          <li>{t("terms.sections.userRights.right3")}</li><li>{t("terms.sections.userRights.right4")}</li>
          <li>{t("terms.sections.userRights.right5")}</li><li>{t("terms.sections.userRights.right6")}</li>
        </ol>
        <LegalCallout type="info" title={t("terms.sections.userRights.calloutTitle")}>{t("terms.sections.userRights.calloutText")}</LegalCallout>
      </LegalSection>
      <LegalSection id="user-obligations" icon="📋" title={t("terms.sections.userObligations.title")}>
        <p>{t("terms.sections.userObligations.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li>{t("terms.sections.userObligations.obligation1")}</li><li>{t("terms.sections.userObligations.obligation2")}</li>
          <li>{t("terms.sections.userObligations.obligation3")}</li><li>{t("terms.sections.userObligations.obligation4")}</li>
          <li>{t("terms.sections.userObligations.obligation5")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="platform-commitments" icon="🤝" title={t("terms.sections.platformCommitments.title")}>
        <p>{t("terms.sections.platformCommitments.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li>{t("terms.sections.platformCommitments.commitment1")}</li><li>{t("terms.sections.platformCommitments.commitment2")}</li>
          <li>{t("terms.sections.platformCommitments.commitment3")}</li><li>{t("terms.sections.platformCommitments.commitment4")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="environmental" icon="🌿" title={t("terms.sections.environmental.title")}>
        <p>{t("terms.sections.environmental.intro")}</p>
        <LegalCallout type="success" title={t("terms.sections.environmental.calloutTitle")}>{t("terms.sections.environmental.calloutText")}</LegalCallout>
        <ul className="list-disc space-y-2 ps-6">
          <li>{t("terms.sections.environmental.commitment1")}</li><li>{t("terms.sections.environmental.commitment2")}</li>
          <li>{t("terms.sections.environmental.commitment3")}</li><li>{t("terms.sections.environmental.commitment4")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="intellectual-property" icon="©️" title={t("terms.sections.intellectualProperty.title")}>
        <p>{t("terms.sections.intellectualProperty.p1")}</p><p>{t("terms.sections.intellectualProperty.p2")}</p>
      </LegalSection>
      <LegalSection id="liability" icon="⚖️" title={t("terms.sections.liability.title")}>
        <p>{t("terms.sections.liability.p1")}</p><p>{t("terms.sections.liability.p2")}</p>
      </LegalSection>
      <LegalSection id="termination" icon="🔒" title={t("terms.sections.termination.title")}>
        <p>{t("terms.sections.termination.p1")}</p><p>{t("terms.sections.termination.p2")}</p>
      </LegalSection>
      <LegalSection id="dispute-resolution" icon="🕊️" title={t("terms.sections.disputeResolution.title")}>
        <p>{t("terms.sections.disputeResolution.p1")}</p>
        <ol className="list-decimal space-y-2 ps-6">
          <li>{t("terms.sections.disputeResolution.step1")}</li><li>{t("terms.sections.disputeResolution.step2")}</li><li>{t("terms.sections.disputeResolution.step3")}</li>
        </ol>
      </LegalSection>
      <LegalSection id="governing-law" icon="🏛️" title={t("terms.sections.governingLaw.title")}>
        <p>{t("terms.sections.governingLaw.p1")}</p>
      </LegalSection>
      <LegalSection id="amendments" icon="📝" title={t("terms.sections.amendments.title")}>
        <p>{t("terms.sections.amendments.p1")}</p>
      </LegalSection>
      <LegalSection id="contact" icon="📧" title={t("terms.sections.contact.title")}>
        <p>{t("terms.sections.contact.p1")}</p>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="font-semibold">{t("terms.sections.contact.emailLabel")}</p>
          <a href="mailto:legal@econojin.com" className="text-emerald-700 hover:underline">legal@econojin.com</a>
          <p className="mt-3 font-semibold">{t("terms.sections.contact.addressLabel")}</p>
          <p className="text-sm">{t("terms.sections.contact.address")}</p>
        </div>
      </LegalSection>
    </LegalLayout>
  );
}
