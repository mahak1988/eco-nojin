// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NAR is ERC721, Ownable {
    ERC20 public rewardToken;
    mapping(uint256 => bool) public isSoulbound;
    mapping(address => uint256) public userToTokenId;
    uint256 public nextTokenId;

    constructor(ERC20 _rewardToken) ERC721("Economugin Governance", "NAR") Ownable(msg.sender) { rewardToken = _rewardToken; }

    function mintSoulbound(address to, string memory uri) external onlyOwner returns (uint256) {
        uint256 tid = nextTokenId++;
        _safeMint(to, tid);
        _setTokenURI(tid, uri);
        isSoulbound[tid] = true;
        userToTokenId[to] = tid;
        return tid;
    }

    function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
        require(!isSoulbound[tokenId], "NAR: Soulbound");
        return super._update(to, tokenId, auth);
    }

    function getVotingPower(address user) external view returns (uint256) {
        return (userToTokenId[user] != 0 && balanceOf(user) > 0) ? 100 : rewardToken.balanceOf(user) / 1e18;
    }
}
