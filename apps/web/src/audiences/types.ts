/**
 * ============================================================================
 *  Audience Types — 5 user roles with dedicated dashboards
 * ============================================================================
 */

export type AudienceRole = "farmer" | "student" | "expert" | "manager" | "researcher";

export interface AudienceMeta {
  role: AudienceRole;
  nameKey: string;
  descriptionKey: string;
  icon: string;
  dashboardPath: string;
  primaryColor: string;
}

export const AUDIENCES: readonly AudienceMeta[] = [
  {
    role: "farmer",
    nameKey: "audiences.farmer.name",
    descriptionKey: "audiences.farmer.description",
    icon: "🌾",
    dashboardPath: "/farmer",
    primaryColor: "emerald",
  },
  {
    role: "student",
    nameKey: "audiences.student.name",
    descriptionKey: "audiences.student.description",
    icon: "🎓",
    dashboardPath: "/student",
    primaryColor: "blue",
  },
  {
    role: "expert",
    nameKey: "audiences.expert.name",
    descriptionKey: "audiences.expert.description",
    icon: "🔬",
    dashboardPath: "/expert",
    primaryColor: "purple",
  },
  {
    role: "manager",
    nameKey: "audiences.manager.name",
    descriptionKey: "audiences.manager.description",
    icon: "📊",
    dashboardPath: "/manager",
    primaryColor: "amber",
  },
  {
    role: "researcher",
    nameKey: "audiences.researcher.name",
    descriptionKey: "audiences.researcher.description",
    icon: "📚",
    dashboardPath: "/researcher",
    primaryColor: "rose",
  },
] as const;

export function getAudienceByRole(role: AudienceRole): AudienceMeta | undefined {
  return AUDIENCES.find((a) => a.role === role);
}
