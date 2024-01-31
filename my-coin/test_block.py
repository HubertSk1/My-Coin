import os
from pprint import pprint
import json
import dataclasses
from Transactions import TransactionSigned, TransInput, TransOutput, eval_balance

my_pub_key = "sdfsfd"

other_keys = list(map(lambda x: str(x), range(5)))


def dummy_trans():
    t = TransactionSigned(None, TransOutput(my_pub_key, 50), 0, 0, "podpis")
    # pop first transaction (coinbase)
    # Sed 5 to others
    transactions = [t]
    sign = "podpis"
    for idx, account in enumerate(other_keys):
        amount = 2
        inp = TransInput(my_pub_key, amount)
        r = int(os.urandom(8))
        output = TransOutput(account, amount)
        # print(
        # inp
        # )
        # print(
        # output
        # )
        # print("Give everybody 2")
        tra = TransactionSigned(inp, output, r, idx, sign)
        transactions.append(tra)
    return transactions


def test_balance(dummy_trans: list[TransactionSigned]):
    transactions = dummy_trans
    # build balance
    accounts = {}
    miner_fee = 50
    eval_balance(transactions, accounts, miner_fee)

    print("###### Transactions")
    pprint(transactions)
    print("###### Balance")
    pprint(accounts)


def test_trans_serialized(dummy_trans: list[TransactionSigned]):
    transactions = dummy_trans
    for t in transactions:
        print(t)
        print("After serialized")
        print(t.serialized_input_output())
        print("#" * 5)

    t = transactions[-1]
    print(json.dumps(dataclasses.asdict(t), sort_keys=True, indent=None))


dummy_trans()
