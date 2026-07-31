# EcoCoin Monetary System — Single Source of Truth (SSOT)

**Version:** 1.0.0  
**Status:** Pilot / Educational–Scientific–Incentive Native  
**Last Updated:** 2026-07-31  
**Governing Principle:** Zero energy for token production. Token minting occurs **only** as a consequence of verified ecological impact or approved educational/action rewards. No proof-of-work, no mining, no idle inflation.

---

## 1. Core Rules (Non-Negotiable)

| Rule | Description |
|------|-------------|
| **Hard Cap** | Maximum supply = **1,000,000,000 ECO** (1 Billion). Immutable after deployment. |
| **No Energy for Mint** | Token creation never requires computational work or energy expenditure. Mint is triggered exclusively by the ImpactRewardEngine after verification. |
| **Zero Destruction Preference** | Tokens are not burned by default. Unused allocation remains in locked buckets. Optional burn only via governance for deflationary events (post-pilot). |
| **Impact-First** | Primary purpose = ecosystem restoration, education, and livelihood support for low-income / unemployed participants. |
| **Local-First Fallback** | `local_ledger` mode is the default safety mode until chain contracts are verified and oracles are live. |

---

## 2. Fixed Supply Allocation (1,000,000,000 ECO)

| Bucket | Code | Allocation | % | Purpose | Unlock / Vesting |
|--------|------|------------|---|---------|------------------|
| **A – Community Rewards** | `COMMUNITY` | 550,000,000 | 55% | Education, verified actions, livelihood for poor/unemployed, learning-to-earn, micro-PES | Gradual release via ImpactRewardEngine; no cliff for verified claims |
| **B – Organization Ops** | `ORG` | 250,000,000 | 25% | Salaries, operations, infrastructure, legal, scientific verification costs, micro-loans to participants | Timelock + multi-sig; quarterly vesting |
| **C – Ecosystem Treasury** | `TREASURY` | 100,000,000 | 10% | Liquidity seeding (DEX), grants matching, emergency restoration funds, institutional co-funding buffer | Gnosis Safe + TimelockController |
| **D – Scientific & Assurance** | `SCIENCE` | 70,000,000 | 7% | Independent audits, dMRV tooling, Hypercert-style registries, L3/L4 verification capacity | Multi-sig; release tied to assurance milestones |
| **E – Founders & Early Contributors** | `FOUNDERS` | 30,000,000 | 3% | Core team, early scientists, legal setup (capped, vested) | 24-month linear vesting + 6-month cliff |

**Total:** 1,000,000,000 ECO (100%).

---

## 3. Multi-Bucket Treasury Architecture

- Each bucket is an isolated accounting unit on-chain (BucketTreasury contract).
- Mint authority for Bucket A resides **only** in `ImpactRewardEngine`.
- Transfers between buckets require Timelock + Safe approval (except automated reward flow A → claimant).
- Off-chain `local_ledger` mirrors the same bucket structure for pilot phase.

---

## 4. Emission Schedule (Pilot → Mainnet)

1. **Pilot (local_ledger / Testnet):**  
   - Soft daily/weekly caps per category.  
   - No hard emission curve; controlled by verification throughput.

2. **Mainnet (Polygon or Celo):**  
   - Remaining supply stays locked in buckets.  
   - Release rate limited by verified impact volume + governance parameters.  
   - No automatic inflation.

---

## 5. Anti-Greenwashing & Integrity

- Every mint event must reference a claim ID in `ImpactClaimRegistry`.
- L1–L4 assurance levels determine reward multiplier and eligibility.
- Double-claim prevention via unique claim hash + idempotency keys.
- Oracle signatures required for on-chain settlement after pilot.

---

## 6. Institutional Compatibility

Designed for alignment with:
- FAO-style Payment for Ecosystem Services (PES)
- Corporate CSR / Scope 3 nature-based claims (with clear L-level disclosure)
- ICVCM Core Carbon Principles spirit (without early registry claim)
- Hypercerts / impact certificates as complementary attestation layer

---

## 7. Change Control

Any change to cap, allocation percentages, or mint rules requires:
1. On-chain Timelock delay
2. Multi-sig approval (Safe)
3. Public documentation update
4. Off-chain community notice period

---

*This document is the authoritative monetary policy for EcoCoin. All smart contracts, APIs, and UI must conform to it.*
