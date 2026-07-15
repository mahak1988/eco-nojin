/**
 *  urbanizationScenario — urbanization scenario preset
 */

import type { Scenario } from "../types";

export const urbanizationScenario: Scenario = {
  id: "urbanization",
  nameKey: "scenarios.urbanization.name",
  descriptionKey: "scenarios.urbanization.description",
  category: "urban",
  audience: ["manager", "expert"],
  icon: "🏙️",
  duration: "۲-۴ هفته",
  satellitesUsed: ["sentinel-2", "landsat-8", "viirs"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.urbanization.step1Title",
      descriptionKey: "scenarios.urbanization.step1Desc",
      requiredDataKey: "scenarios.urbanization.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.urbanization.step2Title",
      descriptionKey: "scenarios.urbanization.step2Desc",
      requiredDataKey: "scenarios.urbanization.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.urbanization.step3Title",
      descriptionKey: "scenarios.urbanization.step3Desc",
      requiredDataKey: "scenarios.urbanization.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.urbanization.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.urbanization.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.urbanization.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.urbanization.outputReport", format: "report" },
  ],
};
