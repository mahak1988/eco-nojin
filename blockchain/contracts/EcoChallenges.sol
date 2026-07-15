// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EcoChallenges {
    struct Challenge {
        string description;
        uint256 rewardAmount;
        uint256 startTime;
        uint256 endTime;
        bool active;
    }

    address public owner;
    uint256 public challengeCount;
    mapping(uint256 => Challenge) public challenges;
    mapping(address => mapping(uint256 => bool)) public submissions;

    event ChallengeCreated(uint256 indexed id, string description, uint256 reward);
    event ChallengeSubmitted(address indexed user, uint256 indexed challengeId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function createChallenge(string calldata _description, uint256 _rewardAmount, uint256 _durationDays) external onlyOwner {
        challengeCount++;
        challenges[challengeCount] = Challenge({
            description: _description,
            rewardAmount: _rewardAmount,
            startTime: block.timestamp,
            endTime: block.timestamp + (_durationDays * 1 days),
            active: true
        });
        emit ChallengeCreated(challengeCount, _description, _rewardAmount);
    }

    function submitChallenge(uint256 _challengeId) external {
        Challenge storage ch = challenges[_challengeId];
        require(ch.active, "Challenge not active");
        require(block.timestamp <= ch.endTime, "Challenge ended");
        require(!submissions[msg.sender][_challengeId], "Already submitted");
        submissions[msg.sender][_challengeId] = true;
        emit ChallengeSubmitted(msg.sender, _challengeId);
        // Reward distribution will be handled off-chain or via another contract
    }
}
