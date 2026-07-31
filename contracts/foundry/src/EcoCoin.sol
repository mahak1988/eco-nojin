// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Pausable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title EcoCoin
 * @notice Educational–Scientific–Incentive token for ecosystem restoration.
 *         Hard cap 1_000_000_000 ECO. No energy used for minting.
 *         Only addresses with MINTER_ROLE may mint (ImpactRewardEngine).
 */
contract EcoCoin is ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice Immutable hard cap: 1 billion tokens (18 decimals)
    uint256 public constant CAP = 1_000_000_000 * 10 ** 18;

    error CapExceeded(uint256 requested, uint256 available);

    constructor(address admin) ERC20("EcoCoin", "ECO") {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, admin); // temporary; transfer to RewardEngine after deploy
        _grantRole(PAUSER_ROLE, admin);
    }

    /**
     * @notice Mint tokens. Respects hard CAP. Only MINTER_ROLE.
     */
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        if (totalSupply() + amount > CAP) {
            revert CapExceeded(amount, CAP - totalSupply());
        }
        _mint(to, amount);
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function remainingCap() external view returns (uint256) {
        return CAP - totalSupply();
    }

    // ----- required overrides -----
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Pausable)
    {
        super._update(from, to, value);
    }
}
