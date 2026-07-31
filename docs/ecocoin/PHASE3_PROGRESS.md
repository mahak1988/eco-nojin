# Phase 3 — Smart Contracts & Testnet

**Status:** Implemented (code + tests offline). **On-chain deploy** requires Foundry + faucet on Amoy/Celo Sepolia.

---

## Deliverables

| Item | Path | Status |
|------|------|--------|
| EcoCoin.sol | `contracts/src/EcoCoin.sol` | Done (cap 1B, roles, pause) |
| BucketTreasury.sol | `contracts/src/BucketTreasury.sol` | Done (A–E, draw/ENGINE_ROLE) |
| ImpactClaimRegistry.sol | `contracts/src/ImpactClaimRegistry.sol` | Done (attest, anti-double) |
| ImpactRewardEngine.sol | `contracts/src/ImpactRewardEngine.sol` | Done (EIP-712 + adminSettle) |
| Deploy script | `contracts/script/Deploy.s.sol` | Done |
| Foundry tests | `contracts/test/EcoCoin.t.sol` | Done (unit + fuzz) |
| foundry.toml / remappings | `contracts/` | Done |
| Install script | `contracts/scripts/install_foundry_deps.sh` | Done |
| EVM Python helpers | `apps/api/services/ecocoin_evm.py` | Done |
| Chain adapter dual-write | `apps/api/services/ecocoin_chain.py` | Done |
| Unit tests payloads | `tests/unit/test_ecocoin_evm.py` | Done |

---

## Security properties encoded

- Immutable **CAP** = 1e9 * 1e18
- Only **ImpactRewardEngine** should hold `MINTER_ROLE` after deploy
- **BucketTreasury** COMMUNITY drawn only by `ENGINE_ROLE`
- **claimSettled** + registry **exists** prevent double payout
- **ReentrancyGuard** on settle paths
- **EIP-712** oracle signatures (ORACLE_ROLE)
- **adminSettle** for pilot only — revoke / Timelock on mainnet
- **Pause** on EcoCoin for emergency transfer halt

---

## Deploy checklist (operator machine)

```bash
cd contracts
bash scripts/install_foundry_deps.sh
forge build
forge test -vvv

export PRIVATE_KEY=0x...          # funded testnet key — never commit
export ADMIN_ADDRESS=0x...
export AMOY_RPC=https://rpc-amoy.polygon.technology

forge script script/Deploy.s.sol:Deploy \
  --rpc-url $AMOY_RPC --broadcast --verify
```

Record addresses into `.env`:

```
ECOCOIN_MODE=evm
ECOCOIN_CHAIN_ID=80002
ECOCOIN_RPC_URL=...
ECOCOIN_CONTRACT_ADDRESS=0x...
ECOCOIN_REWARD_ENGINE=0x...
ECOCOIN_CLAIM_REGISTRY=0x...
ECOCOIN_TREASURY=0x...
ECOCOIN_ORACLE_KEY=0x...   # ORACLE_ROLE signer
```

---

## Backend behaviour

| Mode | Behaviour |
|------|-----------|
| `local_ledger` (default) | DB only |
| `evm` | Dual-write local mint + mark pending; on-chain settle when RPC/keys/ABI wired |

---

## Exit criteria

- [x] Full contract set in repo
- [x] Foundry test suite authored (run with forge)
- [x] Deploy script + role wiring documented
- [x] Backend EVM config + EIP-712 payload builder
- [ ] Live Amoy/Celo deploy (operator + faucet)
- [ ] Explorer verification
- [ ] Timelock + Safe transfer (ops)

---

## Next (Phase 4)

- Wallet connect UI, claim submission with geo/photo
- Oracle worker job for `settleReward`
- Transparency dashboard (treasury remaining + impact stats)
