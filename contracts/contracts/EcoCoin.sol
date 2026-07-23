// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title EcoCoin - Environmental Stewardship Token
 * @notice Rewards ecological actions with blockchain-based verification
 * @dev Implements ERC20-like token with mint/burn/staking, onlySteward and onlyOracle modifiers
 */
contract EcoCoin is ReentrancyGuard {
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
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Transfer(address indexed from, address indexed to, uint256 value);

    modifier onlySteward() {
        require(msg.sender == steward, "Not steward");
        _;
    }

    modifier onlyOracle() {
        require(msg.sender == oracle, "Not oracle");
        _;
    }

    constructor() {
        require(msg.sender != address(0), "Zero address steward");
        steward = msg.sender;
        balanceOf[msg.sender] = totalSupply;
        _totalMinted = totalSupply;

        // Initialize staking tiers
        stakingTiers[0] = StakingInfo(90 days, 800, 12, 1000 * 10 ** decimals);  // 3 months, 8% APY
        stakingTiers[1] = StakingInfo(180 days, 1500, 15, 5000 * 10 ** decimals); // 6 months, 15% APY
        stakingTiers[2] = StakingInfo(365 days, 2500, 20, 10000 * 10 ** decimals); // 1 year, 25% APY
        stakingTiers[3] = StakingInfo(730 days, 5000, 30, 50000 * 10 ** decimals); // 2 years, 50% APY
    }

    // ----- ERC20 Compatibility -----

    function transfer(address to, uint256 amount) external returns (bool) {
        require(to != address(0), "ERC20: transfer to zero address");
        require(balanceOf[msg.sender] >= amount, "ERC20: insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(from != address(0), "ERC20: transfer from zero address");
        require(to != address(0), "ERC20: transfer to zero address");
        require(balanceOf[from] >= amount, "ERC20: insufficient balance");
        require(allowance[from][msg.sender] >= amount, "ERC20: insufficient allowance");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
        return true;
    }

    // ----- Mint & Burn -----

    function mint(
        address to,
        uint256 amount,
        uint256 projectId,
        string calldata reason,
        bytes calldata proof
    ) external onlyOracle {
        require(to != address(0), "Mint to zero address");
        require(amount > 0, "Mint zero amount");
        require(totalSupply + amount <= maxSupply, "Exceeds max supply");

        balanceOf[to] += amount;
        totalSupply += amount;
        _totalMinted += amount;

        emit Minted(to, amount, projectId, reason);
        emit Transfer(address(0), to, amount);
    }

    function burn(uint256 amount) external {
        require(amount > 0, "Burn zero amount");
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");

        balanceOf[msg.sender] -= amount;
        totalSupply -= amount;
        _totalBurned += amount;

        emit Burned(msg.sender, amount);
        emit Transfer(msg.sender, address(0), amount);
    }

    // ----- Staking with Reentrancy Guard -----

    function stake(uint256 tierId) external nonReentrant {
        StakingInfo memory tier = stakingTiers[tierId];
        require(tier.minAmount > 0, "Invalid tier");
        require(tier.minAmount > 0, "Tier does not exist");

        StakeInfo storage existingStake = stakes[msg.sender][tierId];
        require(existingStake.amount == 0, "Already staked in this tier");

        uint256 amount = tier.minAmount;
        require(balanceOf[msg.sender] >= amount, "Insufficient balance for staking");

        // CEI pattern: effects first
        balanceOf[msg.sender] -= amount;
        stakes[msg.sender][tierId] = StakeInfo({
            amount: amount,
            startTime: block.timestamp,
            unlockTime: block.timestamp + tier.duration,
            tierId: tierId
        });

        emit Staked(msg.sender, amount, tierId);
        emit Transfer(msg.sender, address(this), amount);
    }

    function unstake(uint256 tierId) external nonReentrant {
        StakeInfo storage stakeInfo = stakes[msg.sender][tierId];
        require(stakeInfo.amount > 0, "No stake found");
        require(block.timestamp >= stakeInfo.unlockTime, "Still locked");

        uint256 duration = block.timestamp - stakeInfo.startTime;
        uint256 reward = calculateReward(stakeInfo.amount, stakeInfo.tierId, duration);
        uint256 totalReturn = stakeInfo.amount + reward;

        // CEI pattern: effects before external interaction
        uint256 stakedAmount = stakeInfo.amount;
        delete stakes[msg.sender][tierId];

        balanceOf[msg.sender] += totalReturn;

        emit Unstaked(msg.sender, stakedAmount, reward);
        emit Transfer(address(this), msg.sender, totalReturn);
    }

    function calculateReward(uint256 amount, uint256 tierId, uint256 duration)
        public view returns (uint256)
    {
        StakingInfo memory tier = stakingTiers[tierId];
        require(tier.duration > 0, "Invalid tier");
        // Reward = amount * APY * duration / (365 days * 10000)
        // APY is in basis points (e.g., 800 = 8%)
        return (amount * tier.apy * duration) / (365 days * 10000);
    }

    // ----- Admin Functions -----

    function setOracle(address newOracle) external onlySteward {
        require(newOracle != address(0), "Oracle cannot be zero address");
        oracle = newOracle;
        emit OracleUpdated(newOracle);
    }

    // ----- View Functions -----

    function totalMinted() external view returns (uint256) {
        return _totalMinted;
    }

    function totalBurned() external view returns (uint256) {
        return _totalBurned;
    }

    function getStakeInfo(address user, uint256 tierId) external view returns (StakeInfo memory) {
        return stakes[user][tierId];
    }
}
