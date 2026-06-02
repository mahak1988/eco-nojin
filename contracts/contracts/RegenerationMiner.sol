// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface ISeedToken { function mint(address to, uint256 amount) external; }
interface IGaiaCert { function mintCertificate(address to, string calldata activity, uint256 carbon, string calldata uri, string calldata evidence) external returns (uint256); }

contract RegenerationMiner is Ownable, ReentrancyGuard {
    using ECDSA for bytes32;

    ISeedToken public seedToken;
    IGaiaCert public gaiaCert;
    address public oracleAddress;
    uint256 public constant SEED_PER_MILLI_KG = 100;

    struct Proof {
        address miner;
        string activityType;
        uint256 carbonMilliKg;
        uint256 confidenceBps;
        bytes32 evidenceHash;
        uint256 timestamp;
        uint256 seedEarned;
        uint256 tokenId;
        bool exists;
    }

    mapping(bytes32 => Proof) public proofs;
    mapping(address => uint256) public totalCarbonByMiner;
    uint256 public totalProofs;
    uint256 public totalCarbonMilliKg;

    event ProofSubmitted(bytes32 indexed proofId, address indexed miner, uint256 carbonMilliKg, uint256 seedEarned, uint256 tokenId);

    constructor(address _seed, address _cert, address _oracle) Ownable(msg.sender) {
        seedToken = ISeedToken(_seed);
        gaiaCert = IGaiaCert(_cert);
        oracleAddress = _oracle;
    }

    modifier onlyOracle() { require(msg.sender == oracleAddress, "Only oracle"); _; }

    function submitVerifiedProof(
        address miner, string calldata activityType, uint256 carbonMilliKg,
        uint256 confidenceBps, bytes32 evidenceHash, bytes calldata signature
    ) external onlyOracle nonReentrant returns (bytes32 proofId, uint256 tokenId) {
        require(miner != address(0), "Invalid miner");
        require(carbonMilliKg > 0, "No carbon");
        require(confidenceBps >= 5000, "Low confidence");

        proofId = keccak256(abi.encodePacked(miner, activityType, carbonMilliKg, block.timestamp, block.number));
        require(!proofs[proofId].exists, "Proof exists");

        bytes32 msgHash = keccak256(abi.encodePacked(proofId, miner, carbonMilliKg, evidenceHash));
        address signer = msgHash.toEthSignedMessageHash().recover(signature);
        require(signer == oracleAddress, "Invalid signature");

        uint256 seedEarned = (carbonMilliKg * SEED_PER_MILLI_KG * confidenceBps) / 10000;
        seedToken.mint(miner, seedEarned);
        tokenId = gaiaCert.mintCertificate(miner, activityType, carbonMilliKg, "", string(abi.encodePacked(evidenceHash)));

        proofs[proofId] = Proof({
            miner: miner, activityType: activityType, carbonMilliKg: carbonMilliKg,
            confidenceBps: confidenceBps, evidenceHash: evidenceHash, timestamp: block.timestamp,
            seedEarned: seedEarned, tokenId: tokenId, exists: true
        });

        totalProofs++;
        totalCarbonMilliKg += carbonMilliKg;
        totalCarbonByMiner[miner] += carbonMilliKg;

        emit ProofSubmitted(proofId, miner, carbonMilliKg, seedEarned, tokenId);
    }

    function updateOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Invalid oracle");
        oracleAddress = newOracle;
    }
}
