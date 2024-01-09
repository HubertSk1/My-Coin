from dataclasses import dataclass
from hashlib import sha256
from datetime import datetime
import threading
import pickle
import ast
from typing import List
from Transactions import *


@dataclass
class Block:
    index: int
    hash: str
    previous_hash: str | None
    timestamp: int
    data: str | None
    nonce: int | None


@dataclass
class GenesisBlock(Block):
    index = 0
    hash: None
    timestamp: None


class BlockChain:
    def __init__(self, difficulty=4):
        self.genesis_hash = None
        self.chain: list[Block] = [
            GenesisBlock(0, self.genesis_hash, None, None, None, None)
        ]
        self.difficulty = difficulty

    def add_block(self, block: Block):
        self.chain.append(block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    # HASH CALCULATIONS
    def calculate_hash_from_values(
        self, index: int, previous_hash: str, timestamp: int, data: str, nonce: int
    ):
        data_str = f"{index}{previous_hash}{timestamp}{data}{nonce}"
        hashed_data = sha256(data_str.encode()).hexdigest()
        return hashed_data

    def calculate_hash_for_block(self, block: Block):
        data_str = f"{block.index}{block.previous_hash}{block.timestamp}{block.data}{block.nonce}"
        hashed_data = sha256(data_str.encode()).hexdigest()
        return hashed_data

    # VALIDATION
    def hash_matches_difficulty(self, hash_value: str):
        return hash_value[: self.difficulty] == "0" * self.difficulty

    def is_valid_new_block(self, new_block: Block, previous_block: Block):
        if previous_block.index + 1 != new_block.index:
            print("Invalid index")
            return False
        elif previous_block.hash != new_block.previous_hash:
            print("Invalid previous hash")
            return False
        elif not self.hash_matches_difficulty(new_block.hash):
            print("Number of 0 doesn't match teh difficulty")
            return False
        elif self.calculate_hash_for_block(new_block) != new_block.hash:
            print(
                "Invalid hash:",
                self.calculate_hash_for_block(new_block),
                new_block.hash,
            )
            return False
        return True

    def is_valid_chain(self, blockchain_to_validate):
        # Verify if genesis valid
        if blockchain_to_validate.chain[0].index != 0:
            return False
        elif blockchain_to_validate.chain[0].hash != None:
            return False

        # Verify the rest of blocks
        for i in range(1, len(blockchain_to_validate.chain)):
            if not self.is_valid_new_block(
                blockchain_to_validate.chain[i], blockchain_to_validate.chain[i - 1]
            ):
                return False

        # Verify Transactions

        list_with_transactions = self.unpack_transactions_from_blockchain()
        try:
            eval_balance(list_with_transactions, {}, 50)
        except Exception as E:
            print(E)
            return False

        return True

    def unpack_transactions_from_blockchain(self):
        list_with_transactions: list[str] = []
        for i in range(0, len(self.chain)):
            data = self.chain[i].data
            if data:
                list_with_transactions = list_with_transactions + ast.literal_eval(data)
        return [
            TransactionSigned.unpack_transaction(str_transaction)
            for str_transaction in list_with_transactions
        ]

    # CONSENSUS
    def find_longer_chain(self, chain_to_check) -> Tuple[bool, List[Block]]:
        if self.is_valid_chain(chain_to_check) and len(self.chain) < len(
            chain_to_check.chain
        ):
            block_list: list[Block] = []
            for index, block in enumerate(self.chain):
                if block != chain_to_check.chain[index]:
                    block_list.append(block)
            self.chain = chain_to_check.chain
            return True, block_list
        else:
            return False, []

    # MINING
    def generate_next_block(self, block_data: str, stop_event: threading.Event):
        previous_block = self.get_latest_block()
        next_index = previous_block.index + 1
        next_timestamp = int(datetime.now().timestamp())
        found, new_block = self.find_block(
            next_index, previous_block.hash, next_timestamp, block_data, stop_event
        )
        return found, new_block

    def find_block(
        self,
        index: int,
        previous_hash: str,
        timestamp: int,
        data: str,
        stop_event: threading.Event,
    ):
        nonce = 0
        while True:
            hash_value = self.calculate_hash_from_values(
                index, previous_hash, timestamp, data, nonce
            )
            if stop_event.is_set():
                print("Someone found the block before you")
                return False, None
            if self.hash_matches_difficulty(hash_value):
                print("YOU FOUND BLOCK :)")
                return True, Block(
                    index, hash_value, previous_hash, timestamp, data, nonce
                )
            nonce += 1

    # SERIALIZATION
    def pack_blockchain(self) -> str:
        return pickle.dumps(self).decode("latin-1")

    # DESERIALIZATION
    @classmethod
    def unpack_blockchain(cls, packed_blockchain: str):
        return pickle.loads(packed_blockchain.encode("latin-1"))
