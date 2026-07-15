/**
 *  droughtMitigationScenario — droughtMitigation scenario preset
 */

import type { Scenario } from "../types";

export const droughtMitigationScenario: Scenario = {
  id: "droughtMitigation",
  nameKey: "scenarios.droughtMitigation.name",
  descriptionKey: "scenarios.droughtMitigation.description",
  category: "water",
  audience: ["farmer", "expert", "manager"],
  icon: "🏜️",
  duration: "۱ هفته",
  satellitesUsed: ["chirps", "smap", "grace-fo"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.droughtMitigation.step1Title",
      descriptionKey: "scenarios.droughtMitigation.step1Desc",
      requiredDataKey: "scenarios.droughtMitigation.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.droughtMitigation.step2Title",
      descriptionKey: "scenarios.droughtMitigation.step2Desc",
      requiredDataKey: "scenarios.droughtMitigation.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.droughtMitigation.step3Title",
      descriptionKey: "scenarios.droughtMitigation.step3Desc",
      requiredDataKey: "scenarios.droughtMitigation.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.droughtMitigation.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.droughtMitigation.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.droughtMitigation.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.droughtMitigation.outputReport", format: "report" },
  ],
};
