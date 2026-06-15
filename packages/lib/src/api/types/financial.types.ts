/**
 * Financial Domain Types
 * تعاریف تایپ مرتبط با ماژول مالی
 */

export interface ProjectBudget {
  id?: number;
  project_id: string;
  capex: number;
  opex_annual: number;
  currency: 'USD' | 'IRR' | 'EUR';
  breakdown: BudgetBreakdown;
}

export interface BudgetBreakdown {
  labor: number;
  materials: number;
  equipment: number;
  monitoring: number;
  contingency: number;
}

export interface EconomicIndicator {
  npv: number;
  irr: number;
  benefit_cost_ratio: number;
  payback_period_years: number;
  sensitivity_analysis: SensitivityResult[];
}

export interface SensitivityResult {
  parameter: string;
  variation_percent: number;
  npv_impact: number;
}

export interface CarbonCredit {
  id?: string;
  project_id: string;
  volume_tco2e: number;
  verification_date: string;
  price_per_ton: number;
  status: 'PENDING' | 'VERIFIED' | 'ISSUED' | 'SOLD';
}
