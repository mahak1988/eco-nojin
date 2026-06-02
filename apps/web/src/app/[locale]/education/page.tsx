"use client";

import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";

export default function EducationPage() {
  return <ModuleDashboard config={MODULE_REGISTRY.education} />;
}
