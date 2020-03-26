    def read_file(self):
        print("Reading file for transactions")
        f = open("./transactions/trans" + str(self.id)[-1] + ".txt", "r")
        for j in range(5):
            node_id, value = (f.readline()).split()
            for nodes in self.ring:
                if nodes["id"] == node_id[2:]:
                    receiver = nodes["public_key"]
                    break    
            self.create_transaction(self.public ,receiver, int(value))
                #break
        return
