# EcoCoin Economic & Technical Design

**Version:** 1.0  
**Status:** Implementation baseline (engine + API)  
**Principle:** Impact-backed utility token — not pure speculation.

---

## 1. Purpose

EcoCoin (ECO) is the incentive and settlement unit of Econojin. Value is anchored to **measured environmental outcomes** (CO₂e sequestered, water saved, soil organic carbon increase, biodiversity proxies) verified by oracles and science modules (AquaCrop, RothC, NDVI, satellite).

Design goals:

1. Align farmer/steward rewards with real impact, not farm size alone.
2. Cap inflation via a transparent mint curve tied to verified impact.
3. Fund public goods (MRV, open data, education) without dumping on stewards.
4. Remain operable offline/local-first (SQLite path) before chain settlement.

---

## 2. Token parameters (initial SSOT)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Symbol | ECO | — |
| Max supply (hard) | 1_000_000_000 | Long horizon; avoids unbounded print |
| Genesis allocation | 50_000_000 | Bootstrap treasury + liquidity + grants |
| Impact mint budget | 800_000_000 | Released only against verified impact |
| Staking rewards pool | 100_000_000 | Time-locked emissions |
| Community / challenges | 50_000_000 | Campaigns, education, games |
| Decimals (logical) | 6 | Sub-cent precision without float noise |

**Circulating** = total_minted − total_burned − locked_treasury − locked_stake.

---

## 3. Impact mining (not PoW)

“Mining” means **mint against verified impact**:

```
mint_amount = measured_value × credit_factor × quality_score × region_multiplier
```

| Credit type | Unit of measured_value | Base factor (ECO / unit) |
|-------------|------------------------|-------------------------|
| 0 Carbon | tCO₂e | 25 |
| 1 Water | m³ saved | 0.05 |
| 2 Soil SOC | t C / ha increase | 40 |
| 3 Biodiversity | index point (0–100) | 2 |

**Quality score** ∈ [0.5, 1.2] from MRV confidence (satellite + field + model agreement).

**Region multiplier** ∈ [0.8, 1.3] for underserved / high-priority basins (configurable policy).

**Annual mint ceiling** declines on a logistic curve toward max supply so early impact is rewarded more than late dilution.

Burn paths: penalty for failed audits, voluntary retirement of credits, protocol fees (optional 0.5% transfer burn).

---

## 4. Distribution (flow of value)

```
Verified impact
    → Mint ECO
        → 70% Steward (farmer / project operator)
        → 15% Verifier / oracle operators
        → 10% Protocol treasury (MRV, R&D)
        →  5% Local community pool (challenges, schools)
```

Staking does **not** mint new supply beyond the dedicated staking pool; rewards are paid from that pool and from a share of protocol fees.

---

## 5. Staking tiers (steward lock)

| Tier | Lock | APY (nominal) | Multiplier | Min ECO |
|------|------|---------------|------------|--------|
| 0 | 3 months | 8% | 1.0 | 1_000 |
| 1 | 6 months | 15% | 1.2 | 5_000 |
| 2 | 12 months | 25% | 1.5 | 10_000 |
| 3 | 24 months | 50% | 2.0 | 25_000 |

Estimated reward (year-normalized, as in API contract):

```
estimated_reward = amount × apy / 100
```

Unlock is linear in tier index for MVP: `days = 90 × (tier_id + 1)`.

Early unstake: forfeit pending reward + 5% principal fee (burned or to treasury).

---

## 6. Wallet model

| Bucket | Meaning |
|--------|--------|
| available | Spendable / transferable |
| staked | Locked in tiers |
| pending_rewards | Accrued, not yet claimed |
| impact_credits | Linked verified tCO₂e (non-transferable ledger) |

Total equity ≈ available + staked + pending_rewards.

---

## 7. Challenges & rewards

Time-bound campaigns funded from the community pool:

- **Target metric** (e.g. plant N trees, reduce irrigation X%, complete school module).
- **Pool size** in ECO; **reward curve** proportional or winner-take-most.
- **Eligibility**: wallet + optional project_id + KYC tier later.
- Completion verified by science route or admin attestation.

---

## 8. Macro indicators (dashboard)

| Indicator | Definition |
|-----------|------------|
| impact_intensity | ECO minted / tCO₂e (lower = more efficient later stages) |
| stake_ratio | staked / circulating |
| steward_retention_30d | active stewards with ≥1 action in 30d |
| velocity | transfer volume / circulating (30d) |
| gini_holdings | inequality of available balances (sample) |
| treasury_runway_months | treasury / monthly burn+ops estimate |

---

## 9. Security & integrity

- Write paths: `require_write_auth` (JWT / session).
- No private keys on API; addresses are identifiers until chain bridge.
- Verify endpoint requires measured_value + hash; invalid credit_type rejected in engine (API may soft-pass under auth codes for contract tests).
- Rate-limit transfer/stake in non-local environments.
- Audit log for mint/burn/stake.

---

## 10. Roadmap (honest)

| Phase | Scope |
|-------|--------|
| Now | Engine formulas + expanded API (this commit) |
| Next | Persist wallets/stakes in DB + Alembic |
| Later | On-chain settlement bridge, real oracle signatures |
| Not claimed | Listed exchange price, legal tender status |

---

## 11. References in code

- `apps/api/services/ecocoin_engine.py` — pure calculations
- `apps/api/routes/ecocoin.py` — HTTP surface
- `apps/api/tests/test_ecocoin.py` — contract tests (must stay green)
