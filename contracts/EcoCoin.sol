// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title EcoCoin - Environmental Stewardship Token
 * @notice Rewards ecological actions with blockchain-based verification
 */
contract EcoCoin {
    string public name = "EcoCoin";
    string public symbol = "ECO";
    uint8 public decimals = 18;
    uint256 public totalSupply = 312500000 * 10 ** decimals;
    uint256 public maxSupply = 1000000000 * 10 ** decimals;

    address public steward;
    address public oracle;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(uint256 => StakingInfo) public stakingTiers;
    mapping(address => mapping(uint256 => StakeInfo)) public stakes;

    uint256 private _totalMinted;
    uint256 private _totalBurned;

    struct StakingInfo {
        uint256 duration;
        uint256 apy;
        uint256 multiplier;
        uint256 minAmount;
    }

    struct StakeInfo {
        uint256 amount;
        uint256 startTime;
        uint256 unlockTime;
        uint256 tierId;
    }

    event Minted(address indexed to, uint256 amount, uint256 projectId, string reason);
    event Burned(address indexed from, uint256 amount);
    event Staked(address indexed user, uint256 amount, uint256 tierId);
    event Unstaked(address indexed user, uint256 amount, uint256 reward);
    event OracleUpdated(address indexed newOracle);

    modifier onlySteward() {
        require(msg.sender == steward || msg.sender == oracle, "Not steward");
        _;
    }

    modifier onlyOracle() {
        require(msg.sender == oracle, "Not oracle");
        _;
    }

    constructor() {
        steward = msg.sender;
        balanceOf[msg.sender] = totalSupply;
        _totalMinted = totalSupply;

        // Initialize staking tiers
        stakingTiers[0] = StakingInfo(90 days, 800, 12, 1000 * 10 ** decimals);  // 3 months, 8% APY
        stakingTiers[1] = StakingInfo(180 days, 1500, 15, 5000 * 10 ** decimals); // 6 months, 15% APY
        stakingTiers[2] = StakingInfo(365 days, 2500, 20, 10000 * 10 ** decimals); // 1 year, 25% APY
        stakingTiers[3] = StakingInfo(730 days, 5000, 30, 50000 * 10 ** decimals); // 2 years, 50% APY
    }

    function mint(
        address to,
        uint256 amount,
        uint256 projectId,
        string calldata reason,
        bytes calldata proof
    ) external onlyOracle {
        require(totalSupply + amount <= maxSupply, "Exceeds max supply");
        
        balanceOf[to] += amount;
        totalSupply += amount;
        _totalMinted += amount;

        emit Minted(to, amount, projectId, reason);
    }

    function burn(uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        totalSupply -= amount;
        _totalBurned += amount;
        emit Burned(msg.sender, amount);
    }

    function stake(uint256 tierId) external {
        StakingInfo memory tier = stakingTiers[tierId];
        require(tier.minAmount > 0, "Invalid tier");
        
        StakeInfo memory stakeInfo = stakes[msg.sender][tierId];
        require(stakeInfo.amount == 0, "Already staked");

        // Transfer tokens to contract
        // In production, would use ERC20.transferFrom
    }

    function unstake(uint256 tierId) external {
        StakeInfo storage stakeInfo = stakes[msg.sender][tierId];
        require(stakeInfo.amount > 0, "No stake found");
        require(block.timestamp >= stakeInfo.unlockTime, "Still locked");

        uint256 reward = calculateReward(stakeInfo.amount, stakeInfo.tierId, block.timestamp);
        // Transfer tokens back
        stakeInfo.amount = 0;
        emit Unstaked(msg.sender, stakeInfo.amount, reward);
    }

    function calculateReward(uint256 amount, uint256 tierId, uint256 duration) 
        public view returns (uint256) 
    {
        StakingInfo memory tier = stakingTiers[tierId];
        return (amount * tier.apy * duration) / 365 days / 100;
    }

    function setOracle(address newOracle) external onlySteward {
        oracle = newOracle;
        emit OracleUpdated(newOracle);
    }

    function totalMinted() external view returns (uint256) {
        return _totalMinted;
    }

    function totalBurned() external view returns (uint256) {
        return _totalBurned;
    }
}