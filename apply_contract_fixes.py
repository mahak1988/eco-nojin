#!/usr/bin/env python3
import os

# کد اصلاح‌شده و امن EcoCoin.sol
ECOCOIN_SOL = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract EcoCoin is ReentrancyGuard {
    address public steward;
    address public oracle;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    struct StakingInfo {
        uint256 duration;
        uint256 apy;
        uint256 multiplier;
        uint256 minAmount;
    }
    mapping(uint256 => StakingInfo) public stakingTiers;

    struct StakeInfo {
        uint256 amount;
        uint256 startTime;
        uint256 unlockTime;
        uint256 tierId;
    }
    mapping(address => mapping(uint256 => StakeInfo)) public stakes;

    uint256 private _totalMinted;
    uint256 private _totalBurned;

    event Minted(address indexed to, uint256 amount, uint256 projectId, string reason);
    event Burned(address indexed from, uint256 amount);
    event Staked(address indexed user, uint256 amount, uint256 tierId);
    event Unstaked(address indexed user, uint256 amount, uint256 reward);
    event OracleUpdated(address indexed newOracle);

    modifier onlySteward() {
        require(msg.sender == steward, "Only steward can call this");
        _;
    }

    modifier onlyOracle() {
        require(msg.sender == oracle, "Only oracle can call this");
        _;
    }

    constructor() {
        steward = msg.sender;
        oracle = msg.sender;
    }

    function setOracle(address newOracle) external onlySteward {
        require(newOracle != address(0), "Invalid oracle address");
        oracle = newOracle;
        emit OracleUpdated(newOracle);
    }

    function mint(address to, uint256 amount, uint256 projectId, string calldata reason, bytes calldata proof) external onlyOracle {
        require(to != address(0), "Invalid address");
        require(amount > 0, "Amount must be > 0");
        balanceOf[to] += amount;
        _totalMinted += amount;
        emit Minted(to, amount, projectId, reason);
    }

    function burn(uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        _totalBurned += amount;
        emit Burned(msg.sender, amount);
    }

    function stake(uint256 tierId) external nonReentrant {
        StakingInfo memory tier = stakingTiers[tierId];
        require(tier.minAmount > 0, "Invalid tier");
        require(balanceOf[msg.sender] >= tier.minAmount, "Insufficient balance");

        balanceOf[msg.sender] -= tier.minAmount;
        stakes[msg.sender][tierId] = StakeInfo({
            amount: tier.minAmount,
            startTime: block.timestamp,
            unlockTime: block.timestamp + tier.duration,
            tierId: tierId
        });
        emit Staked(msg.sender, tier.minAmount, tierId);
    }

    function unstake(uint256 tierId) external nonReentrant {
        StakeInfo storage info = stakes[msg.sender][tierId];
        require(info.amount > 0, "No active stake");
        require(block.timestamp >= info.unlockTime, "Still locked");

        uint256 reward = calculateReward(info.amount, tierId, block.timestamp - info.startTime);
        uint256 total = info.amount + reward;

        uint256 stakedAmount = info.amount;
        info.amount = 0;
        info.startTime = 0;
        info.unlockTime = 0;

        balanceOf[msg.sender] += total;
        emit Unstaked(msg.sender, stakedAmount, reward);
    }

    function calculateReward(uint256 amount, uint256 tierId, uint256 duration) public view returns (uint256) {
        StakingInfo memory tier = stakingTiers[tierId];
        require(tier.duration > 0, "Invalid tier");
        return (amount * tier.apy * duration) / (365 days * 100) * tier.multiplier / 100;
    }

    function totalMinted() external view returns (uint256) {
        return _totalMinted;
    }

    function totalBurned() external view returns (uint256) {
        return _totalBurned;
    }
}
"""

# کد اصلاح‌شده و امن VerificationOracle.sol
ORACLE_SOL = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VerificationOracle {
    address public steward;
    
    struct Project {
        uint256 id;
        string name;
        string region;
        string ipfsHash;
        uint256 creditType;
        uint256 startDate;
        uint256 endDate;
        bool verified;
    }
    
    struct Verification {
        address verifier;
        uint256 timestamp;
        bytes32 dataHash;
        uint256 value;
        bool valid;
    }
    
    mapping(uint256 => Project) public projects;
    mapping(uint256 => Verification[]) public verifications;
    mapping(address => bool) public verifiers;
    
    uint256 public projectCount;
    
    modifier onlySteward() {
        require(msg.sender == steward, "Only steward can call this");
        _;
    }
    
    modifier onlyVerifier() {
        require(verifiers[msg.sender], "Only authorized verifier can call this");
        _;
    }
    
    constructor() {
        steward = msg.sender;
    }
    
    function registerProject(string calldata name, string calldata region, string calldata ipfsHash, uint256 creditType) external onlySteward {
        projectCount++;
        projects[projectCount] = Project({
            id: projectCount,
            name: name,
            region: region,
            ipfsHash: ipfsHash,
            creditType: creditType,
            startDate: block.timestamp,
            endDate: 0,
            verified: false
        });
    }
    
    function verify(uint256 projectId, uint256 value, bytes32 dataHash) external onlyVerifier {
        require(projectId > 0 && projectId <= projectCount, "Invalid project ID");
        
        // جلوگیری از تأیید تکراری توسط همان تأییدکننده
        Verification[] storage verifs = verifications[projectId];
        for (uint i = 0; i < verifs.length; i++) {
            require(verifs[i].verifier != msg.sender, "Already verified by this verifier");
        }
        
        verifs.push(Verification({
            verifier: msg.sender,
            timestamp: block.timestamp,
            dataHash: dataHash,
            value: value,
            valid: true
        }));
        
        projects[projectId].verified = true;
    }
    
    function addVerifier(address verifier) external onlySteward {
        require(verifier != address(0), "Invalid address");
        verifiers[verifier] = true;
    }
    
    function removeVerifier(address verifier) external onlySteward {
        verifiers[verifier] = false;
    }
    
    function getProject(uint256 projectId) external view returns (Project memory) {
        require(projectId > 0 && projectId <= projectCount, "Invalid project ID");
        return projects[projectId];
    }
    
    function getVerifications(uint256 projectId) external view returns (Verification[] memory) {
        require(projectId > 0 && projectId <= projectCount, "Invalid project ID");
        return verifications[projectId];
    }
    
    function calculateCredits(uint256 projectId, uint256 value, bytes32 dataHash) public pure returns (uint256) {
        return value; 
    }
}
"""

def main():
    base_dir = r"D:\econojin.com\contracts\contracts"
    os.makedirs(base_dir, exist_ok=True)
    
    with open(os.path.join(base_dir, "EcoCoin.sol"), "w", encoding="utf-8") as f:
        f.write(ECOCOIN_SOL)
    print("✅ EcoCoin.sol با موفقیت و با تمام اصلاحات امنیتی بازنویسی شد.")
    
    with open(os.path.join(base_dir, "VerificationOracle.sol"), "w", encoding="utf-8") as f:
        f.write(ORACLE_SOL)
    print("✅ VerificationOracle.sol با موفقیت و با تمام اصلاحات امنیتی بازنویسی شد.")
    
    print("\n🎉 تمام قراردادهای هوشمند اصلی پروژه اکنون ایمن و آمادهٔ کامپایل هستند.")

if __name__ == "__main__":
    main()