# 📊 گزارش تحلیل EcoCoin

**تاریخ اسکن:** 2026-07-23T08:32:26.628663

**مسیر پروژه:** `D:\econojin.com`


## 📋 خلاصه

| معیار | مقدار |
|---|---|
| فایل‌های مرتبط با EcoCoin | 2762 |
| قراردادهای هوشمند | 6 |
| توابع قراردادها | 29 |
| API Endpoints | 77 |
| مدل‌های دیتابیس | 122 |
| کامپوننت‌های فرانت‌اند | 823 |
| وابستگی‌های بلاکچین | 5 |
| الگوهای امنیتی شناسایی‌شده | 18 |
| مشکلات احتمالی | 4 |

## 🏆 فایل‌های با بیشترین ارتباط

| رتبه | فایل | امتیاز | کلمات کلیدی |
|---|---|---|---|
| 1 | `__repo_sync_tmp__\apps\web\generate_batch2.py` | 395 | ecocoin, ECO, token, wallet, reward |
| 2 | `analyze_ecocoin.py` | 291 | ecocoin, eco_coin, eco-coin, ECO, token |
| 3 | `type_errors.json` | 291 | ecocoin, ECO, token, wallet, blockchain |
| 4 | `__repo_sync_tmp__\packages\lib\src\api\hooks\useEcoCoin.ts` | 139 | ecocoin, ECO, reward, transaction, filename_match |
| 5 | `packages\lib\src\api\hooks\useEcoCoin.ts` | 115 | ecocoin, ECO, reward, transaction, filename_match |
| 6 | `unified_audit.json` | 98 | ecocoin, ECO, wallet, blockchain, web3 |
| 7 | `__repo_sync_tmp__\packages\lib\src\api\api-types.ts` | 93 | ecocoin, ECO, token, wallet, carbon |
| 8 | `packages\lib\src\api\api-types.ts` | 93 | ecocoin, ECO, token, wallet, carbon |
| 9 | `packages\lib\src\api\types\ecocoin.types.ts` | 93 | ecocoin, ECO, token, wallet, mint |
| 10 | `__repo_sync_tmp__\apps\web\update_routes.py` | 92 | ecocoin, ECO, wallet, reward, carbon |

## 📜 قراردادهای هوشمند

### `contracts\EcoCoin.sol`

- **اندازه:** 4.26 KB
- **قراردادها:** EcoCoin
- **توابع:** 8
- **رویدادها:** 5
- **الگوهای امنیتی:**
  - ✅ Safe Arithmetic
  - ✅ Input Validation (require)
  - ✅ Event Logging
### `contracts\VerificationOracle.sol`

- **اندازه:** 3.44 KB
- **قراردادها:** VerificationOracle
- **توابع:** 7
- **رویدادها:** 4
- **الگوهای امنیتی:**
  - ✅ Safe Arithmetic
  - ✅ Input Validation (require)
  - ✅ Event Logging
### `repos\AgriSync\frontend\contracts\Marketplace.sol`

- **اندازه:** 1.43 KB
- **قراردادها:** Marketplace
- **توابع:** 3
- **رویدادها:** 2
- **الگوهای امنیتی:**
  - ✅ Safe Arithmetic
  - ✅ Input Validation (require)
  - ✅ Event Logging
- **مشکلات احتمالی:**
  - ⚠️  توابع public بدون access control
### `repos\AgriSync\frontend\contracts\StorageManagement.sol`

- **اندازه:** 1.73 KB
- **قراردادها:** StorageManagement
- **توابع:** 4
- **رویدادها:** 3
- **الگوهای امنیتی:**
  - ✅ Safe Arithmetic
  - ✅ Input Validation (require)
  - ✅ Event Logging
- **مشکلات احتمالی:**
  - ⚠️  توابع public بدون access control
### `repos\AgriSync\backend\blockchain\Marketplace.sol`

- **اندازه:** 1.43 KB
- **قراردادها:** Marketplace
- **توابع:** 3
- **رویدادها:** 2
- **الگوهای امنیتی:**
  - ✅ Safe Arithmetic
  - ✅ Input Validation (require)
  - ✅ Event Logging
- **مشکلات احتمالی:**
  - ⚠️  توابع public بدون access control
### `repos\AgriSync\backend\blockchain\StorageManagement.sol`

- **اندازه:** 1.73 KB
- **قراردادها:** StorageManagement
- **توابع:** 4
- **رویدادها:** 3
- **الگوهای امنیتی:**
  - ✅ Safe Arithmetic
  - ✅ Input Validation (require)
  - ✅ Event Logging
- **مشکلات احتمالی:**
  - ⚠️  توابع public بدون access control

## 🌐 API Endpoints

| Method | Path | File |
|---|---|---|
| POST | `/register` | `__repo_sync_tmp__\apps\users\auth_router.py` |
| POST | `/login` | `__repo_sync_tmp__\apps\users\auth_router.py` |
| GET | `/me` | `__repo_sync_tmp__\apps\users\auth_router.py` |
| POST | `/logout` | `__repo_sync_tmp__\apps\users\auth_router.py` |
| POST | `/refresh` | `__repo_sync_tmp__\apps\users\auth_router.py` |
| POST | `/register` | `__repo_sync_tmp__\apps\users\router.py` |
| POST | `/login` | `__repo_sync_tmp__\apps\users\router.py` |
| GET | `/me` | `__repo_sync_tmp__\apps\users\router.py` |
| PUT | `/me` | `__repo_sync_tmp__\apps\users\router.py` |
| GET | `/` | `__repo_sync_tmp__\apps\users\router.py` |
| DELETE | `/{user_id}` | `__repo_sync_tmp__\apps\users\router.py` |
| GET | `/transactions` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/transactions/{tx_id}` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| POST | `/transactions` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/summary` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/charts/income-expense` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/charts/category-distribution` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/invoices` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/reports/download` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| POST | `/upload/statement` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/ledger` | `__repo_sync_tmp__\apps\api\routes\accounting.py` |
| GET | `/balance/{address}` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| GET | `/stats` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| POST | `/transfer` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| GET | `/staking/tiers` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| POST | `/staking/stake` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| GET | `/transactions/{address}` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| GET | `/mining/recent` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| POST | `/verify` | `__repo_sync_tmp__\apps\api\routes\ecocoin.py` |
| POST | `/carbon/run` | `__repo_sync_tmp__\apps\api\routes\simulator.py` |
| POST | `/water/run` | `__repo_sync_tmp__\apps\api\routes\simulator.py` |
| POST | `/biodiversity/run` | `__repo_sync_tmp__\apps\api\routes\simulator.py` |
| GET | `/forest-types` | `__repo_sync_tmp__\apps\api\routes\simulator.py` |
| GET | `/ecosystem-types` | `__repo_sync_tmp__\apps\api\routes\simulator.py` |
| POST | `/login/access-token` | `repos\fastapi-template\backend\app\api\routes\login.py` |
| POST | `/login/test-token` | `repos\fastapi-template\backend\app\api\routes\login.py` |
| POST | `/password-recovery/{email}` | `repos\fastapi-template\backend\app\api\routes\login.py` |
| POST | `/reset-password/` | `repos\fastapi-template\backend\app\api\routes\login.py` |
| POST | `/password-recovery-html-content/{email}` | `repos\fastapi-template\backend\app\api\routes\login.py` |
| POST | `/register` | `apps\users\auth_router.py` |
| POST | `/login` | `apps\users\auth_router.py` |
| GET | `/me` | `apps\users\auth_router.py` |
| POST | `/logout` | `apps\users\auth_router.py` |
| POST | `/refresh` | `apps\users\auth_router.py` |
| POST | `/register` | `apps\users\router.py` |
| POST | `/login` | `apps\users\router.py` |
| GET | `/me` | `apps\users\router.py` |
| PUT | `/me` | `apps\users\router.py` |
| GET | `/` | `apps\users\router.py` |
| DELETE | `/{user_id}` | `apps\users\router.py` |
| GET | `/accounts` | `apps\api\routes\accounting.py` |
| GET | `/accounts/{account_id}` | `apps\api\routes\accounting.py` |
| POST | `/accounts` | `apps\api\routes\accounting.py` |
| PATCH | `/accounts/{account_id}` | `apps\api\routes\accounting.py` |
| GET | `/journal-entries` | `apps\api\routes\accounting.py` |
| POST | `/journal-entries` | `apps\api\routes\accounting.py` |
| GET | `/invoices` | `apps\api\routes\accounting.py` |
| POST | `/invoices` | `apps\api\routes\accounting.py` |
| PATCH | `/invoices/{invoice_id}` | `apps\api\routes\accounting.py` |
| GET | `/payments` | `apps\api\routes\accounting.py` |
| POST | `/payments` | `apps\api\routes\accounting.py` |
| GET | `/budgets` | `apps\api\routes\accounting.py` |
| POST | `/budgets` | `apps\api\routes\accounting.py` |
| GET | `/summary` | `apps\api\routes\accounting.py` |
| GET | `/balance/{address}` | `apps\api\routes\ecocoin.py` |
| GET | `/stats` | `apps\api\routes\ecocoin.py` |
| POST | `/transfer` | `apps\api\routes\ecocoin.py` |
| GET | `/staking/tiers` | `apps\api\routes\ecocoin.py` |
| POST | `/staking/stake` | `apps\api\routes\ecocoin.py` |
| GET | `/transactions/{address}` | `apps\api\routes\ecocoin.py` |
| GET | `/mining/recent` | `apps\api\routes\ecocoin.py` |
| POST | `/verify` | `apps\api\routes\ecocoin.py` |
| POST | `/carbon/run` | `apps\api\routes\simulator.py` |
| POST | `/water/run` | `apps\api\routes\simulator.py` |
| POST | `/biodiversity/run` | `apps\api\routes\simulator.py` |
| GET | `/forest-types` | `apps\api\routes\simulator.py` |
| GET | `/ecosystem-types` | `apps\api\routes\simulator.py` |

## 🗄️ مدل‌های دیتابیس

### `ContractsBuilder`

- **فایل:** `__repo_sync_tmp__\scripts\builders\contracts_builder.py`
### `Conversation`

- **فایل:** `__repo_sync_tmp__\apps\ai_agents\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `agent_type`: str
  - `title`: Optional[str
  - `metadata_json`: Optional[dict
  - `created_at`: datetime
  - `updated_at`: datetime
  - `messages`: List["Message"
  - `id`: int
  - `conversation_id`: int
### `Message`

- **فایل:** `__repo_sync_tmp__\apps\ai_agents\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `agent_type`: str
  - `title`: Optional[str
  - `metadata_json`: Optional[dict
  - `created_at`: datetime
  - `updated_at`: datetime
  - `messages`: List["Message"
  - `id`: int
  - `conversation_id`: int
### `LoginRequest`

- **فایل:** `__repo_sync_tmp__\apps\users\auth_router.py`
### `RegisterRequest`

- **فایل:** `__repo_sync_tmp__\apps\users\auth_router.py`
### `UserResponse`

- **فایل:** `__repo_sync_tmp__\apps\users\auth_router.py`
### `AuthResponse`

- **فایل:** `__repo_sync_tmp__\apps\users\auth_router.py`
### `RefreshRequest`

- **فایل:** `__repo_sync_tmp__\apps\users\auth_router.py`
### `UserBase`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `UserCreate`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `UserUpdate`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `UserResponse`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `Token`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `TokenData`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `LoginRequest`

- **فایل:** `__repo_sync_tmp__\apps\users\schemas.py`
### `Document`

- **فایل:** `__repo_sync_tmp__\apps\shared_ai\ai\rag\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `title`: str
  - `content`: str
  - `file_type`: str
  - `file_size`: int
  - `metadata_json`: dict
  - `is_processed`: bool
  - `chunk_count`: int
  - `created_at`: datetime
### `DocumentChunk`

- **فایل:** `__repo_sync_tmp__\apps\shared_ai\ai\rag\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `title`: str
  - `content`: str
  - `file_type`: str
  - `file_size`: int
  - `metadata_json`: dict
  - `is_processed`: bool
  - `chunk_count`: int
  - `created_at`: datetime
### `Transaction`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\accounting.py`
### `BalanceResponse`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\ecocoin.py`
### `TransferRequest`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\ecocoin.py`
### `TransferResponse`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\ecocoin.py`
### `StakingTier`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\ecocoin.py`
### `StakeRequest`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\ecocoin.py`
### `EcoCoinStats`

- **فایل:** `__repo_sync_tmp__\apps\api\routes\ecocoin.py`
### `ContractsBuilder`

- **فایل:** `scripts\builders\contracts_builder.py`
### `UserBase`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UserCreate`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UserRegister`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UserUpdate`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UserUpdateMe`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UpdatePassword`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `User`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UserPublic`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `UsersPublic`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `ItemBase`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `ItemCreate`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `ItemUpdate`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `Item`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `ItemPublic`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `ItemsPublic`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `Message`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `Token`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `TokenPayload`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `NewPassword`

- **فایل:** `repos\fastapi-template\backend\app\models.py`
### `Settings`

- **فایل:** `repos\fastapi-template\backend\app\core\config.py`
### `Conversation`

- **فایل:** `apps\ai_agents\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `agent_type`: str
  - `title`: Optional[str
  - `metadata_json`: Optional[dict
  - `created_at`: datetime
  - `updated_at`: datetime
  - `messages`: List["Message"
  - `id`: int
  - `conversation_id`: int
### `Message`

- **فایل:** `apps\ai_agents\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `agent_type`: str
  - `title`: Optional[str
  - `metadata_json`: Optional[dict
  - `created_at`: datetime
  - `updated_at`: datetime
  - `messages`: List["Message"
  - `id`: int
  - `conversation_id`: int
### `Settings`

- **فایل:** `apps\shared_core\config.py`
### `CRUDBase`

- **فایل:** `apps\shared_core\crud.py`
### `CRUDUser`

- **فایل:** `apps\shared_core\crud.py`
### `LoginRequest`

- **فایل:** `apps\users\auth_router.py`
### `RegisterRequest`

- **فایل:** `apps\users\auth_router.py`
### `UserResponse`

- **فایل:** `apps\users\auth_router.py`
### `AuthResponse`

- **فایل:** `apps\users\auth_router.py`
### `RefreshRequest`

- **فایل:** `apps\users\auth_router.py`
### `UserBase`

- **فایل:** `apps\users\schemas.py`
### `UserCreate`

- **فایل:** `apps\users\schemas.py`
### `UserUpdate`

- **فایل:** `apps\users\schemas.py`
### `UserResponse`

- **فایل:** `apps\users\schemas.py`
### `Token`

- **فایل:** `apps\users\schemas.py`
### `TokenData`

- **فایل:** `apps\users\schemas.py`
### `LoginRequest`

- **فایل:** `apps\users\schemas.py`
### `AuditLogMiddleware`

- **فایل:** `apps\shared_core\middleware\audit_log.py`
### `Document`

- **فایل:** `apps\shared_ai\ai\rag\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `title`: str
  - `content`: str
  - `file_type`: str
  - `file_size`: int
  - `metadata_json`: dict
  - `is_processed`: bool
  - `chunk_count`: int
  - `created_at`: datetime
### `DocumentChunk`

- **فایل:** `apps\shared_ai\ai\rag\models.py`
- **فیلدها:**
  - `id`: int
  - `user_id`: int
  - `title`: str
  - `content`: str
  - `file_type`: str
  - `file_size`: int
  - `metadata_json`: dict
  - `is_processed`: bool
  - `chunk_count`: int
  - `created_at`: datetime
### `Account`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `JournalEntry`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `JournalItem`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `Invoice`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `InvoiceItem`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `Payment`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `Budget`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `BudgetAlert`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `TaxRate`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `FixedAsset`

- **فایل:** `apps\api\models\accounting.py`
- **فیلدها:**
  - `id`: str
  - `code`: str
  - `name`: str
  - `name_fa`: Optional[str
  - `account_type`: AccountType
  - `parent_id`: Optional[str
  - `description`: Optional[str
  - `is_active`: bool
  - `is_system`: bool
  - `created_at`: datetime
### `BalanceResponse`

- **فایل:** `apps\api\routes\ecocoin.py`
### `TransferRequest`

- **فایل:** `apps\api\routes\ecocoin.py`
### `TransferResponse`

- **فایل:** `apps\api\routes\ecocoin.py`
### `StakingTier`

- **فایل:** `apps\api\routes\ecocoin.py`
### `StakeRequest`

- **فایل:** `apps\api\routes\ecocoin.py`
### `EcoCoinStats`

- **فایل:** `apps\api\routes\ecocoin.py`
### `AccountBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `AccountCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `AccountUpdate`

- **فایل:** `apps\api\schemas\accounting.py`
### `AccountResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `AccountListResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalItemBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalItemCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalItemResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalEntryBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalEntryCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalEntryUpdate`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalEntryResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `JournalEntryListResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceItemBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceItemCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceItemResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceUpdate`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `InvoiceListResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `PaymentBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `PaymentCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `PaymentResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `PaymentListResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `BudgetBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `BudgetCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `BudgetUpdate`

- **فایل:** `apps\api\schemas\accounting.py`
### `BudgetResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `BudgetListResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `TaxRateBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `TaxRateCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `TaxRateUpdate`

- **فایل:** `apps\api\schemas\accounting.py`
### `TaxRateResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `FixedAssetBase`

- **فایل:** `apps\api\schemas\accounting.py`
### `FixedAssetCreate`

- **فایل:** `apps\api\schemas\accounting.py`
### `FixedAssetUpdate`

- **فایل:** `apps\api\schemas\accounting.py`
### `FixedAssetResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `BalanceSheetResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `IncomeStatementResponse`

- **فایل:** `apps\api\schemas\accounting.py`
### `DashboardSummaryResponse`

- **فایل:** `apps\api\schemas\accounting.py`

## 📦 وابستگی‌های بلاکچین

- `wagmi@^3.7.1`
- `web3@^4.16.0`
- `@rainbow-me/rainbowkit@^2.2.11`
- `viem@^2.55.1`
- `ethers@^6.8.0`