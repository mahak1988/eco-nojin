# api/scripts/seed_ecocoin.py
import asyncio
import sys
from pathlib import Path

# Fix sys.path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from api.core.database import engine, async_session, Base
from api.modules.ecocoin.models import (
    EcoToken, EcoRewardRate, EcoExchangeRate, EcoActionType, TokenType
)


async def seed():
    print("Seeding EcoCoin data...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if already seeded
        from sqlalchemy import select
        result = await session.execute(select(EcoToken))
        if result.scalars().first():
            print("  = Already seeded, skipping")
            return

        # Tokens
        eco = EcoToken(
            symbol="ECO", name="EcoCoin", name_en="EcoCoin",
            token_type=TokenType.ECO,
            total_supply=1_000_000_000,
            circulating_supply=100_000_000,
            price_usd=0.15, price_irr=9000,
            market_cap=15_000_000,
            decimals=18, max_supply=1_000_000_000,
            is_stakable=True,
            description="Utility token for ecological rewards",
        )
        session.add(eco)

        grc = EcoToken(
            symbol="GRC", name="GreenCredit", name_en="GreenCredit",
            token_type=TokenType.GRC,
            total_supply=0, circulating_supply=50_000_000,
            price_usd=0.25, price_irr=15000,
            market_cap=12_500_000,
            decimals=18, is_stakable=True,
            description="Governance token for voting",
        )
        session.add(grc)

        # Reward rates
        rates = [
            {"action_type": EcoActionType.TREE_PLANTING, "eco_per_unit": 10, "grc_per_unit": 2,
             "carbon_per_unit": 0.025, "description": "10 ECO per tree planted"},
            {"action_type": EcoActionType.LAND_RESTORATION, "eco_per_unit": 100, "grc_per_unit": 20,
             "bonus_multiplier": 1.5, "carbon_per_unit": 5.0, "water_per_unit": 10000,
             "description": "100 ECO per hectare restored"},
            {"action_type": EcoActionType.WATER_SAVING, "eco_per_unit": 5, "grc_per_unit": 1,
             "bonus_multiplier": 1.2, "water_per_unit": 1000,
             "description": "5 ECO per 1000L saved"},
            {"action_type": EcoActionType.RENEWABLE_ENERGY, "eco_per_unit": 50, "grc_per_unit": 10,
             "bonus_multiplier": 1.3, "carbon_per_unit": 0.5, "energy_per_unit": 1000,
             "description": "50 ECO per MWh renewable energy"},
            {"action_type": EcoActionType.RECYCLING, "eco_per_unit": 2, "grc_per_unit": 0.5,
             "carbon_per_unit": 0.005, "description": "2 ECO per 10kg recycled"},
            {"action_type": EcoActionType.CARBON_REDUCTION, "eco_per_unit": 20, "grc_per_unit": 5,
             "bonus_multiplier": 1.5, "carbon_per_unit": 1.0,
             "description": "20 ECO per ton CO2 reduced"},
            {"action_type": EcoActionType.SOIL_CONSERVATION, "eco_per_unit": 30, "grc_per_unit": 8,
             "bonus_multiplier": 1.2, "carbon_per_unit": 0.5,
             "description": "30 ECO per hectare soil conservation"},
            {"action_type": EcoActionType.BIODIVERSITY, "eco_per_unit": 50, "grc_per_unit": 15,
             "bonus_multiplier": 2.0, "description": "50 ECO per biodiversity project"},
        ]

        for r in rates:
            session.add(EcoRewardRate(**r))

        # Exchange rates
        session.add(EcoExchangeRate(from_token="ECO", to_token="GRC", rate=0.6, min_amount=100, max_amount=1000000, fee_percent=1.0))
        session.add(EcoExchangeRate(from_token="GRC", to_token="ECO", rate=1.5, min_amount=50, max_amount=500000, fee_percent=1.0))

        await session.commit()
        print("  + 2 tokens created")
        print("  + 8 reward rates created")
        print("  + 2 exchange rates created")
        print("  Done!")


if __name__ == "__main__":
    asyncio.run(seed())

