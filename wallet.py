import base64
import requests
import hashlib
from RSA_everything import to_sign_with_private_key, generate_keystore_file, import_keystore, generate_public_key



myNodeName = ''
transactions = []
firstnode = '127.0.0.1:5001'
connected_node = ''
your_keystore = ''
your_private_key = ''
your_public_key = ''
your_public_address = ''

######  RSA FUNCTIONS

def decode_signature(signature):
    
    decoded_signature = str(base64.b64encode(signature))
    decoded_signature = decoded_signature[:-1]
    decoded_signature = decoded_signature[2:]
    
    return decoded_signature

def encode_signature(decoded_signature):
    encoded_signature = bytes(base64.b64decode(decoded_signature)) 
    return encoded_signature  

######

def connect_to_network(myNodeName):
   global connected_node
   response = requests.get(f'http://{firstnode}/connect_wallet')
   print(response.json()['message'])
   connected_node = response.json()['node']
   myNodeJson = {
    "sender": myNodeName,
   }
   response = requests.post(f'http://{connected_node}/get_balance', json = myNodeJson)
   balance = response.json()['balance']
   return balance

def send_transaction(balance, send_amount, sender, receiver, your_private_key, your_public_key):
          
    
    transaction_string = sender + receiver + str(send_amount)
    signature = to_sign_with_private_key(transaction_string, your_private_key)  
    #print(signature)

    
    decoded_signature = decode_signature(signature)
    #encoded_signature = encode_signature(decoded_signature)
    #print(to_verify_with_public_key(encoded_signature, transaction_string, your_public_key))
    
    your_private_key = str(your_private_key.decode())
    your_public_key = str(your_public_key.decode())

    
    transaction = {
    "sender": sender,
    "receiver": receiver,
    "amount": send_amount,
    "signature" : decoded_signature,
    "sender_public_key": your_public_key
    }
    
    response = requests.post(f'http://{connected_node}/add_transaction', json = transaction)
    if response.status_code == 201:
        message = response.json()["message"] 
        if(message == 'Not enough funds'):
            print('Not enough funds')
        else: 
            print(f'Sent {send_amount} to receiver {receiver}')
            print(message)
  
def import_keystore_sequence(myNodeName):
    global your_keystore
    global your_private_key
    global your_public_key
    global your_public_address
    
    your_keystore = import_keystore(myNodeName)
    your_private_key = your_keystore.export_key()
    your_public_key = generate_public_key(your_keystore)
    your_public_address = hashlib.sha256(your_public_key).hexdigest()
    print(f'Your public address: {your_public_address}') 
    

generate_question = input("Generate new keystore? (y/n) ")
myNodeName = input("Enter your node name : ")

if generate_question == 'y':
    generate_keystore_file(myNodeName)

else:
    try:
        import_keystore_sequence(myNodeName)
    except:
        print(f'Missing keystore {myNodeName}.')
        generate_keystore_file(myNodeName)
        import_keystore_sequence(myNodeName)
 

while(True):
    
        try:
                
            balance = connect_to_network(your_public_address)
            print(f'Your balance: {balance} Ckc')
            receiver = input("Enter receiver address : ") 
            send_amount = float(input("Enter the amount you wish to send : "))   
            send_transaction(balance, send_amount, your_public_address, receiver, your_private_key, your_public_key)
            new_transaction = input("New transaction? (y/n) ")  
            if(new_transaction == 'n'):
                break
        except:
              print(f'Node {connected_node} was disconnected from the network, reconnecting to a new node.')