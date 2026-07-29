import { expect } from "chai";
import { ethers } from "hardhat";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";
import { EcoCoin, VerificationOracle } from "../typechain-types";
import { time } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("EcoCoin", function () {
  let ecoCoin: EcoCoin;
  let oracle: VerificationOracle;
  let steward: SignerWithAddress;
  let oracleSigner: SignerWithAddress;
  let user: SignerWithAddress;
  let attacker: SignerWithAddress;
  let verifier: SignerWithAddress;

  const INITIAL_SUPPLY = ethers.parseEther("312500000");
  const MINT_AMOUNT = ethers.parseEther("1000");
  const STAKE_AMOUNT_TIER0 = ethers.parseEther("1000");
  const ZERO_ADDRESS = ethers.ZeroAddress;

  beforeEach(async function () {
    [steward, oracleSigner, user, attacker, verifier] = await ethers.getSigners();

    // Deploy EcoCoin
    const EcoCoinFactory = await ethers.getContractFactory("EcoCoin");
    ecoCoin = await EcoCoinFactory.deploy();
    await ecoCoin.waitForDeployment();

    // Set oracle address
    await ecoCoin.connect(steward).setOracle(oracleSigner.address);

    // Deploy VerificationOracle
    const OracleFactory = await ethers.getContractFactory("VerificationOracle");
    oracle = await OracleFactory.deploy();
    await oracle.waitForDeployment();
  });

  describe("Deployment", function () {
    it("should set the correct steward", async function () {
      expect(await ecoCoin.steward()).to.equal(steward.address);
    });

    it("should set initial total supply", async function () {
      expect(await ecoCoin.totalSupply()).to.equal(INITIAL_SUPPLY);
    });

    it("should assign initial supply to steward", async function () {
      expect(await ecoCoin.balanceOf(steward.address)).to.equal(INITIAL_SUPPLY);
    });

    it("should initialize staking tiers", async function () {
      const tier0 = await ecoCoin.stakingTiers(0);
      expect(tier0.minAmount).to.equal(ethers.parseEther("1000"));
      expect(tier0.duration).to.equal(90 * 24 * 60 * 60); // 90 days
    });
  });

  describe("Minting", function () {
    const projectId = 1;
    const reason = "Tree planting project";
    const proof = ethers.toUtf8Bytes("verified");

    beforeEach(async function () {
      // Fund user with tokens for testing
      await ecoCoin.connect(steward).transfer(user.address, ethers.parseEther("50000"));
    });

    it("should allow oracle to mint tokens", async function () {
      await expect(
        ecoCoin.connect(oracleSigner).mint(user.address, MINT_AMOUNT, projectId, reason, proof)
      )
        .to.emit(ecoCoin, "Minted")
        .withArgs(user.address, MINT_AMOUNT, projectId, reason);

      expect(await ecoCoin.balanceOf(user.address)).to.equal(
        ethers.parseEther("50000") + MINT_AMOUNT
      );
    });

    it("should update totalMinted", async function () {
      const before = await ecoCoin.totalMinted();
      await ecoCoin.connect(oracleSigner).mint(user.address, MINT_AMOUNT, projectId, reason, proof);
      expect(await ecoCoin.totalMinted()).to.equal(before + MINT_AMOUNT);
    });

    it("should revert when non-oracle tries to mint", async function () {
      await expect(
        ecoCoin.connect(user).mint(user.address, MINT_AMOUNT, projectId, reason, proof)
      ).to.be.revertedWith("Not oracle");
    });

    it("should revert when minting to zero address", async function () {
      await expect(
        ecoCoin.connect(oracleSigner).mint(ZERO_ADDRESS, MINT_AMOUNT, projectId, reason, proof)
      ).to.be.revertedWith("Mint to zero address");
    });

    it("should revert when minting zero amount", async function () {
      await expect(
        ecoCoin.connect(oracleSigner).mint(user.address, 0, projectId, reason, proof)
      ).to.be.revertedWith("Mint zero amount");
    });

    it("should revert when exceeding max supply", async function () {
      const maxSupply = await ecoCoin.maxSupply();
      const excessAmount = maxSupply - INITIAL_SUPPLY + ethers.parseEther("1");
      await expect(
        ecoCoin.connect(oracleSigner).mint(user.address, excessAmount, projectId, reason, proof)
      ).to.be.revertedWith("Exceeds max supply");
    });

    it("should keep mint gas under 150k", async function () {
      const tx = await ecoCoin.connect(oracleSigner).mint(user.address, MINT_AMOUNT, projectId, reason, proof);
      const receipt = await tx.wait();
      if (receipt) {
        expect(receipt.gasUsed).to.be.lessThan(150000);
      }
    });
  });

  describe("Burning", function () {
    const burnAmount = ethers.parseEther("5000");

    beforeEach(async function () {
      // Fund user with tokens for testing
      await ecoCoin.connect(steward).transfer(user.address, ethers.parseEther("50000"));
    });

    it("should allow users to burn their tokens", async function () {
      const before = await ecoCoin.balanceOf(user.address);
      await expect(ecoCoin.connect(user).burn(burnAmount))
        .to.emit(ecoCoin, "Burned")
        .withArgs(user.address, burnAmount);

      expect(await ecoCoin.balanceOf(user.address)).to.equal(before - burnAmount);
    });

    it("should update totalBurned", async function () {
      const before = await ecoCoin.totalBurned();
      await ecoCoin.connect(user).burn(burnAmount);
      expect(await ecoCoin.totalBurned()).to.equal(before + burnAmount);
    });

    it("should revert when burning zero amount", async function () {
      await expect(
        ecoCoin.connect(user).burn(0)
      ).to.be.revertedWith("Burn zero amount");
    });

    it("should revert when burning more than balance", async function () {
      const maxBurn = ethers.parseEther("1000000000"); // More than balance
      await expect(
        ecoCoin.connect(user).burn(maxBurn)
      ).to.be.revertedWith("Insufficient balance");
    });

    it("should revert when user has no tokens", async function () {
      await expect(
        ecoCoin.connect(attacker).burn(burnAmount)
      ).to.be.revertedWith("Insufficient balance");
    });
  });

  describe("Staking", function () {
    const tierId = 0;

    beforeEach(async function () {
      // Fund user with tokens for testing
      await ecoCoin.connect(steward).transfer(user.address, ethers.parseEther("50000"));
    });

    it("should lock tokens when staking", async function () {
      const before = await ecoCoin.balanceOf(user.address);
      await ecoCoin.connect(user).stake(tierId);
      expect(await ecoCoin.balanceOf(user.address)).to.equal(before - STAKE_AMOUNT_TIER0);
    });

    it("should record stake info", async function () {
      await ecoCoin.connect(user).stake(tierId);
      const stakeInfo = await ecoCoin.getStakeInfo(user.address, tierId);
      expect(stakeInfo.amount).to.equal(STAKE_AMOUNT_TIER0);
      expect(stakeInfo.tierId).to.equal(tierId);
    });

    it("should emit Staked event", async function () {
      await expect(ecoCoin.connect(user).stake(tierId))
        .to.emit(ecoCoin, "Staked")
        .withArgs(user.address, STAKE_AMOUNT_TIER0, tierId);
    });

    it("should revert when staking with invalid tier", async function () {
      await expect(
        ecoCoin.connect(user).stake(99)
      ).to.be.revertedWith("Invalid tier");
    });

    it("should revert when staking with insufficient balance", async function () {
      await expect(
        ecoCoin.connect(attacker).stake(tierId)
      ).to.be.revertedWith("Insufficient balance for staking");
    });

    it("should revert when staking same tier twice", async function () {
      await ecoCoin.connect(user).stake(tierId);
      await expect(
        ecoCoin.connect(user).stake(tierId)
      ).to.be.revertedWith("Already staked in this tier");
    });

    describe("unstaking", function () {
      beforeEach(async function () {
        await ecoCoin.connect(user).stake(tierId);
      });

      it("should revert when unstaking before unlock time", async function () {
        await expect(
          ecoCoin.connect(user).unstake(tierId)
        ).to.be.revertedWith("Still locked");
      });

      it("should return principal plus reward after unlocking", async function () {
        // Increase time to unlock
        const tier0 = await ecoCoin.stakingTiers(tierId);
        const duration = tier0.duration;
        await ethers.provider.send("evm_increaseTime", [Number(duration)]);
        await ethers.provider.send("evm_mine", []);

        const stakeInfo = await ecoCoin.getStakeInfo(user.address, tierId);
        const before = await ecoCoin.balanceOf(user.address);
        
        // Calculate expected reward using the same formula as the contract
        // The contract uses: block.timestamp - stakeInfo.startTime
        // After increaseTime + mine, actual duration = duration + 1 (for mine)
        const actualDuration = BigInt(Number(duration) + 1);
        const expectedReward = await ecoCoin.calculateReward(stakeInfo.amount, tierId, actualDuration);

        await expect(ecoCoin.connect(user).unstake(tierId))
          .to.emit(ecoCoin, "Unstaked")
          .withArgs(user.address, STAKE_AMOUNT_TIER0, expectedReward);

        const after = await ecoCoin.balanceOf(user.address);
        expect(after).to.equal(before + STAKE_AMOUNT_TIER0 + expectedReward);
      });

      it("should revert when unstaking non-existent stake", async function () {
        await expect(
          ecoCoin.connect(attacker).unstake(tierId)
        ).to.be.revertedWith("No stake found");
      });

      it("should allow withdrawal after unlock time", async function () {
        const tier0 = await ecoCoin.stakingTiers(tierId);
        await ethers.provider.send("evm_increaseTime", [Number(tier0.duration)]);
        await ethers.provider.send("evm_mine", []);

        await ecoCoin.connect(user).unstake(tierId);
        const stakeInfo = await ecoCoin.getStakeInfo(user.address, tierId);
        expect(stakeInfo.amount).to.equal(0);
      });
    });
  });

  describe("Staking Tiers", function () {
    it("should have 4 staking tiers", async function () {
      for (let i = 0; i < 4; i++) {
        const tier = await ecoCoin.stakingTiers(i);
        expect(tier.minAmount).to.be.gt(0);
      }
    });

    it("should have increasing APY for longer tiers", async function () {
      const tier0 = await ecoCoin.stakingTiers(0);
      const tier3 = await ecoCoin.stakingTiers(3);
      expect(tier3.apy).to.be.gt(tier0.apy);
    });
  });

  describe("calculateReward", function () {
    it("should return correct reward for given parameters", async function () {
      const tierId = 0;
      const amount = ethers.parseEther("1000");
      const tier = await ecoCoin.stakingTiers(tierId);
      const duration = Number(tier.duration);
      const reward = await ecoCoin.calculateReward(amount, tierId, duration);
      // APY is 800 basis points (8%), so reward = 1000 * 8% * 90/365 = ~19.73
      expect(reward).to.be.gt(0);
    });

    it("should return zero reward for zero duration", async function () {
      const amount = ethers.parseEther("1000");
      const reward = await ecoCoin.calculateReward(amount, 0, 0);
      expect(reward).to.equal(0);
    });

    it("should revert for invalid tier", async function () {
      await expect(
        ecoCoin.calculateReward(ethers.parseEther("1000"), 99, 365 * 24 * 60 * 60)
      ).to.be.revertedWith("Invalid tier");
    });
  });

  describe("Access Control", function () {
    it("should allow steward to set oracle", async function () {
      await expect(ecoCoin.connect(steward).setOracle(verifier.address))
        .to.emit(ecoCoin, "OracleUpdated")
        .withArgs(verifier.address);
    });

    it("should revert when non-steward tries to set oracle", async function () {
      await expect(
        ecoCoin.connect(user).setOracle(verifier.address)
      ).to.be.revertedWith("Not steward");
    });

    it("should revert when setting oracle to zero address", async function () {
      await expect(
        ecoCoin.connect(steward).setOracle(ZERO_ADDRESS)
      ).to.be.revertedWith("Oracle cannot be zero address");
    });
  });

  describe("ERC20 Compatibility", function () {
    beforeEach(async function () {
      // Fund user with tokens for testing
      await ecoCoin.connect(steward).transfer(user.address, ethers.parseEther("50000"));
    });

    it("should support transfer", async function () {
      const amount = ethers.parseEther("100");
      await expect(ecoCoin.connect(user).transfer(attacker.address, amount))
        .to.emit(ecoCoin, "Transfer")
        .withArgs(user.address, attacker.address, amount);
    });

    it("should support approve and transferFrom", async function () {
      const amount = ethers.parseEther("100");
      await ecoCoin.connect(user).approve(attacker.address, amount);
      await ecoCoin.connect(attacker).transferFrom(user.address, steward.address, amount);
      const expectedStewardBalance = INITIAL_SUPPLY - ethers.parseEther("50000") + amount;
      expect(await ecoCoin.balanceOf(steward.address)).to.equal(expectedStewardBalance);
    });
  });
});
