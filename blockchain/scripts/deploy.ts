// blockchain/scripts/deploy.ts
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with:", deployer.address);

  // ۱. Deploy VerificationRegistry
  const VerificationRegistry = await ethers.getContractFactory("VerificationRegistry");
  const verification = await VerificationRegistry.deploy(deployer.address);
  await verification.waitForDeployment();
  console.log("VerificationRegistry deployed to:", await verification.getAddress());

  // ۲. Deploy EcoCoin
  const EcoCoin = await ethers.getContractFactory("EcoCoin");
  const ecoCoin = await EcoCoin.deploy(deployer.address, await verification.getAddress());
  await ecoCoin.waitForDeployment();
  console.log("EcoCoin deployed to:", await ecoCoin.getAddress());

  // ۳. Deploy EcoCredit
  const EcoCredit = await ethers.getContractFactory("EcoCredit");
  const ecoCredit = await EcoCredit.deploy(deployer.address);
  await ecoCredit.waitForDeployment();
  console.log("EcoCredit deployed to:", await ecoCredit.getAddress());

  // ۴. Deploy EcoReputation
  const EcoReputation = await ethers.getContractFactory("EcoReputation");
  const ecoRep = await EcoReputation.deploy(deployer.address);
  await ecoRep.waitForDeployment();
  console.log("EcoReputation deployed to:", await ecoRep.getAddress());

  // ۵. Deploy EcoBond
  const EcoBond = await ethers.getContractFactory("EcoBond");
  const reserveToken = "0x..."; // USDC/DAI address
  const ecoBond = await EcoBond.deploy(
    deployer.address,
    reserveToken,
    await ecoCoin.getAddress(),
    deployer.address, // commons treasury
    deployer.address  // liquidity pool
  );
  await ecoBond.waitForDeployment();
  console.log("EcoBond deployed to:", await ecoBond.getAddress());

  console.log("\n✅ All contracts deployed successfully!");
  console.log("\nUpdate apps/web/src/lib/contracts.ts with these addresses.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
