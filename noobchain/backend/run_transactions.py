import requests
import json
import sys 
import time

## RUN: sudo python3 main.py 5
## OR 
## RUN: sudo python3 main.py 10

if len(sys.argv) > 1:
    no_of_nodes = sys.argv[1]
else:
    sys.exit('Please give the number of nodes as argument (e.g.: 5 or 10).')

id_to_address = {"id0":"http://0.0.0.0:1000", "id1":"http://0.0.0.0:2000", "id2":"http://0.0.0.0:3000", "id3":"http://0.0.0.0:4000", "id4":"http://0.0.0.0:5000"}

print("Reading file for transactions")
for i in range(0,int(no_of_nodes)):
    f = open("../transactions/" + no_of_nodes  + "nodes/transactions" + str(i) + ".txt", "r")
    for j in range(15):
        node_id, value = (f.readline()).split()
        print(node_id)
        print(value)
        data = {"sender_address":"id"+str(i), "receiver_address":node_id, "amount":value}
        response = requests.post(id_to_address["id"+str(i)]+"/transactions/create", json=json.dumps(data))
        print (response)
        time.sleep(1)
    f.close()

