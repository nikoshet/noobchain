import requests
import json

id_to_address = {"id1":"http://127.0.0.1:2000", "id0":"http://127.0.0.1:1000"}

print("Reading file for transactions")
for i in range(0,2):
    f = open("../transactions/trans" + str(i) + ".txt", "r")
    for j in range(5):
        node_id, value = (f.readline()).split()
        print(node_id)
        print(value)
        data = {"sender_address":"id"+str(i), "receiver_address":node_id, "amount":value}
        response = requests.post(id_to_address["id"+str(i)]+"/transactions/create", json=json.dumps(data))
        print (response)
    f.close()

