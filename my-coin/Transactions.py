from dataclasses import dataclass

import dataclasses
from typing import Iterable

import json
import pickle

from utils import verify, sign


@dataclass
class TransInput:
    public_key: str  # PEM
    amount: int


@dataclass
class TransOutput:
    public_key: str  # PEM
    amount: int


@dataclass(frozen=True, slots=True)
class Transaction:
    input: TransInput | None
    output: TransOutput
    transaction_id: int
    number_in_chain: int

    def serialized_input_output(self) -> str:
        inp = self.input
        t_id = self.transaction_id
        ou = self.output
        separators = (",", ":")
        output_json_dump = json.dumps(
            obj=dataclasses.asdict(ou), sort_keys=True, separators=separators
        )
        ser_t_id = json.dumps(t_id, separators=separators)

        if inp:
            inp_json_dump = json.dumps(
                obj=dataclasses.asdict(inp), sort_keys=True, separators=separators
            )
            return inp_json_dump + "|" + ser_t_id + "|" + output_json_dump
        else:
            return "|" + ser_t_id + "|" + output_json_dump


@dataclass(frozen=True, slots=True)
class TransactionSigned(Transaction):
    signature: str

    @classmethod
    def from_transaction(cls, transaction: Transaction, private_key: str):
        serialized = transaction.serialized_input_output().encode()
        signature = sign(serialized, private_key).hex()
        return cls(
            transaction.input,
            transaction.output,
            transaction.transaction_id,
            transaction.number_in_chain,
            signature,
        )

    def is_valid(self) -> bool:
        serialized = self.serialized_input_output()
        key = self.input.public_key if self.input else self.output.public_key
        if self.output.amount < 0:
            return False
        if self.input and self.input.amount != self.output.amount:
            return False
        try:
            verify(serialized, self.signature.encode(), key)
            return True
        except Exception:
            return False

    # SERIALIZATION
    def pack_transaction(self) -> str:
        return pickle.dumps(self).decode("latin-1")

    # DESERIALIZATION
    @classmethod
    def unpack_transaction(cls, packed_transaction: str):
        new_obj = pickle.loads(packed_transaction.encode("latin-1"))
        if isinstance(new_obj, TransactionSigned):
            return new_obj
        else:
            raise Exception("Invalid object instance unpickled")


def known_transactions_id(list_with_transactions: Iterable[TransactionSigned]):
    known_trans: dict[str, set[int]] = {}
    for transaction in list_with_transactions:
        trans_input = transaction.input
        if not (trans_input := transaction.input):
            if transaction.transaction_id != 0:
                raise Exception("Genesis with wrong id")
        else:
            public_key = trans_input.public_key
            trans_id = transaction.transaction_id
            if user_trans := known_trans.get(public_key):
                if trans_id in user_trans:
                    raise Exception(
                        f"Replay of transaction with already used id:{trans_id}"
                    )
                else:
                    user_trans.add(trans_id)
    return known_trans


def eval_balance(
    transactions: Iterable[TransactionSigned], accounts: dict[str, int], miner_fee: int
):
    for trans in transactions:
        input = trans.input
        output = trans.output
        # check signed
        # check if amount is the same as fee
        if not trans.is_valid():
            raise Exception("Transaction not valid")

        if not input:
            # coinbase
            if output.amount == miner_fee:
                if not accounts.get(output.public_key):
                    accounts[output.public_key] = miner_fee
                else:
                    accounts[output.public_key] += miner_fee
            else:
                raise Exception("Fee different than miner fee")
        else:
            payer_address = input.public_key
            payee_address = output.public_key
            expense = input.amount
            if expense < 0:
                raise Exception("Input amount cant be a negative number")
            payer_account_balance = accounts.get(payer_address)
            if not payer_account_balance:
                raise Exception("Non existing payer attempting to transfer")
            else:
                print(payer_account_balance)
                if payer_account_balance < expense:
                    raise Exception("Spending above amount")
                else:
                    if not accounts.get(output.public_key):
                        # logging.warning("New or dead wallet")
                        accounts[payee_address] = 0
                    accounts[payee_address] += expense
                    accounts[payer_address] -= expense
    return accounts
