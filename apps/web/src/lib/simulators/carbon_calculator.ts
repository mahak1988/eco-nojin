// Carbon Calculator Simulator
export interface CarbonResult {
  totalEmissions: number;
  sequestration: number;
  netCarbon: number;
}

export function simulateCarbonCalculation(params: any): CarbonResult {
  return {
    totalEmissions: 150.5,
    sequestration: 200.3,
    netCarbon: 49.8
  };
}

export function generateMockPortfolio(address?: string): any[] {
  return [
    { id: '1', name: 'Field A', area: 50, carbonStock: 120.5, year: 2024 },
    { id: '2', name: 'Field B', area: 75, carbonStock: 180.3, year: 2024 }
  ];
}

export default { simulateCarbonCalculation, generateMockPortfolio };