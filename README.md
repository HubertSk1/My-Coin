# WHAT WE HAVE SO FAR

* PEER TO PEER
1. Working Peer-to-Peer (websockets)
2. Key generation base on pass phrase
3. Signatures
4. Signatue Verification

* SIMPLE BLOCKCHAIN
1. Creating blocks
2. Verifing blocks
3. Data exchange in jsons
4. The Nodes syncronize every time the block is added to any node (BroadCasting)
5. Consesus (checking which chain is longer and  is it valid)

* TRANSACTIONS
1. <span style="color:red">Creating Transactions (list of jsons)</span>

LISTA TRANSAKCJI trzymana w Liście w Nodzie, dodawana do Blockchainu. 

2. <span style="color:red">Validate in case of double-spending</span>

LISTA nodów z  jakimiś pięniedzmi
GDY DODAJESZ TRANSAKCJE TO trzeba zweryfikować czy już nie jest wydana w proposed  

3. <span style="color:red">Calculating balances</span>

FUNKCJA (Blockchain + adres) -> ile on ma coinów.

* ASYNC MINE
1. Handling Forks and Orphan Blocks
W Momencie sync UTX powinny być liczone, transakcje z orphan bloków powinny zostać dodane do listy pending transacitons
2. Creating Forks by a Malicious Node
3. <span style="color:red">Broadcasting Transactions and Candidate Blocks with Probability</span>



# TODO 
1. KLASA DO TRANSAKCJI - Patryk 
2. FUNKCJA DO WERYFIKACJI BALANCÓW  
3. FUnckja do weryfikcjaji czy przychodząca transakcja jest poprawna (double spending, in >0)
4. Broadcastowanie transkacji - Hubert 