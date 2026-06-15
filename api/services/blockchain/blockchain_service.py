"""Blockchain integration service for carbon credits and certificates."""
from web3 import Web3
from typing import Optional
import os
import json


class BlockchainService:
    def __init__(self):
        self.rpc_url = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # آدرس قراردادها
        self.seed_token_address = os.getenv("SEED_TOKEN_ADDRESS")
        self.gaia_cert_address = os.getenv("GAIA_CERTIFICATE_ADDRESS")
        
        # ABI قراردادها (ساده‌سازی شده)
        self.seed_token_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "mint",
                "outputs": [],
                "type": "function"
            }
        ]
        
        self.gaia_cert_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "projectId", "type": "string"},
                    {"name": "volumeTCO2e", "type": "uint256"},
                    {"name": "verificationDate", "type": "uint256"}
                ],
                "name": "issueCertificate",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
    
    def is_connected(self) -> bool:
        """بررسی اتصال به بلاکچین"""
        try:
            return self.web3.is_connected()
        except:
            return False
    
    def mint_seed_tokens(
        self,
        to_address: str,
        amount: int,
        private_key: str
    ) -> Optional[str]:
        """ضرب توکن‌های Seed"""
        if not self.seed_token_address:
            return None
        
        try:
            contract = self.web3.eth.contract(
                address=self.seed_token_address,
                abi=self.seed_token_abi
            )
            
            account = self.web3.eth.account.from_key(private_key)
            nonce = self.web3.eth.get_transaction_count(account.address)
            
            tx = contract.functions.mint(
                to_address,
                amount
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            print(f"Error minting tokens: {e}")
            return None
    
    def issue_gaia_certificate(
        self,
        project_id: str,
        volume_tco2e: int,
        verification_timestamp: int,
        private_key: str
    ) -> Optional[str]:
        """صدور گواهی گایا در بلاکچین"""
        if not self.gaia_cert_address:
            return None
        
        try:
            contract = self.web3.eth.contract(
                address=self.gaia_cert_address,
                abi=self.gaia_cert_abi
            )
            
            account = self.web3.eth.account.from_key(private_key)
            nonce = self.web3.eth.get_transaction_count(account.address)
            
            tx = contract.functions.issueCertificate(
                project_id,
                volume_tco2e,
                verification_timestamp
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.web3.eth.gas_price
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            print(f"Error issuing certificate: {e}")
            return None
    
    def get_transaction_receipt(self, tx_hash: str) -> Optional[dict]:
        """دریافت رسید تراکنش"""
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            return {
                "status": receipt.status,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed
            }
        except:
            return None
