# EcoNojin Smart Contracts

Solidity smart contracts for the EcoNojin platform - an environmental stewardship blockchain system.

## Contracts

### EcoCoin.sol
Environmental token rewarding ecological actions with:
- 1:1 backing with verified ecological credits
- Multi-tier staking (3 months to 2 years)
- Oracle-controlled minting
- Burn mechanism for deflation

### VerificationOracle.sol
Verifies ecological projects and data:
- 5 credit types (tree planting, soil carbon, water conservation, biodiversity, renewable energy)
- IPFS hash storage for off-chain data
- Verifier registry system
- Credit calculation formulas

## Development

```bash
# Install dependencies
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test
```

## Deployment

Target: Polygon (for low fees) or Ethereum L2

Environment variables:
- `PRIVATE_KEY` - Deployer wallet private key
- `ALCHEMY_API_KEY` - RPC provider API key
- `POLYGONSCAN_API_KEY` - Verification API key