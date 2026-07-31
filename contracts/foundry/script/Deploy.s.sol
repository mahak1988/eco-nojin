// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console2} from "forge-std/Script.sol";
import {EcoCoin} from "../src/EcoCoin.sol";
import {BucketTreasury} from "../src/BucketTreasury.sol";
import {ImpactClaimRegistry} from "../src/ImpactClaimRegistry.sol";
import {ImpactRewardEngine} from "../src/ImpactRewardEngine.sol";

/**
 * @notice Deployment order for pilot testnets (Amoy / Celo Sepolia).
 * Usage:
 *   forge script script/Deploy.s.sol:Deploy --rpc-url $RPC --broadcast --private-key $PK
 */
contract Deploy is Script {
    function run() external {
        address admin = vm.envOr("ADMIN_ADDRESS", msg.sender);
        uint256 pk = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(pk);

        EcoCoin eco = new EcoCoin(admin);
        BucketTreasury treasury = new BucketTreasury(admin);
        ImpactClaimRegistry registry = new ImpactClaimRegistry(admin);
        ImpactRewardEngine engine =
            new ImpactRewardEngine(admin, address(eco), address(treasury), address(registry));

        // Wire roles
        bytes32 MINTER = eco.MINTER_ROLE();
        eco.grantRole(MINTER, address(engine));

        treasury.grantRole(treasury.ENGINE_ROLE(), address(engine));
        registry.grantRole(registry.ATTESTER_ROLE(), address(engine));

        vm.stopBroadcast();

        console2.log("EcoCoin", address(eco));
        console2.log("BucketTreasury", address(treasury));
        console2.log("ImpactClaimRegistry", address(registry));
        console2.log("ImpactRewardEngine", address(engine));
        console2.log("Admin", admin);
    }
}
