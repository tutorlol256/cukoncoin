

# Importing the libraries
import datetime
import hashlib
import base64
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
from timeit import default_timer as timer
import threading
import random
from numpy import random
from RSA_everything import to_verify_with_public_key
#import time

node_address = str(uuid4()).replace('-', '')
myNodeIp = '127.0.0.1:5002'
myNodeName = 'Frodo'
reward_address = '558fe4ed58c8cda6e048ac3766705eca80ddb846648e3c293571d7f1c08fe9dd'
firstnode = '127.0.0.1:5001'
difficulty = '000'
reward_rate = 100000
mark_length = 0

# Creating a Web App
app = Flask(__name__)





#Blockchain class

class Blockchain:

    current_hash = ''
    mined_block_time = 0
    previous_block_reward = 0
    blockchain_chunk_time = 0
    blockhain_chunk_size = 10
    block_timestamp = ''

    
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.transaction_queue = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
             
     
    #if there is no transactions dont mine block
    def create_block(self, proof, previous_hash):
       
        if len(self.transactions) > 1 : 
            block = {'index': len(self.chain) + 1,  
                     'hash' : self.current_hash,
                     'timestamp': self.block_timestamp,
                     'proof': proof,
                     'previous_hash': previous_hash,
                     'transactions': self.transactions,
                     'mined block time': mined_block_time}
            
            self.chain.append(block)
            self.transactions = []
            return block
        
        if  len(self.chain) == 0 : 
            block = {'index': len(self.chain) + 1,
                     'hash' : 'genesis_hash',
                     'timestamp': str(datetime.datetime.now()),
                     'proof': proof,
                     'previous_hash': previous_hash,
                     'transactions': self.transactions,
                     'mined block time': 0}
                       
            genesis_transaction = {
                "sender": 'genesis',
                "receiver": 'a55ea87bb966a9c4c0f9ab82ec096e95a8ba1878aafa3070c4de4c4d5201e3f5',
                "amount": 1000,
                }
            self.transactions.append(genesis_transaction)
            self.chain.append(block) 
            self.transactions = []              
            return block
        
        else:
            self.transactions = []
            return 'Transaction rejected'
            
        
    def get_previous_block(self):
        return self.chain[-1]

    #timed proof of work reward reverse proportional to the time spent on mining
    def timed_proof_of_work(self, previous_proof, previous_hash):
        
        global previous_block_reward
        global mined_block_time
        global difficulty
        
        new_proof =1 
        
                       
        check_proof = False
        while check_proof is False:  
            start = timer()
            self.block_timestamp = str(datetime.datetime.now())
            current_block = {'index': len(self.chain) + 1,
                             'timestamp': str(self.block_timestamp),                         
                             'proof': new_proof,
                             'previous_hash': previous_hash,
                             'transactions': self.transactions}

            hash_operation = self.hash(current_block)
            #DIFFICULTY      
            #print(hash_operation)
            if hash_operation[:len(difficulty)] == difficulty:
                self.current_hash = hash_operation
                check_proof = True
                end = timer()
                time_elapsed = end - start
                #calculate reward reverse proportional to time
                reward = 1/(time_elapsed * reward_rate)
                
                self.previous_block_reward = reward
                mined_block_time = time_elapsed
                #print(f'Time elapsed to mine block {time_elapsed} reward : {reward}')
            else:
                new_proof = random.randint(1000)
        
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def calculate_reward_rate(self):
        global reward_rate
        self.calculate_blockchain_time()
        print('Reward rate adjusted')
        average_block_time = self.blockchain_chunk_time/len(self.chain)
        print(f'Average block time: {average_block_time}')
        reward_rate = 1/average_block_time
        print(f'Reward rate: {reward_rate}')

    def calculate_blockchain_time(self):
        
        for i in range(mark_length, mark_length + self.blockhain_chunk_size):
            block = self.chain[i]
            self.blockchain_chunk_time += block['mined block time']

    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            
            tmp_current_block = {
                            'index': block['index'],
                            'timestamp': block['timestamp'],
                            'proof': block['proof'],
                            'previous_hash': block['previous_hash'],
                            'transactions': block['transactions']
                            }
            
            #print(block['previous_hash'])
            #print(self.hash(previous_block))
            if block['previous_hash'] != self.hash(previous_block) :
                return False
            #previous_proof = previous_block['proof']
            #proof = block['proof']
            hash_operation = self.hash(tmp_current_block)
    
            if hash_operation[:len(difficulty)] != difficulty or hash_operation != block['hash']:
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_to_transaction_queue(self, sender, receiver, amount):
        self.transaction_queue.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1    
    
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        network_copy = network.copy()
        longest_chain = None
        longest_node = None
        max_length = len(self.chain)
        for node in network:
            if node != myNodeIp:
                try:
                    response = requests.get(f'http://{node}/get_chain')
                    if response.status_code == 200:
                        length = response.json()['length']
                        chain = response.json()['chain']
                        if length > max_length and self.is_chain_valid(chain):
                            max_length = length
                            longest_chain = chain
                            longest_node = node
                except :   
                       network_copy.remove(node)
                       print(f'Node {node} disconnected')
                       print(f'New list of nodes: {network_copy}')
                       
        network = network_copy
        if longest_chain:
            self.chain = longest_chain
            print(f'Longer chain detected on node: {longest_node}, your chain was replaced.')
            return True
        return False
 
    #check blockchain if there is enough funds before adding transaction
    def check_balance(self, sender): 
       transactions = []
       chain = self.chain
       balance = 0
       for block in chain:       
           transactions.append(block['transactions'])              
                
       for transactionList in transactions:
           for transaction in transactionList:
               stringTransaction = json.dumps(transaction)
               jsonTransaction = json.loads(stringTransaction)
               
               amount = jsonTransaction["amount"]
               receiver_chain = jsonTransaction["receiver"]
               sender_chain = jsonTransaction["sender"]
    
               if receiver_chain == sender:
                   balance += amount
            
               if sender_chain == sender:
                   balance -= amount      
                   
       return balance

       
###################################################################
    #methods

def mine_blocks():
    
    #invoke reward rate recalculation 
    global mark_length
    if (len(blockchain.chain) - blockchain.blockhain_chunk_size >= mark_length ):      
        blockchain.calculate_reward_rate()
        mark_length = len(blockchain.chain)
        blockchain.blockchain_chunk_time = 0
    
    #pop transaction from que and check balance
    transaction = blockchain.transaction_queue.pop(0)
    sender = transaction['sender']
    send_amount = transaction['amount']       
    balance = blockchain.check_balance(sender)
    new_balance = balance - send_amount
    if(new_balance) >= 0:
        blockchain.transactions.append(transaction)

    #create new block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']   
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = reward_address,
                               amount = blockchain.previous_block_reward)
    proof = blockchain.timed_proof_of_work(previous_proof, previous_hash) 
    block = blockchain.create_block(proof, previous_hash)
    if block != 'No transactions in block':
        new_block = {
                    'index': block['index'],
                    'hash' : block['hash'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash'],
                    'transactions': block['transactions'],
                    'mined block time': block['mined block time']
                    }
        print('New block mined!')
        print(new_block)
        
        #distribute it to the network
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            new_block_index = block['index']
            print(f'Block {new_block_index} orphaned!')
            
        else:
            network_copy = blockchain.nodes.copy()
            print(f'Time elapsed to mine block {mined_block_time} reward : {blockchain.previous_block_reward}')
            for node in blockchain.nodes:
                try:
                    if node != myNodeIp:
                        response = requests.post(f'http://{node}/add_new_block', json = new_block)
                        if response.status_code == 201:
                           #print(f'Block number {new_block_index} distributed to the node with ip: {node}!')
                            print(f'New block distributed')
                except :   
                       network_copy.remove(node)
                       #print(f'Node {node} disconnected')
                       
            blockchain.nodes = network_copy
            #print(f'New list of nodes: {blockchain.nodes}')
    else:
         print(block)    
                    

#send my ip to first node get list of nodes connected to it and send my ip to the rest of the nodes from the list 
def connect_to_network():
   
   my_node = {
    'nodeIp': myNodeIp,
    'nodeName': myNodeName,
   }
     
   blockchain.nodes.add(myNodeIp)
   
   if firstnode != '':
       request = requests.post(f'http://{firstnode}/add_new_node', json = my_node)
       if request.status_code == 201:
           json = request.json()
           blockchain.nodes = set(json.get('nodeList'))       
           message = json.get('message')
           print(message)
           print(f' Received nodes: {blockchain.nodes}')
           
           if len(blockchain.nodes) > 0:
               for node in blockchain.nodes:
                   if node != myNodeIp and node != firstnode: #safe switch for double
                       request = requests.post(f'http://{node}/add_new_node', json = my_node)
                       if request.status_code == 201:
                           json = request.json()
                           #add recieved nodes from all nodes
                           newNodes = set(json.get('nodeList'))
                           blockchain.nodes = blockchain.nodes.union(newNodes) 
                           message = json.get('message')
                           print(message)
                           print(f' Received nodes: {blockchain.nodes}')
                           
def start_mining():
    
    while(True):
        #time.sleep(10)
        if len(blockchain.transaction_queue) >= 1 : 
            mine_blocks()
                            
def mining_thread():   
    monitoring_thread = threading.Thread(target = start_mining)
    monitoring_thread.daemon=True
    monitoring_thread.start()

def download_chain():
    chain_downloaded = blockchain.replace_chain()
    if chain_downloaded:
        print('Blockchain is downloaded')
        
def encode_signature(decoded_signature):
    encoded_signature = bytes(base64.b64decode(decoded_signature)) 
    return encoded_signature            



# getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount', 'signature', 'sender_public_key']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400

    send_amount = json.get('amount')
    sender = json.get('sender')
    receiver = json.get('receiver')
    signature = encode_signature(json.get('signature'))
    sender_public_key = str.encode(json.get('sender_public_key')) 
    transaction_string = sender + receiver + str(send_amount)
    #print(signature)
    #print(sender_public_key)
    if(to_verify_with_public_key(signature, transaction_string, sender_public_key)):
        
        balance = blockchain.check_balance(sender)
        new_balance = balance - send_amount
        if(new_balance) >= 0:
            blockchain.add_to_transaction_queue(json['sender'], json['receiver'], json['amount'])
            print("Signature valid, transaction added!")
            response = {'message': f'This transaction was added to transaction queue, position in queue: {len(blockchain.transaction_queue)}'     
                       }
        else: 
            response = {'message': f'Not enough funds'}
        return jsonify(response), 201
    else:
        message = {'message': "Transaction was tampered with!"}
        print(message)
        return jsonify(message), 201



#add new node sent from connect_to_netwok method and return list of nodes that this node contains
@app.route('/add_new_node', methods = ['POST'])
def add_new_node():
    json = request.get_json()
    nodeIp = json.get('nodeIp')
    nodeName = json.get('nodeName')
    
    
    blockchain.nodes.add(nodeIp)
    print(f'Node connected! {nodeName} with ip {nodeIp}')
    print(f'Network contains the following nodes: {blockchain.nodes}')
    response = {'message': f'Your node is connected to the node {myNodeName} with ip: {myNodeIp}',
                'nodeList': list(blockchain.nodes)
               }
    return jsonify(response), 201

@app.route('/connect_wallet', methods = ['GET'])
def connect_wallet():
    
    #get random node from nodes list
    
    random_node = random.choice(list(blockchain.nodes))
    response = {'message': f'Your node is connected to the node with ip: {random_node}',
                'node': random_node
               }
    return jsonify(response), 201

@app.route('/add_new_block', methods = ['POST'])
def add_new_block():
    block = request.get_json()
   
    blockchain.chain.append(block)
    print(f'Recieved new block : {block}')
    response = {'message': 'New block added.'
               }
    return jsonify(response), 201


@app.route('/get_balance', methods = ['POST'])
def get_balance():
    json = request.get_json()

    sender = json.get('sender')
    balance = blockchain.check_balance(sender)

    response = {'balance': f'{balance}'
               }

    return jsonify(response), 201


#instantiate blockchain
blockchain = Blockchain()


# Running the app
connect_to_network()
download_chain()
mining_thread()
app.run(host = '0.0.0.0', port = 5002)
