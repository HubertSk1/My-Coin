import hashlib as hash
import json
import logging
from pprint import pprint

from block import *

my_pub_key = "sdfsfd"

other_keys  = list(map(lambda x: str(x), range(5)))

def test_trans():
    t = TransactionSigned(None,TransOutput(my_pub_key, 50), "podpis")
    # pop first transaction (coinbase)
    # Sed 5 to others
    firs = TransInput(my_pub_key,2)
    transactions = [t]
    sign = "podpis"
    for account in other_keys:
        amount = 2
        inp = TransInput(my_pub_key,amount)
        output = TransOutput(account,amount)
        print(
            inp
        )
        print(
            output
        )
        print("Give everybody 2")
        tra = TransactionSigned(inp, output, sign)
        transactions.append(tra)

    # build balance
    accounts = eval_balance(transactions)
            

    
    print("###### Transactions")
    pprint(transactions)
    print("###### Balance")
    pprint(accounts)