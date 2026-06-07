#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contracts Builder Module
Generates Solidity smart contracts and secure Hardhat configuration.
"""
import logging

from .base_builder import CONTRACTS_DIR, BaseBuilder

logger = logging.getLogger(__name__)


class ContractsBuilder(BaseBuilder):
    def __init__(self):
        super().__init__("contracts")

    def build(self):
        logger.info("\n" + "=" * 70)
        logger.info("📜 Building Smart Contracts")
        logger.info("=" * 70)

        self._create_seed_token()
        self._create_gaia_certificate()
        self._create_hardhat_config()
        return self.get_stats()

    def _create_seed_token(self):
        content = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SeedToken is ERC20, Ownable {
    constructor() ERC20("Seed Token", "SEED") Ownable(msg.sender) {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
    
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}
"""
        path = CONTRACTS_DIR / "contracts" / "SeedToken.sol"
        self.write(path, content)

    def _create_gaia_certificate(self):
        content = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract GaiaCertificate is ERC721 {
    uint256 private _nextTokenId;
    
    constructor() ERC721("Gaia Certificate", "GAIA") {}
    
    function mint(address to) public returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        return tokenId;
    }
}
"""
        path = CONTRACTS_DIR / "contracts" / "GaiaCertificate.sol"
        self.write(path, content)

    def _create_hardhat_config(self):
        # تقویت امنیت: ارائه الگوی امن برای استفاده از متغیرهای محیطی
        content = """require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    localhost: { 
      url: "http://127.0.0.1:8545" 
    },
    // ⚠️ SECURITY NOTE: 
    // هرگز کلیدهای خصوصی یا RPC URL ها را در این فایل hardcode نکنید.
    // همیشه از متغیرهای محیطی در فایل .env استفاده کنید.
    // مثال:
    // sepolia: {
    //   url: process.env.SEPOLIA_RPC_URL || "",
    //   accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    // }
  }
};
"""
        path = CONTRACTS_DIR / "hardhat.config.js"
        self.write(path, content)
