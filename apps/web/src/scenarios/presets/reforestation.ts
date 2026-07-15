/**
 *  reforestationScenario — reforestation scenario preset
 */

import type { Scenario } from "../types";

export const reforestationScenario: Scenario = {
  id: "reforestation",
  nameKey: "scenarios.reforestation.name",
  descriptionKey: "scenarios.reforestation.description",
  category: "forest",
  audience: ["manager", "researcher"],
  icon: "🌳",
  duration: "۲-۳ هفته",
  satellitesUsed: ["gedi", "sentinel-2", "icesat-2"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.reforestation.step1Title",
      descriptionKey: "scenarios.reforestation.step1Desc",
      requiredDataKey: "scenarios.reforestation.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.reforestation.step2Title",
      descriptionKey: "scenarios.reforestation.step2Desc",
      requiredDataKey: "scenarios.reforestation.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.reforestation.step3Title",
      descriptionKey: "scenarios.reforestation.step3Desc",
      requiredDataKey: "scenarios.reforestation.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.reforestation.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.reforestation.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.reforestation.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.reforestation.outputReport", format: "report" },
  ],
};
