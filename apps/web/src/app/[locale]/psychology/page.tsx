"use client";

import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";

export default function PsychologyPage() {
  return <ModuleDashboard config={MODULE_REGISTRY.psychology} />;
}
