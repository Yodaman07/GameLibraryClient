from cryptography.fernet import Fernet
from dotenv import load_dotenv
from platforms import ValidateCredentials
import json
import os


class UserData:
    def __init__(self, email="", password="", username=""):
        load_dotenv()

        self.email = email
        self.password = password
        self.username = username
        self.file_path = "data/userdata.txt"
        self.encryption_key = os.getenv("ENCRYPTION_KEY")

        self.configure_file()

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
        if self.email == "" or self.password == "":
            raise InvalidCredentialsError("email_pswrd")

        f = Fernet(self.encryption_key)
        with open(self.file_path, 'r+') as file:
            contents = file.read()
            data = f.decrypt(contents)
            decryptedData = json.loads(data)
            # print(decryptedData)
            if self.email == "" or self.password == "" or username == "":
                return {"code": 400, "msg": "Unable to create account", "user": None}

            if decryptedData['accounts']:  # already stored account data
                for i in decryptedData['accounts']:
                    if i['email'] == self.email:
                        return {"code": 403, "msg": "Email is already in use", "user": None}
                    elif i['username'] == username:
                        return {"code": 403, "msg": "Username is already in use", "user": None}
                # If this account is unique, its created
                self.write_account(decryptedData, username)
                return {"code": 201, "msg": "Account Created!", "user": username}
            else:  # First account added
                self.write_account(decryptedData, username)
                return {"code": 201, "msg": "Account Created!", "user": username}

    def write_account(self, decryptedData, username):
        f = Fernet(self.encryption_key)
        with open(self.file_path, "w") as file:
            decryptedData['accounts'].append(
                {"email": self.email, "password": self.password, "username": username, "accountData": []}
            )
            json_str = json.dumps(decryptedData)
            print(decryptedData)
            encryptedData = f.encrypt(json_str.encode(encoding='utf-8'))
            print(encryptedData)
            file.write(str(encryptedData)[2:-1])  # [2:-1] bc we don't want b''

    def login(self):
        if self.email == "" or self.password == "":
            raise InvalidCredentialsError("email_pswrd")
        loggedIn = False
        f = Fernet(self.encryption_key)
        with open(self.file_path, "r") as file:
            contents = file.read()
            data = f.decrypt(contents)
            decryptedData = json.loads(data)
            if decryptedData['accounts']:
                for i in decryptedData['accounts']:
                    if i['email'] == self.email and i['password'] == self.password:
                        loggedIn = True
                        return {"code": 200, "msg": "Successfully logged in!", "user": i['username']}
                if not loggedIn:
                    return {"code": 401, "msg": "Your email or password is incorrect", "user": None}
            return {"code": 400, "msg": "Error finding account", "user": None}

    def service(self, method, service):
        if self.username == "":
            raise InvalidCredentialsError("")
        updatedData = False
        response = {}
        f = Fernet(self.encryption_key)
        with open(self.file_path, "r+") as file:
            contents = file.read()
            data = f.decrypt(contents)
            decryptedData = json.loads(data)
            # print(decryptedData)
            if decryptedData['accounts']:
                for i in decryptedData['accounts']:
                    if i['username'] == self.username:  # finds current account
                        if method == "add":  # service data is dictionary
                            serviceType = service['type']
                            # code below validates service credentials
                            vc = ValidateCredentials(service['data'])
                            if serviceType == 'steam':
                                response = vc.validateSteam(os.getenv("STEAM_API_KEY"))
                            elif serviceType == 'xbox':
                                response = vc.validateXbox()

                            if response['code'] == 202: # 202 is the valid code
                                for j in i['accountData']:  # searches through all of the service credentials
                                    if j['type'] == serviceType:  # overwrites existing data
                                        j['data'] = service['data']
                                        updatedData = True
                                if not updatedData:  # adds new data
                                    i['accountData'].append(service) # service can be seen in settings/app.js
                                    updatedData = True

                        elif method == "get":  # service data is service name
                            responseFound = False
                            if i['accountData']:
                                for j in i['accountData']:
                                    if j['type'] == service:
                                        response = {"code": 202, "msg": j['data']}
                                        responseFound = True
                                if not responseFound:
                                    response = {"code": 404, "msg": "Requested service not found. Use the 'add' "
                                                                    "method to add data to the desired account"}
                            else:
                                response = {"code": 404,
                                            "msg": "No services found. Use the 'add' method to add data to the "
                                                   "desired account"}
        if updatedData:
            with open(self.file_path, "w") as file:
                json_str = json.dumps(decryptedData)
                # print(decryptedData)
                encryptedData = f.encrypt(json_str.encode(encoding='utf-8'))
                file.write(str(encryptedData)[2:-1])  # [2:-1] bc we don't want b''

        return response


class InvalidCredentialsError(Exception):
    def __init__(self, errortype):
        self.msg = "Invalid Credentials; You are missing the email and password" if errortype == "email_pswrd" else "Invalid Credentials; You are missing the username"
        super().__init__(self.msg)
