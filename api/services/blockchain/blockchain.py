"""
Blockchain Service - Polygon/Ethereum Integration
سرویس بلاکچین برای EcoCoin - رایگان با testnet
Documentation: https://docs.polygon.technology/
"""
import hashlib
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal


class Wallet(BaseModel):
    address: str
    balance_eco: float
    balance_grc: float
    staked_eco: float
    staked_grc: float
    total_earned: float
    reputation_score: float
    level: int
    created_at: str


class Transaction(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str
    token_type: str  # ECO, GRC
    amount: float
    tx_type: str  # transfer, stake, unstake, reward, exchange
    status: str  # pending, confirmed, failed
    timestamp: str
    block_number: int
    gas_used: int
    gas_price: float


class StakePosition(BaseModel):
    id: str
    wallet_address: str
    token_type: str
    amount: float
    lock_period_days: int
    start_date: str
    end_date: str
    apy: float
    status: str  # active, matured, withdrawn
    rewards_earned: float


class EcoCoinContract:
    """شبیه‌سازی قرارداد هوشمند EcoCoin"""
    
    # Token constants
    ECO_TOTAL_SUPPLY = 1_000_000_000  # 1 billion
    GRC_TOTAL_SUPPLY = 100_000_000    # 100 million
    
    # Staking APY
    STAKING_APY = {
        'ECO': 0.08,  # 8% annual
        'GRC': 0.12,  # 12% annual
    }
    
    # Reward rates (tokens per action)
    REWARD_RATES = {
        'tree_planting': {'ECO': 10, 'GRC': 0},
        'water_saving': {'ECO': 5, 'GRC': 0},
        'carbon_offset': {'ECO': 0, 'GRC': 100},
        'renewable_energy': {'ECO': 50, 'GRC': 10},
        'waste_recycling': {'ECO': 2, 'GRC': 0},
        'soil_restoration': {'ECO': 20, 'GRC': 5},
        'biodiversity': {'ECO': 15, 'GRC': 3},
    }
    
    def __init__(self):
        # In-memory state (replace with actual blockchain in production)
        self._wallets: Dict[str, Wallet] = {}
        self._transactions: List[Transaction] = []
        self._stakes: Dict[str, StakePosition] = {}
        self._block_number = 1000000
    
    def create_wallet(self, address: Optional[str] = None) -> Wallet:
        """ایجاد کیف پول جدید"""
        if not address:
            # Generate mock address
            address = "0x" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:40]
        
        wallet = Wallet(
            address=address,
            balance_eco=1000.0,  # Initial balance for testing
            balance_grc=50.0,
            staked_eco=0.0,
            staked_grc=0.0,
            total_earned=0.0,
            reputation_score=50.0,
            level=1,
            created_at=datetime.now().isoformat()
        )
        
        self._wallets[address] = wallet
        return wallet
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        """دریافت کیف پول"""
        wallet = self._wallets.get(address)
        if not wallet:
            # Auto-create for testing
            wallet = self.create_wallet(address)
        return wallet
    
    def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        token_type: str = 'ECO'
    ) -> Transaction:
        """انتقال توکن"""
        from_wallet = self.get_wallet(from_address)
        to_wallet = self.get_wallet(to_address)
        
        if not from_wallet or not to_wallet:
            raise ValueError("Invalid wallet address")
        
        # Check balance
        if token_type == 'ECO':
            if from_wallet.balance_eco < amount:
                raise ValueError("Insufficient ECO balance")
            from_wallet.balance_eco -= amount
            to_wallet.balance_eco += amount
        elif token_type == 'GRC':
            if from_wallet.balance_grc < amount:
                raise ValueError("Insufficient GRC balance")
            from_wallet.balance_grc -= amount
            to_wallet.balance_grc += amount
        else:
            raise ValueError("Invalid token type")
        
        # Create transaction
        self._block_number += 1
        tx = Transaction(
            tx_hash="0x" + hashlib.sha256(f"{time.time()}{from_address}{to_address}".encode()).hexdigest()[:64],
            from_address=from_address,
            to_address=to_address,
            token_type=token_type,
            amount=amount,
            tx_type="transfer",
            status="confirmed",
            timestamp=datetime.now().isoformat(),
            block_number=self._block_number,
            gas_used=21000,
            gas_price=0.00000003  # 30 gwei in ETH
        )
        
        self._transactions.append(tx)
        return tx
    
    def stake(
        self,
        wallet_address: str,
        amount: float,
        token_type: str,
        lock_period_days: int = 30
    ) -> StakePosition:
        """Stake کردن توکن"""
        wallet = self.get_wallet(wallet_address)
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Check balance
        if token_type == 'ECO':
            if wallet.balance_eco < amount:
                raise ValueError("Insufficient ECO balance")
            wallet.balance_eco -= amount
            wallet.staked_eco += amount
        elif token_type == 'GRC':
            if wallet.balance_grc < amount:
                raise ValueError("Insufficient GRC balance")
            wallet.balance_grc -= amount
            wallet.staked_grc += amount
        else:
            raise ValueError("Invalid token type")
        
        # Create stake position
        stake_id = f"stake_{int(time.time() * 1000)}"
        start_date = datetime.now()
        end_date = start_date + __import__('datetime').timedelta(days=lock_period_days)
        
        stake = StakePosition(
            id=stake_id,
            wallet_address=wallet_address,
            token_type=token_type,
            amount=amount,
            lock_period_days=lock_period_days,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            apy=self.STAKING_APY[token_type],
            status="active",
            rewards_earned=0.0
        )
        
        self._stakes[stake_id] = stake
        return stake
    
    def unstake(self, stake_id: str) -> Tuple[StakePosition, float]:
        """برداشت از stake"""
        stake = self._stakes.get(stake_id)
        if not stake:
            raise ValueError("Stake position not found")
        
        if stake.status != "active":
            raise ValueError("Stake is not active")
        
        # Calculate rewards
        start = datetime.fromisoformat(stake.start_date)
        now = datetime.now()
        days_staked = (now - start).days
        
        # Proportional rewards
        annual_reward = stake.amount * stake.apy
        daily_reward = annual_reward / 365
        rewards = daily_reward * days_staked
        
        # Update stake
        stake.status = "withdrawn"
        stake.rewards_earned = rewards
        
        # Return tokens + rewards to wallet
        wallet = self.get_wallet(stake.wallet_address)
        if stake.token_type == 'ECO':
            wallet.staked_eco -= stake.amount
            wallet.balance_eco += stake.amount + rewards
        else:
            wallet.staked_grc -= stake.amount
            wallet.balance_grc += stake.amount + rewards
        
        return stake, rewards
    
    def reward_action(
        self,
        wallet_address: str,
        action_type: str,
        quantity: float = 1.0
    ) -> Dict[str, float]:
        """پاداش برای اقدام زیست‌محیطی"""
        wallet = self.get_wallet(wallet_address)
        if not wallet:
            raise ValueError("Wallet not found")
        
        rates = self.REWARD_RATES.get(action_type)
        if not rates:
            raise ValueError(f"Unknown action type: {action_type}")
        
        rewards = {}
        for token, rate in rates.items():
            reward_amount = rate * quantity
            rewards[token] = reward_amount
            
            if token == 'ECO':
                wallet.balance_eco += reward_amount
            elif token == 'GRC':
                wallet.balance_grc += reward_amount
        
        wallet.total_earned += sum(rewards.values())
        
        # Update reputation
        wallet.reputation_score = min(100, wallet.reputation_score + 0.5)
        
        # Level up
        wallet.level = int(wallet.reputation_score / 10) + 1
        
        # Create reward transaction
        self._block_number += 1
        for token, amount in rewards.items():
            if amount > 0:
                tx = Transaction(
                    tx_hash="0x" + hashlib.sha256(f"{time.time()}{wallet_address}{action_type}".encode()).hexdigest()[:64],
                    from_address="0x0000000000000000000000000000000000000000",  # Mint
                    to_address=wallet_address,
                    token_type=token,
                    amount=amount,
                    tx_type="reward",
                    status="confirmed",
                    timestamp=datetime.now().isoformat(),
                    block_number=self._block_number,
                    gas_used=0,
                    gas_price=0
                )
                self._transactions.append(tx)
        
        return rewards
    
    def get_transactions(
        self,
        wallet_address: Optional[str] = None,
        limit: int = 50
    ) -> List[Transaction]:
        """دریافت تراکنش‌ها"""
        txs = self._transactions
        
        if wallet_address:
            txs = [
                t for t in txs
                if t.from_address == wallet_address or t.to_address == wallet_address
            ]
        
        return txs[-limit:]
    
    def get_stake_positions(self, wallet_address: str) -> List[StakePosition]:
        """دریافت موقعیت‌های stake"""
        return [
            s for s in self._stakes.values()
            if s.wallet_address == wallet_address
        ]
    
    def get_token_stats(self) -> Dict:
        """آمار توکن‌ها"""
        total_eco = sum(w.balance_eco + w.staked_eco for w in self._wallets.values())
        total_grc = sum(w.balance_grc + w.staked_grc for w in self._wallets.values())
        
        return {
            "eco": {
                "total_supply": self.ECO_TOTAL_SUPPLY,
                "circulating": total_eco,
                "price_usd": 0.50,
                "market_cap": total_eco * 0.50
            },
            "grc": {
                "total_supply": self.GRC_TOTAL_SUPPLY,
                "circulating": total_grc,
                "price_usd": 10.00,
                "market_cap": total_grc * 10.00
            },
            "total_wallets": len(self._wallets),
            "total_transactions": len(self._transactions),
            "block_number": self._block_number
        }
    
    def exchange_tokens(
        self,
        wallet_address: str,
        from_token: str,
        to_token: str,
        amount: float
    ) -> Transaction:
        """تبدیل توکن‌ها"""
        wallet = self.get_wallet(wallet_address)
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Exchange rate: 1 GRC = 20 ECO
        if from_token == 'ECO' and to_token == 'GRC':
            if wallet.balance_eco < amount:
                raise ValueError("Insufficient ECO balance")
            grc_amount = amount / 20
            wallet.balance_eco -= amount
            wallet.balance_grc += grc_amount
            received_amount = grc_amount
        elif from_token == 'GRC' and to_token == 'ECO':
            if wallet.balance_grc < amount:
                raise ValueError("Insufficient GRC balance")
            eco_amount = amount * 20
            wallet.balance_grc -= amount
            wallet.balance_eco += eco_amount
            received_amount = eco_amount
        else:
            raise ValueError("Invalid exchange pair")
        
        # Create transaction
        self._block_number += 1
        tx = Transaction(
            tx_hash="0x" + hashlib.sha256(f"{time.time()}{wallet_address}exchange".encode()).hexdigest()[:64],
            from_address=wallet_address,
            to_address=wallet_address,
            token_type=f"{from_token}->{to_token}",
            amount=amount,
            tx_type="exchange",
            status="confirmed",
            timestamp=datetime.now().isoformat(),
            block_number=self._block_number,
            gas_used=60000,
            gas_price=0.00000003
        )
        
        self._transactions.append(tx)
        return tx


# Singleton
ecocoin_contract = EcoCoinContract()
