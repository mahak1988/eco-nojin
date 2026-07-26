export interface AccountingSummary {
  total_income: string | number;
  total_expense: string | number;
  net_profit: string | number;
  current_balance: string | number;
  transactions_count: number;
  eco_rewards_distributed?: string | number;
  carbon_credits_value?: string | number;
}

export interface Account {
  id: string;
  code?: string;
  name: string;
  name_fa?: string;
  account_type: string;
  is_active?: boolean;
  balance?: string | number;
}
