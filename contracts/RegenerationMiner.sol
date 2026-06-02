// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title RegenerationMiner
 * @dev Smart Contract برای استخراج SEED از طریق فعالیت‌های بازسازی اکوسیستمی
 * هر فعالیت تأیید شده یک Proof منحصربه‌فرد تولید می‌کند
 */
contract RegenerationMiner is Ownable, ReentrancyGuard {
    using ECDSA for bytes32;

    // ========================================================================
    // State Variables
    // ========================================================================
    
    IERC20 public seedToken;
    IERC721 public certificateNFT;
    
    address public oracleAddress;
    
    uint256 public totalProofs;
    uint256 public totalCarbonMilliKg;
    uint256 public totalSeedMinted;
    
    // نرخ تبدیل: 1 kg CO2 = 100 SEED (0.1 SEED per gram)
    uint256 public constant SEED_PER_MILLI_KG = 100;
    
    struct Proof {
        address miner;
        string activityType;
        uint256 carbonMilliKg;
        uint256 confidenceBps;
        bytes32 evidenceHash;
        uint256 timestamp;
        uint256 seedEarned;
        bool exists;
    }
    
    struct MinerStats {
        uint256 totalProofs;
        uint256 totalCarbonMilliKg;
        uint256 totalSeedEarned;
    }
    
    mapping(bytes32 => Proof) public proofs;
    mapping(address => MinerStats) public minerStats;
    mapping(bytes32 => bool) public usedEvidenceHashes;
    
    // ========================================================================
    // Events
    // ========================================================================
    
    event ProofSubmitted(
        bytes32 indexed proofId,
        address indexed miner,
        string activityType,
        uint256 carbonMilliKg,
        uint256 seedEarned,
        bytes32 evidenceHash
    );
    
    event OracleUpdated(address indexed oldOracle, address indexed newOracle);
    
    // ========================================================================
    // Constructor
    // ========================================================================
    
    constructor(
        address _seedToken,
        address _certificateNFT,
        address _oracle
    ) Ownable(msg.sender) {
        require(_seedToken != address(0), "Invalid seed token");
        require(_certificateNFT != address(0), "Invalid NFT");
        require(_oracle != address(0), "Invalid oracle");
        
        seedToken = IERC20(_seedToken);
        certificateNFT = IERC721(_certificateNFT);
        oracleAddress = _oracle;
    }
    
    // ========================================================================
    // Modifiers
    // ========================================================================
    
    modifier onlyOracle() {
        require(msg.sender == oracleAddress, "Only oracle");
        _;
    }
    
    // ========================================================================
    // Core Functions
    // ========================================================================
    
    /**
     * @dev ثبت یک Proof جدید توسط Oracle
     */
    function submitVerifiedProof(
        address miner,
        string calldata activityType,
        uint256 carbonMilliKg,
        uint256 confidenceBps,
        bytes32 evidenceHash,
        bytes calldata oracleSignature
    ) external onlyOracle nonReentrant returns (bytes32 proofId) {
        require(miner != address(0), "Invalid miner");
        require(carbonMilliKg > 0, "No carbon");
        require(confidenceBps >= 5000, "Confidence too low"); // حداقل 50%
        require(!usedEvidenceHashes[evidenceHash], "Evidence reused");
        
        // ایجاد proofId
        proofId = keccak256(
            abi.encodePacked(
                miner,
                activityType,
                carbonMilliKg,
                block.timestamp,
                block.number
            )
        );
        
        require(!proofs[proofId].exists, "Proof exists");
        
        // تأیید امضای Oracle
        bytes32 messageHash = keccak256(
            abi.encodePacked(
                proofId,
                miner,
                carbonMilliKg,
                evidenceHash
            )
        );
        bytes32 ethSignedHash = messageHash.toEthSignedMessageHash();
        address signer = ethSignedHash.recover(oracleSignature);
        require(signer == oracleAddress, "Invalid signature");
        
        // محاسبه SEED
        uint256 seedEarned = (carbonMilliKg * SEED_PER_MILLI_KG * confidenceBps) / 10000;
        
        // ذخیره Proof
        proofs[proofId] = Proof({
            miner: miner,
            activityType: activityType,
            carbonMilliKg: carbonMilliKg,
            confidenceBps: confidenceBps,
            evidenceHash: evidenceHash,
            timestamp: block.timestamp,
            seedEarned: seedEarned,
            exists: true
        });
        
        usedEvidenceHashes[evidenceHash] = true;
        
        // به‌روزرسانی آمار
        totalProofs++;
        totalCarbonMilliKg += carbonMilliKg;
        totalSeedMinted += seedEarned;
        
        MinerStats storage stats = minerStats[miner];
        stats.totalProofs++;
        stats.totalCarbonMilliKg += carbonMilliKg;
        stats.totalSeedEarned += seedEarned;
        
        emit ProofSubmitted(
            proofId,
            miner,
            activityType,
            carbonMilliKg,
            seedEarned,
            evidenceHash
        );
        
        return proofId;
    }
    
    /**
     * @dev دریافت آمار یک miner
     */
    function getMinerStats(address miner) external view returns (
        uint256 totalProofs_,
        uint256 totalCarbonMilliKg_,
        uint256 totalSeedEarned_
    ) {
        MinerStats memory stats = minerStats[miner];
        return (stats.totalProofs, stats.totalCarbonMilliKg, stats.totalSeedEarned);
    }
    
    /**
     * @dev دریافت جزئیات Proof
     */
    function getProof(bytes32 proofId) external view returns (
        address miner,
        string memory activityType,
        uint256 carbonMilliKg,
        uint256 confidenceBps,
        bytes32 evidenceHash,
        uint256 timestamp,
        uint256 seedEarned
    ) {
        require(proofs[proofId].exists, "Proof not found");
        Proof memory p = proofs[proofId];
        return (
            p.miner,
            p.activityType,
            p.carbonMilliKg,
            p.confidenceBps,
            p.evidenceHash,
            p.timestamp,
            p.seedEarned
        );
    }
    
    // ========================================================================
    // Admin Functions
    // ========================================================================
    
    function updateOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Invalid oracle");
        emit OracleUpdated(oracleAddress, newOracle);
        oracleAddress = newOracle;
    }
    
    // ========================================================================
    // Emergency
    // ========================================================================
    
    function emergencyPause() external onlyOwner {
        // پیاده‌سازی pause mechanism
    }
}