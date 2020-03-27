import random

n_nodes = 3
n_transactions = 2

for node in range(n_nodes):
    with open(f'trans{node}.txt', 'w') as file:
        for trans in range(n_transactions):
            id_to_send = None
            while id_to_send==None:
                id_to_send = random.randint(0,n_nodes-1)
                print (id_to_send)
                if id_to_send==node:
                    id_to_send = None
            file.write(f'id{id_to_send} {random.randint(1, 10)}\n')
