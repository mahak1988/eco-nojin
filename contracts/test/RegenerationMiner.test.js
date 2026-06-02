const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Gaia Protocol Contracts", function () {
  let seedToken, gaiaCert, miner;
  let owner, user1, oracle;

  beforeEach(async function () {
    [owner, user1, oracle] = await ethers.getSigners();

    const SeedToken = await ethers.getContractFactory("SeedToken");
    seedToken = await SeedToken.deploy();
    await seedToken.waitForDeployment();

    const GaiaCertificate = await ethers.getContractFactory("GaiaCertificate");
    gaiaCert = await GaiaCertificate.deploy(owner.address);
    await gaiaCert.waitForDeployment();

    const RegenerationMiner = await ethers.getContractFactory("RegenerationMiner");
    miner = await RegenerationMiner.deploy(
      await seedToken.getAddress(),
      await gaiaCert.getAddress(),
      oracle.address
    );
    await miner.waitForDeployment();

    await seedToken.addMinter(await miner.getAddress());
  });

  describe("SeedToken", function () {
    it("Should have correct name and symbol", async function () {
      expect(await seedToken.name()).to.equal("Gaia Seed Token");
      expect(await seedToken.symbol()).to.equal("SEED");
    });

    it("Should allow minter to mint tokens", async function () {
      await seedToken.addMinter(owner.address);
      await seedToken.mint(user1.address, ethers.parseEther("1000"));
      expect(await seedToken.balanceOf(user1.address)).to.equal(ethers.parseEther("1000"));
    });
  });

  describe("GaiaCertificate", function () {
    it("Should mint a certificate", async function () {
      await gaiaCert.mintCertificate(
        user1.address,
        "tree_planting",
        7960000,
        "ipfs://test",
        "0x" + "a".repeat(64)
      );
      
      expect(await gaiaCert.ownerOf(1)).to.equal(user1.address);
      expect(await gaiaCert.totalSupply()).to.equal(1);
    });

    it("Should update certificate growth", async function () {
      await gaiaCert.mintCertificate(
        user1.address,
        "tree_planting",
        7960000,
        "ipfs://test",
        "0x" + "a".repeat(64)
      );

      await gaiaCert.updateCertificate(1, 15000000, 2, "ipfs://updated");
      
      const cert = await gaiaCert.getCertificate(1);
      expect(cert.carbonMilliKg).to.equal(15000000);
      expect(cert.growthStage).to.equal(2);
    });
  });
});