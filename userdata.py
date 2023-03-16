from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json
import os


class UserData:
    def __init__(self, email, password):
        load_dotenv()
        self.email = email
        self.password = password
        self.file_path = "data/userdata.txt"
        self.encryption_key = os.getenv("ENCRYPTION_KEY")

    def configure_file(self):
        f = Fernet(self.encryption_key)
        with open(self.file_path, 'r+') as file:
            contents = file.read()
            if contents == "":
                json_template = {"accounts": []}
                data = f.encrypt(json.dumps(json_template).encode(encoding='utf-8'))
                file.write(str(data)[2:-1])
                print("Successfully Encrypted Template Data")

    def create_account(self, username):
        f = Fernet(self.encryption_key)
        with open(self.file_path, 'r+') as file:
            contents = file.read()
            data = f.decrypt(contents)
            decryptedData = json.loads(data)
            # print(decryptedData)
            if self.email == "" or self.password == "" or username == "":
                return {"code": 400, "msg": "Unable to create account"}

            if decryptedData['accounts']:  # already stored account data
                for i in decryptedData['accounts']:
                    if i['email'] == self.email:
                        return {"code": 403, "msg": "Email is already in use"}
                    elif i['username'] == username:
                        return {"code": 403, "msg": "Username is already in use"}
                # If this account is unique, its created
                self.write_account(decryptedData, username)
                return {"code": 201, "msg": "Account Created!"}
            else:  # First account added
                self.write_account(decryptedData, username)
                return {"code": 201, "msg": "Account Created!"}

    def write_account(self, decryptedData, username):
        f = Fernet(self.encryption_key)
        with open(self.file_path, "w") as file:
            decryptedData['accounts'].append(
                {"email": self.email, "password": self.password, "username": username}
            )
            json_str = json.dumps(decryptedData)
            print(decryptedData)
            encryptedData = f.encrypt(json_str.encode(encoding='utf-8'))
            print(encryptedData)
            file.write(str(encryptedData)[2:-1])  # [2:-1] bc we don't want b''

    def login(self):
        f = Fernet(self.encryption_key)
        # Add login detection
