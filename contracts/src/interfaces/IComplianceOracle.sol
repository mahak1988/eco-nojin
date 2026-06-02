// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;
interface IComplianceOracle {
    function checkTransfer(address from, address to, uint256 amount) external view returns (bool, string memory);
}
