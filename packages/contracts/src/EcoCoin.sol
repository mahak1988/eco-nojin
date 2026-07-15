// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title EcoCoin
 * @dev ERC-20 token for Eco Nozhin ecosystem
 * Backed by verified ecological services (carbon, water, biodiversity)
 */
contract EcoCoin is ERC20, ERC20Burnable, Ownable, Pausable {
    
    uint256 public constant MAX_SUPPLY = 100_000_000 * 10**18; // 100M tokens
    uint256 public totalMinted;
    
    // Ecological backing (1 ECO = 1 ton CO2 equivalent)
    uint256 public ecologicalBacking; // in tons CO2
    
    // Oracle address for ecological verification
    address public ecologicalOracle;
    
    event TokensMinted(address indexed to, uint256 amount, string reason);
    event TokensBurned(address indexed from, uint256 amount, string reason);
    event EcologicalBackingUpdated(uint256 newBacking);
    
    constructor() ERC20("EcoCoin", "ECO") {
        ecologicalOracle = msg.sender;
    }
    
    /**
     * @dev Mint tokens based on ecological action
     * Only callable by ecological oracle
     */
    function mint(address to, uint256 amount, string calldata reason) external onlyOracle {
        require(totalMinted + amount <= MAX_SUPPLY, "Exceeds max supply");
        
        totalMinted += amount;
        _mint(to, amount);
        
        emit TokensMinted(to, amount, reason);
    }
    
    /**
     * @dev Burn tokens for ecological violation
     */
    function burnWithReason(address from, uint256 amount, string calldata reason) external onlyOracle {
        _burn(from, amount);
        emit TokensBurned(from, amount, reason);
    }
    
    /**
     * @dev Update ecological backing (verified by oracle)
     */
    function updateEcologicalBacking(uint256 newBacking) external onlyOracle {
        ecologicalBacking = newBacking;
        emit EcologicalBackingUpdated(newBacking);
    }
    
    /**
     * @dev Set ecological oracle address
     */
    function setEcologicalOracle(address newOracle) external onlyOwner {
        ecologicalOracle = newOracle;
    }
    
    /**
     * @dev Pause all transfers
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause all transfers
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Check if address is oracle
     */
    modifier onlyOracle() {
        require(msg.sender == ecologicalOracle, "Not authorized");
        _;
    }
    
    /**
     * @dev Override _beforeTokenTransfer to enforce pause
     */
    function _beforeTokenTransfer(address from, address to, uint256 amount)
        internal
        override
        whenNotPaused
    {
        super._beforeTokenTransfer(from, to, amount);
    }
}
