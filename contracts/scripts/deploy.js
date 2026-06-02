const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying Gaia Protocol to", hre.network.name, "\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 Deployer:", deployer.address);
  console.log("💰 Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\n");

  console.log("1️⃣  Deploying SeedToken...");
  const SeedToken = await hre.ethers.getContractFactory("SeedToken");
  const seedToken = await SeedToken.deploy();
  await seedToken.waitForDeployment();
  const seedAddr = await seedToken.getAddress();
  console.log("   ✅ SeedToken:", seedAddr);

  console.log("\n2️⃣  Deploying GaiaCertificate...");
  const GaiaCert = await hre.ethers.getContractFactory("GaiaCertificate");
  const gaiaCert = await GaiaCert.deploy(deployer.address);
  await gaiaCert.waitForDeployment();
  const certAddr = await gaiaCert.getAddress();
  console.log("   ✅ GaiaCertificate:", certAddr);

  console.log("\n3️⃣  Deploying RegenerationMiner...");
  const Miner = await hre.ethers.getContractFactory("RegenerationMiner");
  const miner = await Miner.deploy(seedAddr, certAddr, deployer.address);
  await miner.waitForDeployment();
  const minerAddr = await miner.getAddress();
  console.log("   ✅ RegenerationMiner:", minerAddr);

  console.log("\n4️⃣  Configuring...");
  await (await seedToken.addMinter(minerAddr)).wait();
  console.log("   ✅ Miner added as SEED minter");
  await (await gaiaCert.transferOwnership(minerAddr)).wait();
  console.log("   ✅ Cert ownership transferred to Miner");

  console.log("\n" + "=".repeat(70));
  console.log("🎉 DEPLOYMENT COMPLETE on", hre.network.name);
  console.log("=".repeat(70));
  console.log("\n📋 Contract Addresses:");
  console.log(`   SEED_TOKEN_ADDRESS=${seedAddr}`);
  console.log(`   GAIA_CERT_ADDRESS=${certAddr}`);
  console.log(`   MINER_CONTRACT_ADDRESS=${minerAddr}`);
  console.log(`   ORACLE_ADDRESS=${deployer.address}`);
  console.log("\n🔗 Explorer:");
  if (hre.network.name === "polygonAmoy") {
    console.log(`   https://amoy.polygonscan.com/address/${minerAddr}`);
  } else if (hre.network.name === "polygon") {
    console.log(`   https://polygonscan.com/address/${minerAddr}`);
  }
  console.log("=".repeat(70));
}

main().then(() => process.exit(0)).catch((error) => { console.error(error); process.exit(1); });
