# EcoCoin: Frontend · API · Smart contract bridge

## Architecture

```
React (/ecocoin*)  →  FastAPI /api/v1/ecocoin/*  →  ProtocolState + ledger
                                              ↘  EcoCoin.sol (optional RPC)
```

| Layer | Role |
|-------|------|
| **Frontend** | `ecocoinApi.ts` loads wallet, challenges, claim rewards |
| **API** | Mint, stake, transfer, challenges join/claim, rewards claim |
| **Local ledger** | `ecocoin_chain.ledger_append` — hash-chained audit without Docker/RPC |
| **Contract** | `contracts/contracts/EcoCoin.sol` — mint (oracle), stake, transfer |

## Local mode (default)

No RPC required. All writes update in-memory balances and append a SHA-256 `tx_hash` to the ledger.

```http
GET /api/v1/ecocoin/chain/status
GET /api/v1/ecocoin/challenges
POST /api/v1/ecocoin/challenges/{id}/join
POST /api/v1/ecocoin/challenges/{id}/claim
POST /api/v1/ecocoin/rewards/claim
```

## EVM mode (later)

Set in `.env`:

```env
ECOCOIN_RPC_URL=https://...
ECOCOIN_CONTRACT_ADDRESS=0x...
ECOCOIN_CHAIN_ID=11155111
# ECOCOIN_ORACLE_PRIVATE_KEY=  # server-side oracle only; never commit
```

Until a server signer is enabled, mint/claim still succeed off-chain and record `evm_intent` in the ledger.

## Rewards flow

1. User **joins** challenge → participants++
2. User **claims** with score → `reward_eco` added to **pending_rewards**
3. User **claims rewards** → pending → available balance + ledger tx

## Default demo address

`0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18` (seeded balance + pending rewards).
