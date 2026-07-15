/**
 *  climateChangeScenario — climateChange scenario preset
 */

import type { Scenario } from "../types";

export const climateChangeScenario: Scenario = {
  id: "climateChange",
  nameKey: "scenarios.climateChange.name",
  descriptionKey: "scenarios.climateChange.description",
  category: "climate",
  audience: ["manager", "expert", "researcher"],
  icon: "🌡️",
  duration: "۲-۴ هفته",
  satellitesUsed: ["sentinel-2", "landsat-8", "modis"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.climateChange.step1Title",
      descriptionKey: "scenarios.climateChange.step1Desc",
      requiredDataKey: "scenarios.climateChange.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.climateChange.step2Title",
      descriptionKey: "scenarios.climateChange.step2Desc",
      requiredDataKey: "scenarios.climateChange.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.climateChange.step3Title",
      descriptionKey: "scenarios.climateChange.step3Desc",
      requiredDataKey: "scenarios.climateChange.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.climateChange.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.climateChange.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.climateChange.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.climateChange.outputReport", format: "report" },
  ],
};
