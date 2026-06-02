const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying Gaia Protocol to Local Hardhat Network...\n");
  
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 Deployer:", deployer.address);
  console.log("💰 Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\n");

  // 1) Deploy SeedToken
  console.log("1️⃣  Deploying SeedToken...");
  const SeedToken = await hre.ethers.getContractFactory("SeedToken");
  const seedToken = await SeedToken.deploy();
  await seedToken.waitForDeployment();
  const seedTokenAddress = await seedToken.getAddress();
  console.log("   ✅ SeedToken:", seedTokenAddress);

  // 2) Deploy GaiaCertificate
  console.log("\n2️⃣  Deploying GaiaCertificate...");
  const GaiaCertificate = await hre.ethers.getContractFactory("GaiaCertificate");
  const gaiaCert = await GaiaCertificate.deploy(deployer.address);
  await gaiaCert.waitForDeployment();
  const gaiaCertAddress = await gaiaCert.getAddress();
  console.log("   ✅ GaiaCertificate:", gaiaCertAddress);

  // 3) Deploy RegenerationMiner
  console.log("\n3️⃣  Deploying RegenerationMiner...");
  const RegenerationMiner = await hre.ethers.getContractFactory("RegenerationMiner");
  const miner = await RegenerationMiner.deploy(
    seedTokenAddress,
    gaiaCertAddress,
    deployer.address
  );
  await miner.waitForDeployment();
  const minerAddress = await miner.getAddress();
  console.log("   ✅ RegenerationMiner:", minerAddress);

  // 4) Configure
  console.log("\n4️⃣  Configuring permissions...");
  const addMinterTx = await seedToken.addMinter(minerAddress);
  await addMinterTx.wait();
  console.log("   ✅ Miner added as SEED minter");

  // 5) Test mint
  console.log("\n5️⃣  Minting first NFT certificate...");
  const mintTx = await gaiaCert.mintCertificate(
    deployer.address,
    "tree_planting",
    7960000, // 7.96 tons in milli-kg
    "ipfs://QmFirstCertificate",
    "0x" + "a".repeat(64)
  );
  const receipt = await mintTx.wait();
  console.log("   ✅ First NFT minted in block:", receipt.blockNumber);
  console.log("   🎉 Token ID: #1");

  // Summary
  console.log("\n" + "=".repeat(70));
  console.log("🎉 LOCAL DEPLOYMENT COMPLETE!");
  console.log("=".repeat(70));
  console.log("\n📋 Contract Addresses:");
  console.log(`   SeedToken:         ${seedTokenAddress}`);
  console.log(`   GaiaCertificate:   ${gaiaCertAddress}`);
  console.log(`   RegenerationMiner: ${minerAddress}`);
  console.log(`   Oracle (deployer): ${deployer.address}`);
  console.log("\n🔗 View on local explorer:");
  console.log("   http://localhost:8000 (if running blockscout)");
  console.log("\n💾 Save to .env:");
  console.log(`   SEED_TOKEN_ADDRESS=${seedTokenAddress}`);
  console.log(`   GAIA_CERT_ADDRESS=${gaiaCertAddress}`);
  console.log(`   MINER_CONTRACT_ADDRESS=${minerAddress}`);
  console.log("=".repeat(70));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
