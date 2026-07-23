// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title VerificationOracle - Verifies ecological credits and data
 * @notice Bridges off-chain environmental data to on-chain tokens
 * @dev Access-controlled project registration and verification system
 */
contract VerificationOracle {
    enum CreditType {
        TREE_PLANTING,
        SOIL_CARBON,
        WATER_CONSERVATION,
        BIODIVERSITY,
        RENEWABLE_ENERGY
    }

    struct Project {
        uint256 id;
        string name;
        string region;
        string ipfsHash;
        uint256 creditType;
        uint256 startDate;
        uint256 endDate;
        bool verified;
    }

    struct Verification {
        address verifier;
        uint256 timestamp;
        bytes32 dataHash;
        uint256 value;
        bool valid;
    }

    mapping(uint256 => Project) public projects;
    mapping(uint256 => Verification[]) public verifications;
    mapping(address => bool) public verifiers;
    mapping(uint256 => mapping(address => bool)) public projectVerified; // projectId => verifier => verified

    uint256 public projectCount;
    address public steward;

    event ProjectRegistered(uint256 indexed id, string name, uint256 creditType);
    event Verified(uint256 indexed projectId, address indexed verifier, uint256 value);
    event VerifierAdded(address indexed verifier);
    event VerifierRemoved(address indexed verifier);

    modifier onlySteward() {
        require(msg.sender == steward, "Not steward");
        _;
    }

    modifier onlyVerifier() {
        require(verifiers[msg.sender], "Not verifier");
        _;
    }

    constructor() {
        require(msg.sender != address(0), "Zero address steward");
        steward = msg.sender;
    }

    function registerProject(
        string calldata name,
        string calldata region,
        string calldata ipfsHash,
        uint256 creditType
    ) external onlySteward returns (uint256) {
        require(bytes(name).length > 0, "Project name required");
        require(bytes(region).length > 0, "Region required");
        require(bytes(ipfsHash).length > 0, "IPFS hash required");
        require(creditType <= uint256(type(CreditType).max), "Invalid credit type");

        projectCount++;
        projects[projectCount] = Project({
            id: projectCount,
            name: name,
            region: region,
            ipfsHash: ipfsHash,
            creditType: creditType,
            startDate: block.timestamp,
            endDate: 0,
            verified: false
        });

        emit ProjectRegistered(projectCount, name, creditType);
        return projectCount;
    }

    function verify(
        uint256 projectId,
        uint256 value,
        bytes32 dataHash
    ) external onlyVerifier {
        require(projectId > 0 && projectId <= projectCount, "Project not found");
        require(!projectVerified[projectId][msg.sender], "Already verified by this verifier");
        require(value > 0, "Verification value must be positive");
        require(dataHash != bytes32(0), "Data hash required");

        Project storage project = projects[projectId];
        require(project.id > 0, "Project not found");

        project.verified = true;
        project.endDate = block.timestamp;
        projectVerified[projectId][msg.sender] = true;

        verifications[projectId].push(Verification({
            verifier: msg.sender,
            timestamp: block.timestamp,
            dataHash: dataHash,
            value: value,
            valid: true
        }));

        emit Verified(projectId, msg.sender, value);
    }

    function addVerifier(address verifier) external onlySteward {
        require(verifier != address(0), "Verifier cannot be zero address");
        require(!verifiers[verifier], "Already a verifier");
        verifiers[verifier] = true;
        emit VerifierAdded(verifier);
    }

    function removeVerifier(address verifier) external onlySteward {
        require(verifier != address(0), "Verifier cannot be zero address");
        require(verifiers[verifier], "Not a verifier");
        verifiers[verifier] = false;
        emit VerifierRemoved(verifier);
    }

    function getProject(uint256 projectId) external view returns (Project memory) {
        require(projectId > 0 && projectId <= projectCount, "Project not found");
        return projects[projectId];
    }

    function getVerifications(uint256 projectId)
        external view returns (Verification[] memory)
    {
        require(projectId > 0 && projectId <= projectCount, "Project not found");
        return verifications[projectId];
    }

    function calculateCredits(
        uint256 /* projectId */,
        uint256 value,
        bytes32 /* dataHash */
    ) public pure returns (uint256) {
        require(value > 0, "Value must be positive");
        // Simplified credit calculation
        // In production, would use actual formulas based on credit type
        return value * 10;
    }
}
