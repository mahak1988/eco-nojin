# استقرار قراردادها (Deployment)

## روش ۱: Remix IDE (پیشنهاد برای توسعه)
1. فایل‌های `contracts/EcoCoin.sol` و `contracts/EcoChallenges.sol` را در Remix باز کنید.
2. کامپایل با Solidity 0.8.20.
3. استقرار روی شبکه دلخواه (Polygon Mumbai Testnet یا محلی Ganache).

## روش ۲: Hardhat (پیشرفته)
1. در پوشه blockchain اجرا کنید:
   pnpm init -y
   pnpm add --save-dev hardhat @openzeppelin/contracts
2. npx hardhat init
3. قراردادها را به contracts/ منتقل کنید.
4. npx hardhat compile
5. اسکریپت deploy بنویسید.

آدرس قراردادهای مستقرشده را در فایل .env قرار دهید.
