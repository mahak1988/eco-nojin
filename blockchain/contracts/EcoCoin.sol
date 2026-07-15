// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract EcoCoin is ERC20, Ownable {
    mapping(address => uint256) public lastRewardTime;

    event TokensMinted(address indexed to, uint256 amount);
    event RewardDistributed(address indexed to, uint256 amount);

    constructor() ERC20("EcoCoin", "ECO") Ownable(msg.sender) {
        _mint(msg.sender, 1000000 * 10 ** decimals()); // initial supply
    }

    function mint(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "Invalid address");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    function reward(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "Invalid address");
        require(block.timestamp >= lastRewardTime[to] + 1 days, "Reward already given today");
        _mint(to, amount);
        lastRewardTime[to] = block.timestamp;
        emit RewardDistributed(to, amount);
    }
}
