from cryptography.fernet import Fernet

class Encryptor:
    def __init__(self):
        self.__key__ = Fernet.generate_key()

    def encrypt(self,value):
        cipher = Fernet(self.__key__)
        return cipher.encrypt(value.encode("utf-8"))

    def decrypt(self,value):
        cipher = Fernet(self.__key__)
        return cipher.decrypt(value).decode("utf-8")

if __name__ == "__main__":
    encryptor = Encryptor()
    token = encryptor.encrypt("thePassword")
    print(token)
    decrypted = encryptor.decrypt(token)
    print(decrypted)
