/**
 *  biodiversityConservationScenario — biodiversityConservation scenario preset
 */

import type { Scenario } from "../types";

export const biodiversityConservationScenario: Scenario = {
  id: "biodiversityConservation",
  nameKey: "scenarios.biodiversityConservation.name",
  descriptionKey: "scenarios.biodiversityConservation.description",
  category: "biodiversity",
  audience: ["researcher", "expert"],
  icon: "🦋",
  duration: "۳-۶ هفته",
  satellitesUsed: ["gedi", "icesat-2", "sentinel-2"],
  steps: [
    {
      order: 1,
      titleKey: "scenarios.biodiversityConservation.step1Title",
      descriptionKey: "scenarios.biodiversityConservation.step1Desc",
      requiredDataKey: "scenarios.biodiversityConservation.step1Data",
    },
    {
      order: 2,
      titleKey: "scenarios.biodiversityConservation.step2Title",
      descriptionKey: "scenarios.biodiversityConservation.step2Desc",
      requiredDataKey: "scenarios.biodiversityConservation.step2Data",
    },
    {
      order: 3,
      titleKey: "scenarios.biodiversityConservation.step3Title",
      descriptionKey: "scenarios.biodiversityConservation.step3Desc",
      requiredDataKey: "scenarios.biodiversityConservation.step3Data",
    },
  ],
  inputs: [
    { id: "region", labelKey: "scenarios.biodiversityConservation.inputRegion", type: "user", required: true },
    { id: "timeframe", labelKey: "scenarios.biodiversityConservation.inputTimeframe", type: "user", required: true },
  ],
  outputs: [
    { id: "map", labelKey: "scenarios.biodiversityConservation.outputMap", format: "map" },
    { id: "report", labelKey: "scenarios.biodiversityConservation.outputReport", format: "report" },
  ],
};
