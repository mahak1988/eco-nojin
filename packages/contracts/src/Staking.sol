// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title EcoStaking
 * @dev Staking contract for EcoCoin with governance power
 */
contract EcoStaking is ReentrancyGuard {
    
    IERC20 public ecoCoin;
    
    struct Stake {
        uint256 amount;
        uint256 timestamp;
        uint256 unlockTime;
    }
    
    mapping(address => Stake) public stakes;
    mapping(address => uint256) public governancePower;
    
    uint256 public totalStaked;
    uint256 public constant MIN_STAKE_DURATION = 30 days;
    uint256 public constant MAX_STAKE_DURATION = 365 days;
    uint256 public constant REWARD_RATE = 5; // 5% APY
    
    event Staked(address indexed user, uint256 amount, uint256 duration);
    event Unstaked(address indexed user, uint256 amount, uint256 reward);
    event GovernancePowerUpdated(address indexed user, uint256 power);
    
    constructor(address _ecoCoin) {
        ecoCoin = IERC20(_ecoCoin);
    }
    
    /**
     * @dev Stake EcoCoins for governance power and rewards
     */
    function stake(uint256 amount, uint256 duration) external nonReentrant {
        require(amount > 0, "Amount must be > 0");
        require(duration >= MIN_STAKE_DURATION, "Duration too short");
        require(duration <= MAX_STAKE_DURATION, "Duration too long");
        require(ecoCoin.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        // If already staked, calculate rewards first
        if (stakes[msg.sender].amount > 0) {
            uint256 reward = calculateReward(msg.sender);
            if (reward > 0) {
                ecoCoin.transfer(msg.sender, reward);
            }
        }
        
        uint256 unlockTime = block.timestamp + duration;
        stakes[msg.sender] = Stake(amount, block.timestamp, unlockTime);
        
        totalStaked += amount;
        
        // Update governance power
        updateGovernancePower(msg.sender);
        
        emit Staked(msg.sender, amount, duration);
    }
    
    /**
     * @dev Unstake EcoCoins after lock period
     */
    function unstake() external nonReentrant {
        Stake storage userStake = stakes[msg.sender];
        require(userStake.amount > 0, "No stake");
        require(block.timestamp >= userStake.unlockTime, "Still locked");
        
        uint256 amount = userStake.amount;
        uint256 reward = calculateReward(msg.sender);
        
        totalStaked -= amount;
        delete stakes[msg.sender];
        
        // Update governance power
        updateGovernancePower(msg.sender);
        
        // Transfer stake + reward
        ecoCoin.transfer(msg.sender, amount + reward);
        
        emit Unstaked(msg.sender, amount, reward);
    }
    
    /**
     * @dev Calculate staking reward
     */
    function calculateReward(address user) public view returns (uint256) {
        Stake storage userStake = stakes[user];
        if (userStake.amount == 0) return 0;
        
        uint256 duration = block.timestamp - userStake.timestamp;
        uint256 annualReward = (userStake.amount * REWARD_RATE) / 100;
        return (annualReward * duration) / 365 days;
    }
    
    /**
     * @dev Update governance power based on stake
     */
    function updateGovernancePower(address user) internal {
        uint256 power = stakes[user].amount;
        governancePower[user] = power;
        emit GovernancePowerUpdated(user, power);
    }
    
    /**
     * @dev Get user's governance power
     */
    function getGovernancePower(address user) external view returns (uint256) {
        return governancePower[user];
    }
}
