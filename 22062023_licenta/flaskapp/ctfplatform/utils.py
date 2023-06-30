import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import datetime


session_token = None
ALLOWED_EXTENSIONS = {"tgz"}
def init():
    password = b"CTFplatForm123!"
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
        backend=default_backend()
    )
    token = base64.urlsafe_b64encode(kdf.derive(password))

    fernet = Fernet(token)
    
    return fernet, token

session_token = None
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkFudm12WWVmN1g0YV94Z1lwUFZTMFN2a2ozU3BIUGR0QU9peHcyVUNGZ3MifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJjdGZzcGFjZSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJjdGZwbGF0Zm9ybS1zZWNyZXQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiY3RmcGxhdGZvcm1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjkwNzQzZWYyLTJlNzktNDJhZC1hMDEzLWRmMjU1ZjU2YTQ1ZCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpjdGZzcGFjZTpjdGZwbGF0Zm9ybXNhIn0.pBY8em8EZv1_I28j6dGtFNtuiLwYkg6LqrhQ87CqmmBUgWrxwcCIx_fGvqwTQL-jvWH912dtRGVa4bjApUiPCK3v0mSHZCSBcK6gBBqaHyCK0-E54aDdMbnozozbqXty7roHrtHxBrthtOUmIWBLF1ZVcbcUbmUdqIAo-9WpMIXxjID5cQ30ajHLmd5kRcsmJ1kdbUrTDzecQJWMRKvNhwr_Q8o-c2fXtz8uojE_FBq1txesPe5IxXpR_OVeutr0EgeJoxKzYiMseKnGSZU7RvnLcHNFxLhcD5ccZ6kMpP9ec58dFphHnZP41xNHdbRwOZymRDqUJikReeyI3Xvdbg"
deployment_template_path = "ctfplatform/manifest_templates/deployment_template.yaml"
service_template_path = "ctfplatform/manifest_templates/service_template.yaml"
namespace_template_path = "ctfplatform/manifest_templates/namespace_template.yaml"
secret_template_path = "ctfplatform/manifest_templates/secret_template.yaml"
ready_manifests_folder_path = "ctfplatform/manifest_templates/manifests/"


def append_new_line(file_name, text_to_append):
    with open(file_name, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(text_to_append)

def encrypt_data(data):
    try: 
        fernetInst, session_token = init()
        ciphertext = fernetInst.encrypt(bytes(data,'utf-8'))
        return ciphertext, session_token
    except Exception as e:
        raise Exception(f"Error: encrypting: {e}")
    
def decrypt_data(ciphertext, session_token): 
    try:
        fernetInst = Fernet(session_token)
        decrypted_data = fernetInst.decrypt(ciphertext)

        return decrypted_data
    except InvalidToken or TypeError  as e:
        raise Exception(f"Error: decrypting: {e}")

def get_sa_token():
    return token

def format_timestamp():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M %d-%m-%Y")
    return formatted_time

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
