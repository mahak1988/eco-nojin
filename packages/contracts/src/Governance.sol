// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Staking.sol";

/**
 * @title EcoGovernance
 * @dev Governance contract for Eco Nozhin DAO
 */
contract EcoGovernance {
    
    EcoStaking public staking;
    
    struct Proposal {
        uint256 id;
        string description;
        address proposer;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 startTime;
        uint256 endTime;
        bool executed;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    
    uint256 public proposalCount;
    uint256 public constant VOTING_DURATION = 7 days;
    uint256 public constant QUORUM = 1000 * 10**18; // 1000 tokens
    
    event ProposalCreated(uint256 indexed id, address indexed proposer, string description);
    event Voted(uint256 indexed proposalId, address indexed voter, bool support);
    event ProposalExecuted(uint256 indexed id);
    
    constructor(address _staking) {
        staking = EcoStaking(_staking);
    }
    
    /**
     * @dev Create a new proposal
     */
    function createProposal(string calldata description) external {
        require(staking.getGovernancePower(msg.sender) > 0, "No governance power");
        
        proposalCount++;
        proposals[proposalCount] = Proposal({
            id: proposalCount,
            description: description,
            proposer: msg.sender,
            votesFor: 0,
            votesAgainst: 0,
            startTime: block.timestamp,
            endTime: block.timestamp + VOTING_DURATION,
            executed: false
        });
        
        emit ProposalCreated(proposalCount, msg.sender, description);
    }
    
    /**
     * @dev Vote on a proposal
     */
    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        
        uint256 votingPower = staking.getGovernancePower(msg.sender);
        require(votingPower > 0, "No voting power");
        
        hasVoted[proposalId][msg.sender] = true;
        
        if (support) {
            proposal.votesFor += votingPower;
        } else {
            proposal.votesAgainst += votingPower;
        }
        
        emit Voted(proposalId, msg.sender, support);
    }
    
    /**
     * @dev Execute a passed proposal
     */
    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp > proposal.endTime, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(proposal.votesFor > proposal.votesAgainst, "Not passed");
        require(proposal.votesFor >= QUORUM, "Quorum not reached");
        
        proposal.executed = true;
        
        // Execute proposal logic here
        // This would call different functions based on proposal type
        
        emit ProposalExecuted(proposalId);
    }
    
    /**
     * @dev Check if proposal passed
     */
    function isProposalPassed(uint256 proposalId) external view returns (bool) {
        Proposal storage proposal = proposals[proposalId];
        return proposal.votesFor > proposal.votesAgainst && 
               proposal.votesFor >= QUORUM;
    }
}
