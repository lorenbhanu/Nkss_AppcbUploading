# from Crypto.Cipher import AES
# import base64
# def get_aes(secret_key):
#     key_bytes = secret_key.encode('utf-8')[:32]
#     arr_iv = b'\x00' * 16
#     return AES.new(key_bytes, AES.MODE_CBC, iv=arr_iv)


# def encrypte(plainbytes,key):
#     return(key.encrypt(plainbytes))
# def encrypt(data,key):
#     plainbytes = str(data).encode('utf-8')
#     keyy=get_aes(key)
#     return(base64.b64encode(encrypte(plainbytes,keyy)))

# def decrypt(data,key):
#     keyy=get_aes(key)
#     data=base64.b64decode(data)
#     return(keyy.decrypt(data))
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom
import base64

def get_aes(secret_key):
    key_bytes = secret_key.encode('utf-8')[:32]
    arr_iv = b'\x00' * 16
    return Cipher(algorithms.AES(key_bytes), modes.CBC(arr_iv), backend=default_backend())

def encrypt(data, key):
    plainbytes = str(data).encode('utf-8')
    keyy = get_aes(key).encryptor()
    ciphertext = keyy.update(plainbytes) + keyy.finalize()
    return base64.b64encode(ciphertext)

def decrypt(data, key):
    keyy = get_aes(key).decryptor()
    ciphertext = base64.b64decode(data)
    decrypted = keyy.update(ciphertext) + keyy.finalize()
    return decrypted.decode('utf-8')
