// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ModelValidation
 * @notice On-chain validation of scientific model results
 * @dev Stores validation metrics and verification proofs
 */
contract ModelValidation {
    struct ValidationResult {
        uint256 id;
        string modelName;
        address validator;
        uint256 timestamp;
        float nse;
        float r2;
        float pbias;
        float kge;
        string rating;
        bytes32 dataHash;
        bool verified;
    }
    
    struct ModelRegistration {
        string name;
        string organization;
        string version;
        address owner;
        bool isActive;
    }
    
    uint256 public validationCount;
    mapping(uint256 => ValidationResult) public validations;
    mapping(string => ModelRegistration) public models;
    mapping(address => uint256[]) public validatorResults;
    
    event ModelRegistered(string name, address owner);
    event ValidationSubmitted(uint256 id, string modelName, address validator);
    event ValidationVerified(uint256 id, address verifier);
    
    modifier onlyModelOwner(string memory modelName) {
        require(models[modelName].owner == msg.sender, "Not model owner");
        _;
    }
    
    function registerModel(
        string memory name,
        string memory organization,
        string memory version
    ) external {
        require(models[name].owner == address(0), "Model already registered");
        
        models[name] = ModelRegistration({
            name: name,
            organization: organization,
            version: version,
            owner: msg.sender,
            isActive: true
        });
        
        emit ModelRegistered(name, msg.sender);
    }
    
    function submitValidation(
        string memory modelName,
        float nse,
        float r2,
        float pbias,
        float kge,
        string memory rating,
        bytes32 dataHash
    ) external returns (uint256) {
        require(models[modelName].isActive, "Model not active");
        
        validationCount++;
        
        validations[validationCount] = ValidationResult({
            id: validationCount,
            modelName: modelName,
            validator: msg.sender,
            timestamp: block.timestamp,
            nse: nse,
            r2: r2,
            pbias: pbias,
            kge: kge,
            rating: rating,
            dataHash: dataHash,
            verified: false
        });
        
        validatorResults[msg.sender].push(validationCount);
        
        emit ValidationSubmitted(validationCount, modelName, msg.sender);
        
        return validationCount;
    }
    
    function verifyValidation(uint256 validationId) external {
        ValidationResult storage v = validations[validationId];
        require(v.id != 0, "Validation not found");
        require(!v.verified, "Already verified");
        
        // Auto-verify if metrics meet standards
        if (v.nse > 0.5 && abs(v.pbias) < 25) {
            v.verified = true;
            emit ValidationVerified(validationId, msg.sender);
        }
    }
    
    function getValidation(uint256 id) external view returns (ValidationResult memory) {
        return validations[id];
    }
    
    function getValidatorResults(address validator) external view returns (uint256[] memory) {
        return validatorResults[validator];
    }
    
    function abs(float x) internal pure returns (float) {
        return x < 0 ? -x : x;
    }
}
