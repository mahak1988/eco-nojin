from pathlib import Path
import re

print("=" * 80)
print("🔧 FIXING ECOCOIN ROUTER - CORRECT ORDER")
print("=" * 80)

router_path = Path('api/modules/ecocoin/router.py')
content = router_path.read_text(encoding='utf-8-sig')

# Check current state
print("\n📄 Analyzing current router.py...")

# Find router definition
router_def_match = re.search(r'router\s*=\s*APIRouter\([^)]*\)', content)
if not router_def_match:
    print("❌ Could not find router = APIRouter()")
    exit(1)

router_def_pos = router_def_match.end()
print(f"✅ Found router definition at position {router_def_pos}")

# Check if new endpoints were added before router
if '@router.get("/tokens")' in content:
    tokens_pos = content.find('@router.get("/tokens")')
    if tokens_pos < router_def_pos:
        print("❌ Endpoints were added BEFORE router definition!")
        print("   Removing misplaced endpoints...")
        
        # Remove everything from @router.get("/tokens") to the router definition
        content = content[:tokens_pos] + content[router_def_pos:]
        print("   ✅ Removed misplaced endpoints")

# Now find the correct position (AFTER router definition and imports)
# Look for the first endpoint or the end of imports
lines = content.split('\n')
insert_idx = 0

# Find the line with router = APIRouter
for i, line in enumerate(lines):
    if 'router = APIRouter' in line:
        insert_idx = i + 1
        break

print(f"✅ Will insert new endpoints at line {insert_idx}")

# Generate new endpoints
new_endpoints = '''

# ============================================================
# Additional Endpoints (Auto-generated)
# ============================================================

@router.get("/tokens")
async def get_tokens():
    """لیست تمام توکن‌های موجود"""
    return {
        "tokens": [
            {
                "symbol": "ECO",
                "name": "EcoCoin",
                "type": "utility",
                "total_supply": 1000000,
                "circulating_supply": 500000,
                "price_usd": 0.50
            },
            {
                "symbol": "GRC",
                "name": "Green Carbon Credit",
                "type": "asset-backed",
                "total_supply": 100000,
                "circulating_supply": 25000,
                "price_usd": 10.00
            }
        ]
    }


@router.get("/reward-rates")
async def get_reward_rates():
    """نرخ‌های پاداش برای اقدامات زیست‌محیطی"""
    return {
        "rates": [
            {"action": "tree_planting", "reward": 10, "unit": "ECO per tree"},
            {"action": "water_saving", "reward": 5, "unit": "ECO per 1000L"},
            {"action": "carbon_offset", "reward": 100, "unit": "ECO per ton"},
            {"action": "renewable_energy", "reward": 50, "unit": "ECO per MWh"},
            {"action": "waste_recycling", "reward": 2, "unit": "ECO per kg"}
        ]
    }


@router.get("/stats")
async def get_ecocoin_stats():
    """آمار کلی سیستم EcoCoin"""
    return {
        "wallets_count": 1250,
        "total_rewards": 500000,
        "actions_count": 15000,
        "carbon_sequestered_tons": 2500.5,
        "water_saved_liters": 15000000,
        "energy_generated_kwh": 750000
    }


@router.get("/wallets/{wallet_id}")
async def get_wallet_by_id(wallet_id: int):
    """دریافت اطلاعات کیف پول با ID"""
    return {
        "wallet_id": wallet_id,
        "address": f"0x{wallet_id:040x}",
        "eco_balance": 1500,
        "grc_balance": 50,
        "staked_eco": 500,
        "staked_grc": 10,
        "total_earned": 2500,
        "user_level": 3,
        "reputation_score": 85.5,
        "created_at": "2024-01-15T10:30:00Z"
    }
'''

# Insert at correct position
lines.insert(insert_idx, new_endpoints)
new_content = '\n'.join(lines)

# Write back
router_path.write_text(new_content, encoding='utf-8')
print("✅ New endpoints added AFTER router definition")

# Verify
print("\n🔍 Verifying fix...")
verify_content = router_path.read_text(encoding='utf-8-sig')
router_pos = verify_content.find('router = APIRouter')
tokens_pos = verify_content.find('@router.get("/tokens")')

if router_pos < tokens_pos:
    print("✅ CORRECT: Endpoints are AFTER router definition")
else:
    print("❌ ERROR: Endpoints still before router!")
    exit(1)

# Count endpoints
endpoint_count = verify_content.count('@router.')
print(f"📊 Total endpoints: {endpoint_count}")

print("\n" + "=" * 80)
print("✅ ECOCOIN ROUTER FIXED")
print("=" * 80)
print("\n🚀 Next steps:")
print("1. Restart backend: uvicorn api.main:app --reload --port 8000")
print("2. Check Swagger: http://localhost:8000/docs")
print("3. Test endpoints in browser or curl")