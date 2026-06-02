"use client";

import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";

export default function LibraryPage() {
  return <ModuleDashboard config={MODULE_REGISTRY.library} />;
}
