require("@nomicfoundation/hardhat-toolbox");
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
