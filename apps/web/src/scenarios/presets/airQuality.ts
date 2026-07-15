/**
 *  airQualityScenario — airQuality scenario preset
 */

import type { Scenario } from "../types";

export const airQualityScenario: Scenario = {
  id: "airQuality",
  nameKey: "scenarios.airQuality.name",
  descriptionKey: "scenarios.airQuality.description",
  category: "air",
  audience: ["manager", "expert", "researcher"],
  icon: "🌫️",
  duration: "۳-۵ روز",
  satellitesUsed: ["sentinel-5p", "modis"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.airQuality.step1Title",
      descriptionKey: "scenarios.airQuality.step1Desc",
      requiredDataKey: "scenarios.airQuality.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.airQuality.step2Title",
      descriptionKey: "scenarios.airQuality.step2Desc",
      requiredDataKey: "scenarios.airQuality.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.airQuality.step3Title",
      descriptionKey: "scenarios.airQuality.step3Desc",
      requiredDataKey: "scenarios.airQuality.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.airQuality.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.airQuality.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.airQuality.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.airQuality.outputReport", format: "report" },
  ],
};
