# -*- coding: utf-8 -*-
"""
Gaia Oracle - پل ارتباطی بین Econojin و Gaia Blockchain
انتقال داده‌های علمی تأیید شده به Smart Contracts
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)


@dataclass
class RegenerationProof:
    """مدرک بازسازی اکوسیستمی"""
    proof_id: str
    miner_address: str
    activity_type: str
    location: Dict
    carbon_kg: float
    confidence: float
    methodology: str
    evidence_hash: str  # IPFS hash
    timestamp: datetime
    signature: Optional[str] = None
    
    def to_blockchain_format(self) -> Dict:
        """فرمت سازگار با Smart Contract"""
        return {
            "proofId": self.proof_id,
            "miner": self.miner_address,
            "activityType": self.activity_type,
            "carbonMilliKg": int(self.carbon_kg * 1000),  # دقت بالاتر
            "confidenceBps": int(self.confidence * 10000),  # basis points
            "evidenceHash": self.evidence_hash,
            "timestamp": int(self.timestamp.timestamp()),
        }


class GaiaOracle:
    """
    Oracle برای اتصال Econojin به Gaia Blockchain
    
    وظایف:
    1. دریافت نتایج علمی از Econojin
    2. امضای دیجیتال نتایج
    3. ارسال به Smart Contract
    4. تأیید و ثبت در blockchain
    """
    
    def __init__(
        self,
        rpc_url: str = "https://polygon-rpc.com",
        private_key: Optional[str] = None,
        contract_address: Optional[str] = None,
        network: str = "polygon_mainnet"
    ):
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.contract_address = contract_address
        self.network = network
        
        self.w3 = None
        self.account = None
        self.contract = None
        
        # تلاش برای اتصال
        self._init_web3()
    
    def _init_web3(self):
        """راه‌اندازی Web3"""
        try:
            from web3 import Web3
            
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self.w3.is_connected():
                logger.warning(f"Cannot connect to {self.rpc_url}")
                return
            
            logger.info(f"Connected to {self.network}")
            
            if self.private_key:
                self.account = self.w3.eth.account.from_key(self.private_key)
                logger.info(f"Oracle account: {self.account.address}")
            
            if self.contract_address:
                self._load_contract()
                
        except ImportError:
            logger.warning("Web3 not installed - using simulation mode")
        except Exception as e:
            logger.error(f"Web3 init failed: {e}")
    
    def _load_contract(self):
        """بارگذاری Smart Contract"""
        try:
            # ABI فایل contract
            abi_path = Path(__file__).parent.parent.parent / "contracts" / "RegenerationMiner.json"
            if abi_path.exists():
                with open(abi_path) as f:
                    contract_data = json.load(f)
                    self.contract = self.w3.eth.contract(
                        address=self.contract_address,
                        abi=contract_data.get('abi', [])
                    )
                    logger.info(f"Contract loaded: {self.contract_address}")
        except Exception as e:
            logger.error(f"Contract load failed: {e}")
    
    def create_proof(
        self,
        miner_address: str,
        activity_type: str,
        location: Dict,
        carbon_kg: float,
        confidence: float,
        methodology: str,
        evidence_data: Dict,
    ) -> RegenerationProof:
        """ایجاد مدرک بازسازی"""
        
        # ایجاد proof_id منحصربه‌فرد
        proof_hash = hashlib.sha256(
            f"{miner_address}:{activity_type}:{carbon_kg}:{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:32]
        proof_id = f"GAIA-{proof_hash[:8].upper()}"
        
        # Hash داده‌های evidence برای IPFS
        evidence_json = json.dumps(evidence_data, sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        proof = RegenerationProof(
            proof_id=proof_id,
            miner_address=miner_address,
            activity_type=activity_type,
            location=location,
            carbon_kg=carbon_kg,
            confidence=confidence,
            methodology=methodology,
            evidence_hash=evidence_hash,
            timestamp=datetime.now(timezone.utc),
        )
        
        logger.info(f"Proof created: {proof_id} ({carbon_kg:.2f} kg CO2)")
        return proof
    
    def sign_proof(self, proof: RegenerationProof) -> str:
        """امضای دیجیتال مدرک"""
        if not self.account:
            logger.warning("No account - cannot sign")
            return "simulation_signature"
        
        try:
            # ایجاد message hash
            message = self.w3.solidity_keccak(
                ['string', 'address', 'string', 'uint256', 'uint256', 'bytes32'],
                [
                    proof.proof_id,
                    proof.miner_address,
                    proof.activity_type,
                    int(proof.carbon_kg * 1000),
                    int(proof.confidence * 10000),
                    bytes.fromhex(proof.evidence_hash),
                ]
            )
            
            # امضا
            signed = self.account.sign_message(
                self.w3.eth.account.encode_defunct(message)
            )
            
            proof.signature = signed.signature.hex()
            logger.info(f"Proof signed: {proof.proof_id}")
            return proof.signature
            
        except Exception as e:
            logger.error(f"Signing failed: {e}")
            return "signature_error"
    
    def submit_to_blockchain(self, proof: RegenerationProof) -> Dict:
        """ارسال مدرک به blockchain"""
        
        if not self.contract or not self.account:
            # Simulation mode
            logger.info(f"[SIMULATION] Would submit: {proof.proof_id}")
            return {
                "status": "simulated",
                "proof_id": proof.proof_id,
                "tx_hash": f"0x{'0' * 64}",
                "gas_used": 150000,
            }
        
        try:
            # ساخت تراکنش
            blockchain_data = proof.to_blockchain_format()
            
            tx = self.contract.functions.submitVerifiedProof(
                blockchain_data["miner"],
                blockchain_data["carbonMilliKg"],
                blockchain_data["evidenceHash"],
                proof.signature
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # امضا و ارسال
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # انتظار برای تأیید
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            logger.info(f"Proof submitted: {tx_hash.hex()}")
            
            return {
                "status": "confirmed",
                "proof_id": proof.proof_id,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
            }
            
        except Exception as e:
            logger.error(f"Submission failed: {e}")
            return {
                "status": "failed",
                "proof_id": proof.proof_id,
                "error": str(e),
            }
    
    def verify_proof_onchain(self, proof_id: str) -> Dict:
        """تأیید مدرک روی blockchain"""
        if not self.contract:
            return {"verified": False, "error": "No contract"}
        
        try:
            proof_data = self.contract.functions.getProof(proof_id).call()
            return {
                "verified": True,
                "data": proof_data,
            }
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    def get_miner_stats(self, miner_address: str) -> Dict:
        """دریافت آمار miner"""
        if not self.contract:
            return {"error": "No contract"}
        
        try:
            stats = self.contract.functions.getMinerStats(miner_address).call()
            return {
                "total_proofs": stats[0],
                "total_carbon_kg": stats[1] / 1000,
                "total_seed_earned": stats[2] / 10**18,  # Wei to tokens
            }
        except Exception as e:
            return {"error": str(e)}