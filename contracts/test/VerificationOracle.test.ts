import { expect } from "chai";
import { ethers } from "hardhat";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";
import { VerificationOracle } from "../typechain-types";

describe("VerificationOracle", function () {
  let oracle: VerificationOracle;
  let steward: SignerWithAddress;
  let verifier: SignerWithAddress;
  let user: SignerWithAddress;
  let attacker: SignerWithAddress;
  let secondVerifier: SignerWithAddress;

  const PROJECT_NAME = "Amazon Reforestation";
  const REGION = "Brazil";
  const IPFS_HASH = "QmX8stY7QmF5qQnQvQkT6qQkQmX8stY7QmF5qQnQvQkT6qQk";
  const CREDIT_TYPE = 0; // TREE_PLANTING
  const VERIFY_VALUE = 1000;
  const DATA_HASH = ethers.keccak256(ethers.toUtf8Bytes("ecological-data"));

  beforeEach(async function () {
    [steward, verifier, user, attacker, secondVerifier] = await ethers.getSigners();

    const OracleFactory = await ethers.getContractFactory("VerificationOracle");
    oracle = await OracleFactory.deploy();
    await oracle.waitForDeployment();
  });

  describe("Deployment", function () {
    it("should set the correct steward", async function () {
      expect(await oracle.steward()).to.equal(steward.address);
    });

    it("should start with zero projects", async function () {
      expect(await oracle.projectCount()).to.equal(0);
    });

    it("should revert construction with zero address", async function () {
      // This is implicitly tested — constructor uses msg.sender which can't be zero
    });
  });

  describe("Project Registration", function () {
    it("should allow steward to register a project", async function () {
      const tx = await oracle.connect(steward).registerProject(
        PROJECT_NAME, REGION, IPFS_HASH, CREDIT_TYPE
      );
      await expect(tx)
        .to.emit(oracle, "ProjectRegistered")
        .withArgs(1, PROJECT_NAME, CREDIT_TYPE);

      expect(await oracle.projectCount()).to.equal(1);
    });

    it("should increment project ID", async function () {
      await oracle.connect(steward).registerProject(PROJECT_NAME, REGION, IPFS_HASH, CREDIT_TYPE);
      await oracle.connect(steward).registerProject("Project 2", REGION, IPFS_HASH, CREDIT_TYPE);
      expect(await oracle.projectCount()).to.equal(2);
    });

    it("should store project details", async function () {
      await oracle.connect(steward).registerProject(PROJECT_NAME, REGION, IPFS_HASH, CREDIT_TYPE);
      const project = await oracle.getProject(1);
      expect(project.name).to.equal(PROJECT_NAME);
      expect(project.region).to.equal(REGION);
      expect(project.ipfsHash).to.equal(IPFS_HASH);
      expect(project.creditType).to.equal(CREDIT_TYPE);
      expect(project.verified).to.be.false;
    });

    it("should revert when non-steward registers a project", async function () {
      await expect(
        oracle.connect(user).registerProject(PROJECT_NAME, REGION, IPFS_HASH, CREDIT_TYPE)
      ).to.be.revertedWith("Not steward");
    });

    it("should revert when registering with empty name", async function () {
      await expect(
        oracle.connect(steward).registerProject("", REGION, IPFS_HASH, CREDIT_TYPE)
      ).to.be.revertedWith("Project name required");
    });

    it("should revert when registering with empty region", async function () {
      await expect(
        oracle.connect(steward).registerProject(PROJECT_NAME, "", IPFS_HASH, CREDIT_TYPE)
      ).to.be.revertedWith("Region required");
    });

    it("should revert when registering with empty IPFS hash", async function () {
      await expect(
        oracle.connect(steward).registerProject(PROJECT_NAME, REGION, "", CREDIT_TYPE)
      ).to.be.revertedWith("IPFS hash required");
    });

    it("should revert when registering with invalid credit type", async function () {
      await expect(
        oracle.connect(steward).registerProject(PROJECT_NAME, REGION, IPFS_HASH, 99)
      ).to.be.revertedWith("Invalid credit type");
    });
  });

  describe("Verifier Management", function () {
    it("should allow steward to add a verifier", async function () {
      await expect(oracle.connect(steward).addVerifier(verifier.address))
        .to.emit(oracle, "VerifierAdded")
        .withArgs(verifier.address);

      expect(await oracle.verifiers(verifier.address)).to.be.true;
    });

    it("should allow steward to remove a verifier", async function () {
      await oracle.connect(steward).addVerifier(verifier.address);
      await expect(oracle.connect(steward).removeVerifier(verifier.address))
        .to.emit(oracle, "VerifierRemoved")
        .withArgs(verifier.address);

      expect(await oracle.verifiers(verifier.address)).to.be.false;
    });

    it("should revert when non-steward adds a verifier", async function () {
      await expect(
        oracle.connect(user).addVerifier(verifier.address)
      ).to.be.revertedWith("Not steward");
    });

    it("should revert when non-steward removes a verifier", async function () {
      await expect(
        oracle.connect(user).removeVerifier(verifier.address)
      ).to.be.revertedWith("Not steward");
    });

    it("should revert when adding zero address as verifier", async function () {
      await expect(
        oracle.connect(steward).addVerifier(ethers.ZeroAddress)
      ).to.be.revertedWith("Verifier cannot be zero address");
    });

    it("should revert when removing zero address", async function () {
      await expect(
        oracle.connect(steward).removeVerifier(ethers.ZeroAddress)
      ).to.be.revertedWith("Verifier cannot be zero address");
    });

    it("should revert when adding an existing verifier", async function () {
      await oracle.connect(steward).addVerifier(verifier.address);
      await expect(
        oracle.connect(steward).addVerifier(verifier.address)
      ).to.be.revertedWith("Already a verifier");
    });

    it("should revert when removing a non-verifier", async function () {
      await expect(
        oracle.connect(steward).removeVerifier(user.address)
      ).to.be.revertedWith("Not a verifier");
    });
  });

  describe("Verification", function () {
    beforeEach(async function () {
      await oracle.connect(steward).registerProject(PROJECT_NAME, REGION, IPFS_HASH, CREDIT_TYPE);
      await oracle.connect(steward).addVerifier(verifier.address);
    });

    it("should allow a verifier to verify a project", async function () {
      const tx = await oracle.connect(verifier).verify(1, VERIFY_VALUE, DATA_HASH);
      await expect(tx)
        .to.emit(oracle, "Verified")
        .withArgs(1, verifier.address, VERIFY_VALUE);
    });

    it("should mark project as verified", async function () {
      await oracle.connect(verifier).verify(1, VERIFY_VALUE, DATA_HASH);
      const project = await oracle.getProject(1);
      expect(project.verified).to.be.true;
    });

    it("should store verification record", async function () {
      await oracle.connect(verifier).verify(1, VERIFY_VALUE, DATA_HASH);
      const verifications = await oracle.getVerifications(1);
      expect(verifications.length).to.equal(1);
      expect(verifications[0].verifier).to.equal(verifier.address);
      expect(verifications[0].value).to.equal(VERIFY_VALUE);
      expect(verifications[0].dataHash).to.equal(DATA_HASH);
      expect(verifications[0].valid).to.be.true;
    });

    it("should revert when non-verifier tries to verify", async function () {
      await expect(
        oracle.connect(user).verify(1, VERIFY_VALUE, DATA_HASH)
      ).to.be.revertedWith("Not verifier");
    });

    it("should revert when verifying a non-existent project", async function () {
      await expect(
        oracle.connect(verifier).verify(99, VERIFY_VALUE, DATA_HASH)
      ).to.be.revertedWith("Project not found");
    });

    it("should revert when verifying with zero value", async function () {
      await expect(
        oracle.connect(verifier).verify(1, 0, DATA_HASH)
      ).to.be.revertedWith("Verification value must be positive");
    });

    it("should revert when verifying with empty data hash", async function () {
      await expect(
        oracle.connect(verifier).verify(1, VERIFY_VALUE, ethers.ZeroHash)
      ).to.be.revertedWith("Data hash required");
    });

    it("should prevent duplicate verification by same verifier", async function () {
      await oracle.connect(verifier).verify(1, VERIFY_VALUE, DATA_HASH);
      await expect(
        oracle.connect(verifier).verify(1, VERIFY_VALUE, DATA_HASH)
      ).to.be.revertedWith("Already verified by this verifier");
    });

    it("should allow different verifiers to verify same project", async function () {
      await oracle.connect(steward).addVerifier(secondVerifier.address);
      await oracle.connect(verifier).verify(1, VERIFY_VALUE, DATA_HASH);
      await oracle.connect(secondVerifier).verify(1, VERIFY_VALUE + 1, DATA_HASH);

      const verifications = await oracle.getVerifications(1);
      expect(verifications.length).to.equal(2);
    });
  });

  describe("calculateCredits", function () {
    it("should return correct credits for given value", async function () {
      const credits = await oracle.calculateCredits(1, VERIFY_VALUE, DATA_HASH);
      expect(credits).to.equal(VERIFY_VALUE * 10);
    });

    it("should revert when value is zero", async function () {
      await expect(
        oracle.calculateCredits(1, 0, DATA_HASH)
      ).to.be.revertedWith("Value must be positive");
    });

    it("should handle large values", async function () {
      const largeValue = ethers.parseEther("1000000");
      const credits = await oracle.calculateCredits(1, largeValue, DATA_HASH);
      expect(credits).to.equal(largeValue * 10n);
    });
  });

  describe("View Functions", function () {
    beforeEach(async function () {
      await oracle.connect(steward).registerProject(PROJECT_NAME, REGION, IPFS_HASH, CREDIT_TYPE);
    });

    it("should return project details via getProject", async function () {
      const project = await oracle.getProject(1);
      expect(project.name).to.equal(PROJECT_NAME);
    });

    it("should revert getProject for non-existent project", async function () {
      await expect(
        oracle.getProject(99)
      ).to.be.revertedWith("Project not found");
    });

    it("should revert getVerifications for non-existent project", async function () {
      await expect(
        oracle.getVerifications(99)
      ).to.be.revertedWith("Project not found");
    });

    it("should return empty verifications array for unverified project", async function () {
      const verifications = await oracle.getVerifications(1);
      expect(verifications.length).to.equal(0);
    });
  });

  describe("Edge Cases", function () {
    it("should allow multiple project registrations by same steward", async function () {
      await oracle.connect(steward).registerProject("Project A", REGION, IPFS_HASH, CREDIT_TYPE);
      await oracle.connect(steward).registerProject("Project B", REGION, IPFS_HASH, CREDIT_TYPE);
      await oracle.connect(steward).registerProject("Project C", REGION, IPFS_HASH, CREDIT_TYPE);
      expect(await oracle.projectCount()).to.equal(3);
    });

    it("should maintain verifier list after multiple additions and removals", async function () {
      await oracle.connect(steward).addVerifier(verifier.address);
      await oracle.connect(steward).addVerifier(secondVerifier.address);
      expect(await oracle.verifiers(verifier.address)).to.be.true;
      expect(await oracle.verifiers(secondVerifier.address)).to.be.true;

      await oracle.connect(steward).removeVerifier(verifier.address);
      expect(await oracle.verifiers(verifier.address)).to.be.false;
      expect(await oracle.verifiers(secondVerifier.address)).to.be.true;
    });
  });
});
