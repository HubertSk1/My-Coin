import cryptography.hazmat.primitives.serialization as serial
import cryptography.exceptions as crypto_exceptions

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

from dataclasses import dataclass

import dataclasses
from typing import Iterable, Self

import json
import logging

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

    def serialized_input_output(self) -> str:
        inp = self.input
        ou = self.output
        separators = (",", ":")
        output_json_dump = json.dumps(
            obj=dataclasses.asdict(ou), sort_keys=True, separators=separators
        )

        if inp:
            inp_json_dump = json.dumps(
                obj=dataclasses.asdict(inp), sort_keys=True, separators=separators
            )
            return inp_json_dump + "|" + output_json_dump
        else:
            return "|" + output_json_dump


@dataclass(frozen=True, slots=True)
class TransactionSigned(Transaction):
    signature: str

    @classmethod
    def from_transaction(cls, t: Transaction, private_key: ec.EllipticCurvePrivateKey) -> Self:
        serialized = t.serialized_input_output().encode()
        signature = sign(serialized, private_key)
        return cls(t.input, t.output, signature)

    def is_valid(self) -> bool:
        serialized = self.serialized_input_output().encode()
        key = self.input.public_key if self.input else self.output.public_key
        try:
            verify(key, self.signature, serialized)
            return True
        except crypto_exceptions.InvalidSignature:
            return False


def eval_balance(
    transactions: Iterable[TransactionSigned], accounts: dict[str, int], miner_fee: int
):
    for trans in transactions:
        print(trans)
        input = trans.input
        output = trans.output
        # check signaged
        # check if ammount is the same as fee
        if not trans.is_valid():
            raise Exception("Transaction not valid")

        if not input:
            # mined
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
            payer_account_balance = accounts.get(payer_address)
            if not payer_account_balance:
                raise Exception("Non existing payer attempting to transfer")
            else:
                if payer_account_balance < expense:
                    raise Exception("Spending above amount")
                else:
                    if not accounts.get(output.public_key):
                        logging.warning("New or dead wallet")
                        accounts[payee_address] = 0
                    accounts[payee_address] += expense
                    accounts[payer_address] -= expense
    return accounts


# validate trans

# loop to find balances
# create dict with balances
