// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IEcoCoin {
    function mint(address to, uint256 amount) external;
    function CAP() external view returns (uint256);
    function remainingCap() external view returns (uint256);
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
}
