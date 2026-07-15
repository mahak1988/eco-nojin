/**
 *  wildfireScenario — wildfire scenario preset
 */

import type { Scenario } from "../types";

export const wildfireScenario: Scenario = {
  id: "wildfire",
  nameKey: "scenarios.wildfire.name",
  descriptionKey: "scenarios.wildfire.description",
  category: "risk",
  audience: ["manager", "expert"],
  icon: "🔥",
  duration: "۱-۳ روز",
  satellitesUsed: ["viirs", "modis", "sentinel-2"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.wildfire.step1Title",
      descriptionKey: "scenarios.wildfire.step1Desc",
      requiredDataKey: "scenarios.wildfire.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.wildfire.step2Title",
      descriptionKey: "scenarios.wildfire.step2Desc",
      requiredDataKey: "scenarios.wildfire.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.wildfire.step3Title",
      descriptionKey: "scenarios.wildfire.step3Desc",
      requiredDataKey: "scenarios.wildfire.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.wildfire.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.wildfire.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.wildfire.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.wildfire.outputReport", format: "report" },
  ],
};
