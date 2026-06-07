# -*- coding: utf-8 -*-
"""
Blockchain Simulator for Testing
Simulates Polygon blockchain interactions without real network
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class Block:
    number: int
    timestamp: int
    transactions: List[Dict]
    previous_hash: str
    hash: str
    nonce: int = 0


@dataclass
class Transaction:
    tx_hash: str
    from_address: str
    to_address: str
    value: int
    data: str
    timestamp: int
    block_number: Optional[int] = None


@dataclass
class NFTToken:
    token_id: int
    owner: str
    contract_address: str
    metadata_uri: str
    minted_at: int
    last_update: int


class BlockchainSimulator:
    """Simulates a blockchain for testing smart contracts"""

    def __init__(self, chain_id: int = 31337, block_time: int = 2):
        self.chain_id = chain_id
        self.block_time = block_time
        self.blocks: List[Block] = []
        self.pending_txs: List[Transaction] = []
        self.nfts: Dict[int, NFTToken] = {}
        self.balances: Dict[str, int] = {}
        self.next_token_id = 1
        self.current_block = 0

        # Create genesis block
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = Block(
            number=0,
            timestamp=int(time.time()),
            transactions=[],
            previous_hash="0" * 64,
            hash=self._calculate_hash(0, int(time.time()), [], "0" * 64, 0),
        )
        self.blocks.append(genesis)

    def _calculate_hash(
        self, number: int, timestamp: int, txs: List[Dict], prev_hash: str, nonce: int
    ) -> str:
        data = f"{number}{timestamp}{json.dumps(txs)}{prev_hash}{nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self) -> Block:
        """Mine a new block with pending transactions"""
        self.current_block += 1
        prev_block = self.blocks[-1]

        # Simple mining (no real PoW)
        nonce = 0
        new_hash = self._calculate_hash(
            self.current_block,
            int(time.time()),
            [asdict(tx) for tx in self.pending_txs],
            prev_block.hash,
            nonce,
        )
        block = Block(
            number=self.current_block,
            timestamp=int(time.time()),
            transactions=[asdict(tx) for tx in self.pending_txs],
            previous_hash=prev_block.hash,
            hash=new_hash,
            nonce=nonce,
        )

        # Update transaction block numbers
        for tx in self.pending_txs:
            tx.block_number = self.current_block

        self.blocks.append(block)
        self.pending_txs.clear()

        return block

    def send_transaction(
        self, from_addr: str, to_addr: str, value: int, data: str = ""
    ) -> Transaction:
        """Send a transaction"""
        tx_hash = hashlib.sha256(
            f"{from_addr}{to_addr}{value}{data}{time.time()}".encode()
        ).hexdigest()

        tx = Transaction(
            tx_hash=tx_hash,
            from_address=from_addr,
            to_address=to_addr,
            value=value,
            data=data,
            timestamp=int(time.time()),
        )

        self.pending_txs.append(tx)

        # Auto-mine after each transaction
        self.mine_block()

        return tx

    def mint_nft(self, owner: str, contract_address: str, metadata_uri: str) -> NFTToken:
        """Mint a new NFT"""
        token_id = self.next_token_id
        self.next_token_id += 1

        nft = NFTToken(
            token_id=token_id,
            owner=owner,
            contract_address=contract_address,
            metadata_uri=metadata_uri,
            minted_at=int(time.time()),
            last_update=int(time.time()),
        )

        self.nfts[token_id] = nft

        # Create mint transaction
        self.send_transaction(
            from_addr="0x0000000000000000000000000000000000000000",
            to_addr=contract_address,
            value=0,
            data=json.dumps({"type": "mint", "token_id": token_id, "owner": owner}),
        )

        return nft

    def get_nft(self, token_id: int) -> Optional[NFTToken]:
        return self.nfts.get(token_id)

    def get_balance(self, address: str) -> int:
        return self.balances.get(address, 0)

    def set_balance(self, address: str, amount: int):
        self.balances[address] = amount

    def get_block(self, number: int) -> Optional[Block]:
        if 0 <= number < len(self.blocks):
            return self.blocks[number]
        return None

    def get_latest_block(self) -> Block:
        return self.blocks[-1]

    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        for block in self.blocks:
            for tx in block.transactions:
                if tx["tx_hash"] == tx_hash:
                    return Transaction(**tx)
        return None

    def get_chain_info(self) -> Dict:
        return {
            "chain_id": self.chain_id,
            "current_block": self.current_block,
            "total_transactions": sum(len(b.transactions) for b in self.blocks),
            "total_nfts": len(self.nfts),
            "latest_block_hash": self.blocks[-1].hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global simulator instance
_simulator = BlockchainSimulator()


def get_simulator() -> BlockchainSimulator:
    return _simulator


def reset_simulator():
    global _simulator
    _simulator = BlockchainSimulator()
