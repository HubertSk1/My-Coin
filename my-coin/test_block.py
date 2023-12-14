import hashlib as hash
from pprint import pprint
from Transactions import *

my_pub_key = "sdfsfd"

other_keys  = list(map(lambda x: str(x), range(5)))

def dummy_trans():
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
        # print(
            # inp
        # )
        # print(
            # output
        # )
        # print("Give everybody 2")
        tra = TransactionSigned(inp, output, sign)
        transactions.append(tra)
    return transactions

def test_balance(dummy_trans):
    transactions: list[TransactionSigned] = dummy_trans
    # build balance
    accounts = {}
    minner_fee = 50
    eval_balance(transactions, accounts, 50)
            
    print("###### Transactions")
    pprint(transactions)
    print("###### Balance")
    pprint(accounts)

def test_trans_serialized(dummy_trans):
    transactions: list[TransactionSigned] = dummy_trans
    for t in transactions:
        print(t)
        print("After serialized")
        print(t.serialized_input_output())
        print("#" * 5)
        
    t = transactions[-1]
    print(
        json.dumps(
        dataclasses.asdict(t),
        sort_keys=True,
        indent=None))
    
dummy_trans()