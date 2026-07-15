/**
 *  agriculturalMonitoringScenario — agriculturalMonitoring scenario preset
 */

import type { Scenario } from "../types";

export const agriculturalMonitoringScenario: Scenario = {
  id: "agriculturalMonitoring",
  nameKey: "scenarios.agriculturalMonitoring.name",
  descriptionKey: "scenarios.agriculturalMonitoring.description",
  category: "agriculture",
  audience: ["farmer", "expert"],
  icon: "🌾",
  duration: "۱-۲ هفته",
  satellitesUsed: ["sentinel-2", "smap", "chirps"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.agriculturalMonitoring.step1Title",
      descriptionKey: "scenarios.agriculturalMonitoring.step1Desc",
      requiredDataKey: "scenarios.agriculturalMonitoring.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.agriculturalMonitoring.step2Title",
      descriptionKey: "scenarios.agriculturalMonitoring.step2Desc",
      requiredDataKey: "scenarios.agriculturalMonitoring.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.agriculturalMonitoring.step3Title",
      descriptionKey: "scenarios.agriculturalMonitoring.step3Desc",
      requiredDataKey: "scenarios.agriculturalMonitoring.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.agriculturalMonitoring.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.agriculturalMonitoring.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.agriculturalMonitoring.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.agriculturalMonitoring.outputReport", format: "report" },
  ],
};
