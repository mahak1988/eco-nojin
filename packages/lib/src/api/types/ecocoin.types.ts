// ============================================================================
// 🔴 تطبیق دقیق با EcoCoin Models و Router
// ============================================================================

// منطبق با api/modules/ecocoin/router.py::TokenResponse
export interface EcoToken {
  symbol: string;           // "ECO" | "GRC"
  name: string;             // "EcoCoin" | "Green Carbon Credit"
  type: string;             // "utility" | "asset-backed"
  total_supply: number;
  circulating_supply: number;
  price_usd: number;
}

// منطبق با api/modules/ecocoin/router.py::RewardRateResponse
export interface RewardRate {
  action: string;           // "tree_planting", "water_saving", etc.
  reward: number;
  unit: string;             // "ECO per tree", etc.
}

// منطبق با api/modules/ecocoin/router.py::EcoCoinStatsResponse
export interface EcoCoinStats {
  wallets_count: number;
  total_rewards: number;
  actions_count: number;
  carbon_sequestered_tons: number;
  water_saved_liters: number;
  energy_generated_kwh: number;
}

// منطبق با api/modules/ecocoin/router.py::WalletResponse
export interface EcoWallet {
  wallet_id: number;
  address: string;
  eco_balance: number;
  grc_balance: number;
  staked_eco: number;
  staked_grc: number;
  total_earned: number;
  user_level: number;
  reputation_score: number;
  created_at: string;       // ISO datetime
}

// ============================================================================
// Enums (منطبق با api/modules/ecocoin/models.py)
// ============================================================================

export enum TokenType {
  ECO = "eco",
  GRC = "grc",
}

export enum TxType {
  REWARD = "reward",
  TRANSFER = "transfer",
  STAKE = "stake",
  UNSTAKE = "unstake",
  BURN = "burn",
  MINT = "mint",
  EXCHANGE = "exchange",
}

export enum TxStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  FAILED = "failed",
}

export enum EcoActionType {
  TREE_PLANTING = "tree_planting",
  LAND_RESTORATION = "land_restoration",
  WATER_SAVING = "water_saving",
  RENEWABLE_ENERGY = "renewable_energy",
  RECYCLING = "recycling",
  CARBON_REDUCTION = "carbon_reduction",
  SOIL_CONSERVATION = "soil_conservation",
  BIODIVERSITY = "biodiversity",
}

// ============================================================================
// Transaction & Action Types
// ============================================================================

export interface EcoTransaction {
  id: number;
  tx_hash: string;
  wallet_id: number;
  token_symbol: string;
  tx_type: TxType;
  amount: number;           // BigInteger
  fee: number;
  from_address?: string;
  to_address?: string;
  status: TxStatus;
  description?: string;
  created_at: string;
  confirmed_at?: string;
}

export interface EcoAction {
  id: number;
  user_id: number;
  action_type: EcoActionType;
  title: string;
  description?: string;
  quantity: number;
  unit: string;
  latitude?: number;
  longitude?: number;
  location_name?: string;
  status: string;           // RewardStatus
  eco_reward: number;
  grc_reward: number;
  carbon_sequestered?: number;
  water_saved?: number;
  created_at: string;
}

// ============================================================================
// Request Types
// ============================================================================

export interface TransferRequest {
  from_wallet_id: number;
  to_wallet_id: number;
  amount: number;
  token_symbol: string;
}

export interface TransferResponse {
  success: boolean;
  tx_hash: string;
  from_wallet: number;
  to_wallet: number;
  amount: number;
  token: string;
}

export interface StakeRequest {
  amount: number;
  lock_days?: number;
}

export interface StakeResponse {
  success: boolean;
  staked_amount: number;
  lock_period: number;
  expected_reward: number;
}

export interface ExchangeRequest {
  from_token: string;
  to_token: string;
  from_amount: number;
}

export interface ExchangeResponse {
  success: boolean;
  from_token: string;
  to_token: string;
  from_amount: number;
  to_amount: number;
  exchange_rate: number;
}

// Alias برای سازگاری با useEcoCoin
export type EcoCoinBalance = EcoWallet;
export type EcoCoinTransaction = EcoTransaction;
export type EcoCoinTransferRequest = TransferRequest;
export type EcoCoinTransferResponse = TransferResponse;
export type EcoCoinReward = RewardRate;
export type EcoCoinHistory = EcoToken[];

// ====== نوع Dashboard تجمیعی ======
export interface EcoCoinDashboard {
  wallet: EcoWallet;
  stats: EcoCoinStats;
  recentTransactions: EcoTransaction[];
  rewards: RewardRate[];
  token: EcoToken;
}
