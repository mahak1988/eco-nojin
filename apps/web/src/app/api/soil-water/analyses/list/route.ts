import { NextRequest, NextResponse } from "next/server";

export async function GET(_req: NextRequest) {
  // TODO: when backend implements list endpoint, proxy to it instead of this mock.
  const now = new Date().toISOString();

  const mock = {
    analyses: [
      {
        id: "DEMO-0001",
        region: "Nozhin watershed",
        soil_type: "Loam",
        area_ha: 12.5,
        crop: "Pistachio",
        irrigation_method: "Drip",
        results: {
          overall_score: 82,
        },
        status: "Completed (demo)",
        created_at: now,
        updated_at: now,
      },
      {
        id: "DEMO-0002",
        region: "Central plateau pilot",
        soil_type: "Clay loam",
        area_ha: 8.0,
        crop: "Wheat",
        irrigation_method: "Surface",
        results: {
          overall_score: 73,
        },
        status: "Completed (demo)",
        created_at: now,
        updated_at: now,
      },
    ],
    total: 2,
  };

  return NextResponse.json(mock, { status: 200 });
}