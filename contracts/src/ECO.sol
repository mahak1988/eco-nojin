// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ECO is ERC20, Ownable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 1e18;
    uint256 public constant BURN_RATE_BPS = 500;
    address public complianceOracle;
    event ComplianceCheck(address indexed user, bool passed, string reason);

    constructor() ERC20("Economugin Utility", "ECO") Ownable(msg.sender) {
        _mint(msg.sender, TOTAL_SUPPLY);
    }

    function _update(address from, address to, uint256 amount) internal override {
        if (amount > 0 && complianceOracle != address(0)) {
            (bool passed, string memory reason) = IComplianceOracle(complianceOracle).checkTransfer(from, to, amount);
            emit ComplianceCheck(from, passed, reason);
            require(passed, reason);
        }
        super._update(from, to, amount);
    }

    function _burnFee(uint256 amount) internal {
        uint256 burn = (amount * BURN_RATE_BPS) / 10000;
        if (burn > 0) _burn(msg.sender, burn);
    }

    function setComplianceOracle(address _oracle) external onlyOwner { complianceOracle = _oracle; }
    
    interface IComplianceOracle {
        function checkTransfer(address from, address to, uint256 amount) external view returns (bool, string memory);
    }
}
