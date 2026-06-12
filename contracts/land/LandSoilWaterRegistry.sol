// contracts/land/LandSoilWaterRegistry.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title LandSoilWaterRegistry
 * @notice Registry contract for storing summarized and validated land & soil-water analyses.
 *         Only authorized registrar accounts (backend services / admins) can register new records.
 *         The contract stores compact numeric summaries and metadata hashes to keep gas costs low.
 */
contract LandSoilWaterRegistry is AccessControl {
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");

    struct AnalysisRecord {
        bytes32 analysisIdHash;      // hash of internal analysis ID
        bytes32 userIdHash;          // hash of user identifier
        bytes32 landUnitIdHash;      // hash of land unit identifier
        uint8 scenarioType;          // 0: baseline, 1: management
        int32 periodStartYear;       // e.g., 2024
        int32 periodEndYear;         // e.g., 2030
        int32 runoffMmAvgTimes10;    // mm * 10
        int32 soilLossTHaAvgTimes10; // t/ha * 10
        int32 swcMmAvgTimes10;       // mm * 10
        int32 erosionRiskIndexTimes1000; // [0,1000] representing [0.0,1.0]
        bytes32 metadataHash;        // hash of off-chain metadata (e.g., IPFS / HTTPS JSON)
        uint64 timestamp;            // block timestamp of registration
        address registrar;           // msg.sender that registered the record
    }

    // analysisIdHash => record
    mapping(bytes32 => AnalysisRecord) private _records;
    // simple list of ids for iteration in off-chain indexers
    bytes32[] private _recordIds;

    event AnalysisRegistered(
        bytes32 indexed analysisIdHash,
        bytes32 indexed userIdHash,
        bytes32 indexed landUnitIdHash,
        uint8 scenarioType,
        int32 periodStartYear,
        int32 periodEndYear,
        int32 runoffMmAvgTimes10,
        int32 soilLossTHaAvgTimes10,
        int32 swcMmAvgTimes10,
        int32 erosionRiskIndexTimes1000,
        bytes32 metadataHash,
        uint64 timestamp,
        address registrar
    );

    constructor(address admin) {
        require(admin != address(0), "admin is zero address");
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(REGISTRAR_ROLE, admin);
    }

    /**
     * @notice Register a new analysis summary. Can only be called by accounts with REGISTRAR_ROLE.
     * @dev Reverts if a record for the given analysisIdHash already exists.
     */
    function registerAnalysis(
        bytes32 analysisIdHash,
        bytes32 userIdHash,
        bytes32 landUnitIdHash,
        uint8 scenarioType,
        int32 periodStartYear,
        int32 periodEndYear,
        int32 runoffMmAvgTimes10,
        int32 soilLossTHaAvgTimes10,
        int32 swcMmAvgTimes10,
        int32 erosionRiskIndexTimes1000,
        bytes32 metadataHash
    ) external onlyRole(REGISTRAR_ROLE) {
        require(analysisIdHash != bytes32(0), "invalid analysisIdHash");
        require(userIdHash != bytes32(0), "invalid userIdHash");
        require(landUnitIdHash != bytes32(0), "invalid landUnitIdHash");
        require(metadataHash != bytes32(0), "invalid metadataHash");

        // must not overwrite existing record
        require(_records[analysisIdHash].timestamp == 0, "analysis already registered");

        AnalysisRecord memory record = AnalysisRecord({
            analysisIdHash: analysisIdHash,
            userIdHash: userIdHash,
            landUnitIdHash: landUnitIdHash,
            scenarioType: scenarioType,
            periodStartYear: periodStartYear,
            periodEndYear: periodEndYear,
            runoffMmAvgTimes10: runoffMmAvgTimes10,
            soilLossTHaAvgTimes10: soilLossTHaAvgTimes10,
            swcMmAvgTimes10: swcMmAvgTimes10,
            erosionRiskIndexTimes1000: erosionRiskIndexTimes1000,
            metadataHash: metadataHash,
            timestamp: uint64(block.timestamp),
            registrar: msg.sender
        });

        _records[analysisIdHash] = record;
        _recordIds.push(analysisIdHash);

        emit AnalysisRegistered(
            analysisIdHash,
            userIdHash,
            landUnitIdHash,
            scenarioType,
            periodStartYear,
            periodEndYear,
            runoffMmAvgTimes10,
            soilLossTHaAvgTimes10,
            swcMmAvgTimes10,
            erosionRiskIndexTimes1000,
            metadataHash,
            uint64(block.timestamp),
            msg.sender
        );
    }

    /**
     * @notice Returns true if a record exists for the given analysisIdHash.
     */
    function exists(bytes32 analysisIdHash) external view returns (bool) {
        return _records[analysisIdHash].timestamp != 0;
    }

    /**
     * @notice Get a full analysis record by its analysisIdHash.
     */
    function getAnalysis(bytes32 analysisIdHash) external view returns (AnalysisRecord memory) {
        AnalysisRecord memory record = _records[analysisIdHash];
        require(record.timestamp != 0, "record not found");
        return record;
    }

    /**
     * @notice Returns the total number of registered analysis records.
     * @dev Intended for off-chain indexing and monitoring.
     */
    function totalRecords() external view returns (uint256) {
        return _recordIds.length;
    }

    /**
     * @notice Returns analysisIdHash at a given index.
     * @dev Use together with totalRecords() for off-chain iteration.
     */
    function recordIdAt(uint256 index) external view returns (bytes32) {
        require(index < _recordIds.length, "index out of bounds");
        return _recordIds[index];
    }
}