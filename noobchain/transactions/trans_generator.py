import random

n_nodes = 2
n_transactions = 5

for node in range(n_nodes):
    with open(f'trans{node}.txt', 'w') as file:
        for trans in range(n_transactions):
            file.write(f'id{abs(n_nodes-node-1)} {random.randint(1, 10)}\n')
