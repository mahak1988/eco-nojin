// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title GaiaCertificate (Living NFT)
 * @dev NFTs that grow as the real ecosystem grows
 */
contract GaiaCertificate is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    address public minerContract;

    struct Certificate {
        string activityType;
        uint256 carbonMilliKg;
        uint256 plantedAt;
        uint256 lastUpdate;
        uint8 growthStage;  // 0=seedling, 1=sapling, 2=young, 3=mature, 4=old
        string evidenceHash;
    }

    mapping(uint256 => Certificate) public certificates;

    event CertificateMinted(uint256 indexed tokenId, address indexed owner, string activityType, uint256 carbonMilliKg);
    event CertificateUpdated(uint256 indexed tokenId, uint256 newCarbonMilliKg, uint8 newGrowthStage);

    constructor(address _minerContract) ERC721("Gaia Certificate", "GAIA") Ownable(msg.sender) {
        minerContract = _minerContract;
    }

    modifier onlyMinerOrOwner() {
        require(msg.sender == minerContract || msg.sender == owner(), "Not authorized");
        _;
    }

    function mintCertificate(address to, string calldata activityType, uint256 carbonMilliKg, string calldata tokenURI, string calldata evidenceHash)
        external onlyMinerOrOwner returns (uint256) {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        _safeMint(to, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        certificates[newTokenId] = Certificate({
            activityType: activityType,
            carbonMilliKg: carbonMilliKg,
            plantedAt: block.timestamp,
            lastUpdate: block.timestamp,
            growthStage: 0,
            evidenceHash: evidenceHash
        });
        emit CertificateMinted(newTokenId, to, activityType, carbonMilliKg);
        return newTokenId;
    }

    function updateCertificate(uint256 tokenId, uint256 newCarbonMilliKg, uint8 newGrowthStage, string calldata newTokenURI)
        external onlyMinerOrOwner {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        Certificate storage cert = certificates[tokenId];
        cert.carbonMilliKg = newCarbonMilliKg;
        cert.growthStage = newGrowthStage;
        cert.lastUpdate = block.timestamp;
        if (bytes(newTokenURI).length > 0) _setTokenURI(tokenId, newTokenURI);
        emit CertificateUpdated(tokenId, newCarbonMilliKg, newGrowthStage);
    }

    function getCertificate(uint256 tokenId) external view returns (
        address owner, string memory activityType, uint256 carbonMilliKg,
        uint256 plantedAt, uint256 lastUpdate, uint8 growthStage, string memory evidenceHash
    ) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        Certificate memory cert = certificates[tokenId];
        return (ownerOf(tokenId), cert.activityType, cert.carbonMilliKg, cert.plantedAt, cert.lastUpdate, cert.growthStage, cert.evidenceHash);
    }

    function totalSupply() public view returns (uint256) { return _tokenIds.current(); }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) { super._burn(tokenId); }
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) { return super.tokenURI(tokenId); }
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) { return super.supportsInterface(interfaceId); }
}
