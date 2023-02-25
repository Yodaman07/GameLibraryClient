from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json
import os


class UserData:
    def __init__(self, username, password):
        load_dotenv()
        self.username = username
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

    def create_account(self):
        accountExists = False
        f = Fernet(self.encryption_key)
        with open(self.file_path, 'r+') as file:
            contents = file.read()
            data = f.decrypt(contents)
            decryptedData = json.loads(data)
            # print(decryptedData)
            if self.username or self.password == "":
                if decryptedData['accounts']:
                    for i in decryptedData['accounts']:
                        if i['username'] == self.username:
                            accountExists = True
                    if not accountExists:
                        self.write_account(decryptedData)
                    else:
                        return "Email is already in use"
                else:
                    self.write_account(decryptedData)
            return "Unable to create account"

    def write_account(self, decryptedData):
        f = Fernet(self.encryption_key)
        with open(self.file_path, "w") as file:
            decryptedData['accounts'].append(
                {"username": self.username, "password": self.password}
            )
            json_str = json.dumps(decryptedData)
            # print(decryptedData)
            encryptedData = f.encrypt(json_str.encode(encoding='utf-8'))
            # print(encryptedData)
            file.write(str(encryptedData)[2:-1])
