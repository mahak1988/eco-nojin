const hre = require("hardhat");

async function main() {
  console.log("🪙 Minting First Living NFT Certificate...\n");

  const [deployer] = await hre.ethers.getSigners();
  
  // آدرس‌ها از environment variables
  const GAIA_CERT_ADDRESS = process.env.GAIA_CERT_ADDRESS;
  const MINER_ADDRESS = process.env.MINER_CONTRACT_ADDRESS;
  
  if (!GAIA_CERT_ADDRESS || !MINER_ADDRESS) {
    console.error("❌ Please set GAIA_CERT_ADDRESS and MINER_CONTRACT_ADDRESS in .env");
    process.exit(1);
  }

  const gaiaCert = await hre.ethers.getContractAt("GaiaCertificate", GAIA_CERT_ADDRESS);
  
  // داده‌های اولین فعالیت واقعی
  const activityData = {
    owner: deployer.address,
    activityType: "tree_planting",
    carbonMilliKg: 7960 * 1000, // 7.96 tons = 7960 kg -> milli
    tokenURI: "ipfs://QmExampleFirstNFTMetadata",
    evidenceHash: "0x" + "a".repeat(64),
  };

  console.log("📝 Minting certificate with:");
  console.log(`   Owner:        ${activityData.owner}`);
  console.log(`   Activity:     ${activityData.activityType}`);
  console.log(`   Carbon:       ${activityData.carbonMilliKg / 1000} kg`);
  console.log(`   Token URI:    ${activityData.tokenURI}`);
  console.log();

  // Mint
  const tx = await gaiaCert.mintCertificate(
    activityData.owner,
    activityData.activityType,
    activityData.carbonMilliKg,
    activityData.tokenURI,
    activityData.evidenceHash
  );
  
  console.log("⏳ Transaction sent:", tx.hash);
  console.log("   Waiting for confirmation...");
  
  const receipt = await tx.wait();
  console.log("✅ Transaction confirmed in block:", receipt.blockNumber);
  
  // استخراج tokenId از event
  const event = receipt.logs.find(log => {
    try {
      const parsed = gaiaCert.interface.parseLog(log);
      return parsed && parsed.name === "CertificateMinted";
    } catch { return false; }
  });
  
  if (event) {
    const parsed = gaiaCert.interface.parseLog(event);
    const tokenId = parsed.args.tokenId;
    console.log(`\n🎉 FIRST LIVING NFT MINTED!`);
    console.log(`   Token ID:     #${tokenId}`);
    console.log(`   View:         https://amoy.polygonscan.com/token/${GAIA_CERT_ADDRESS}?a=${tokenId}`);
    console.log(`   OpenSea:      https://testnets.opensea.io/assets/amoy/${GAIA_CERT_ADDRESS}/${tokenId}`);
  }
  
  // نمایش total supply
  const totalSupply = await gaiaCert.totalSupply();
  console.log(`\n📊 Total certificates minted: ${totalSupply}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });