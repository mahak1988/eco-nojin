/**
 *  deforestationScenario — deforestation scenario preset
 */

import type { Scenario } from "../types";

export const deforestationScenario: Scenario = {
  id: "deforestation",
  nameKey: "scenarios.deforestation.name",
  descriptionKey: "scenarios.deforestation.description",
  category: "forest",
  audience: ["expert", "researcher", "manager"],
  icon: "🌲",
  duration: "۱-۲ هفته",
  satellitesUsed: ["landsat-8", "sentinel-2", "gedi"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.deforestation.step1Title",
      descriptionKey: "scenarios.deforestation.step1Desc",
      requiredDataKey: "scenarios.deforestation.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.deforestation.step2Title",
      descriptionKey: "scenarios.deforestation.step2Desc",
      requiredDataKey: "scenarios.deforestation.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.deforestation.step3Title",
      descriptionKey: "scenarios.deforestation.step3Desc",
      requiredDataKey: "scenarios.deforestation.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.deforestation.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.deforestation.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.deforestation.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.deforestation.outputReport", format: "report" },
  ],
};
