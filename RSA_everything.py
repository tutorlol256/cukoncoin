from Crypto.PublicKey import RSA
import Crypto.Signature.PKCS1_v1_5 as sign_PKCS1_v1_5  # For signature/Verify Signature
from Crypto.Cipher import PKCS1_v1_5  # For encryption
from Crypto import Random
from Crypto import Hash


def encrypt_with_rsa(message, my_public_key):
 
    #First Public Key Encryption
    cipher_pub_obj = PKCS1_v1_5.new(RSA.importKey(my_public_key))
    encrypted_message = cipher_pub_obj.encrypt(message.encode())
    
    return encrypted_message
 
def decrypt_with_rsa(encrypted_message, my_private_key ):
 
    #Post-private key decryption
    cipher_pri_obj = PKCS1_v1_5.new(RSA.importKey(my_private_key))
    decrypted_message = cipher_pri_obj.decrypt(encrypted_message, Random.new().read)
    message = decrypted_message.decode()
 
    return message

def to_sign_with_private_key(message, my_private_key):
 
    #Private key signature
    signer_pri_obj = sign_PKCS1_v1_5.new(RSA.importKey(my_private_key))
    rand_hash = Hash.SHA256.new()
    rand_hash.update(message.encode())
    signature = signer_pri_obj.sign(rand_hash)
    print('Message signed with private key, signature generated!')
    #print(signature)
    
    return signature
 
def to_verify_with_public_key(signature, message, my_public_key):
 
    #Public Key Verification
    verifier = sign_PKCS1_v1_5.new(RSA.importKey(my_public_key))
    _rand_hash = Hash.SHA256.new()
    _rand_hash.update(message.encode())
    verify = verifier.verify(_rand_hash, signature)
    
    return verify #true / false
 

    
def generate_keystore_file(keystore_owner):
    
    x = RSA.generate(1024,  Random.new().read)
    private_key = x.export_key()
    with open(f'Keys/{keystore_owner}_keystore.pem', "wb") as x:
        x.write(private_key)
        print(f'Generated new keystore file: {keystore_owner}_keystore.pem')
        #print(private_key)
 
def import_keystore(keystore_owner):
    with open(f'Keys/{keystore_owner}_keystore.pem','rb')as x:
        private_key = RSA.importKey(x.read())
        print(f'Imported keystore file: {keystore_owner}_keystore.pem')
        #print(private_key.export_key())
        return private_key

def generate_public_key(private_key):
    public_key = private_key.publickey()
    #print(public_key.export_key())
    return public_key.export_key()


# GENERATE KEYSTORE
#generate_keystore_file('Gandalf')
    
# IMPORT KEYSTORE
"""
receiver_keystore = import_keystore('Gandalf')
receiver_private_key = receiver_keystore.export_key()
receiver_public_key = generate_public_key(receiver_keystore)


sender_keystore = import_keystore('Frodo')
sender_private_key = sender_keystore.export_key()
sender_public_key = generate_public_key(sender_keystore)

message = 'Neka tajna poruka'
"""
# MESSAGE ENCRYPTION 
"""
encrypted_message = encrypt_with_rsa(message, receiver_public_key)

print(f'Encrypted message: {encrypted_message} with receiver public key: {receiver_public_key}')  

message_decrypted = decrypt_with_rsa(encrypted_message, receiver_private_key )

print(f'Decrypted message: {message_decrypted}')

"""

#SIGN AND VERIFY WITH SIGNATURE
"""
signature = to_sign_with_private_key(message, sender_private_key)

#message = 'Neka tajna poruka promijenjena'
if(to_verify_with_public_key(signature, message, sender_public_key)):
    print("Signature Valid!")
else:
    print("Message was tampered with!")
""" 


