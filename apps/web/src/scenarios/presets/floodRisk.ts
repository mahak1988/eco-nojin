/**
 *  floodRiskScenario — floodRisk scenario preset
 */

import type { Scenario } from "../types";

export const floodRiskScenario: Scenario = {
  id: "floodRisk",
  nameKey: "scenarios.floodRisk.name",
  descriptionKey: "scenarios.floodRisk.description",
  category: "risk",
  audience: ["manager", "expert"],
  icon: "🌊",
  duration: "۱-۲ هفته",
  satellitesUsed: ["sentinel-1", "gpm", "smap"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.floodRisk.step1Title",
      descriptionKey: "scenarios.floodRisk.step1Desc",
      requiredDataKey: "scenarios.floodRisk.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.floodRisk.step2Title",
      descriptionKey: "scenarios.floodRisk.step2Desc",
      requiredDataKey: "scenarios.floodRisk.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.floodRisk.step3Title",
      descriptionKey: "scenarios.floodRisk.step3Desc",
      requiredDataKey: "scenarios.floodRisk.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.floodRisk.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.floodRisk.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.floodRisk.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.floodRisk.outputReport", format: "report" },
  ],
};
