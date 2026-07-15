// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title EcoTreasury
 * @dev Treasury contract for managing Eco Nozhin funds
 */
contract EcoTreasury is Ownable {
    
    IERC20 public ecoCoin;
    
    mapping(address => uint256) public allocations;
    
    uint256 public totalAllocated;
    
    event FundsAllocated(address indexed recipient, uint256 amount, string purpose);
    event FundsWithdrawn(address indexed recipient, uint256 amount);
    
    constructor(address _ecoCoin) {
        ecoCoin = IERC20(_ecoCoin);
    }
    
    /**
     * @dev Allocate funds to a recipient
     */
    function allocate(address recipient, uint256 amount, string calldata purpose) external onlyOwner {
        require(ecoCoin.balanceOf(address(this)) >= totalAllocated + amount, "Insufficient funds");
        
        allocations[recipient] += amount;
        totalAllocated += amount;
        
        emit FundsAllocated(recipient, amount, purpose);
    }
    
    /**
     * @dev Withdraw allocated funds
     */
    function withdraw() external {
        uint256 amount = allocations[msg.sender];
        require(amount > 0, "No allocation");
        
        allocations[msg.sender] = 0;
        totalAllocated -= amount;
        
        ecoCoin.transfer(msg.sender, amount);
        
        emit FundsWithdrawn(msg.sender, amount);
    }
    
    /**
     * @dev Get treasury balance
     */
    function getBalance() external view returns (uint256) {
        return ecoCoin.balanceOf(address(this));
    }
}
