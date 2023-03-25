from cryptography.fernet import Fernet
import os

key = os.environ['FERNET']
fernet = Fernet(key)

# decrypting
print("Loading crypted files...")

def decrypt(fileName):
	with open(fileName,"rb") as file:
		ctext = file.read()
		text = fernet.decrypt(text)
	with open(f'{fileName.split(".")[0]}.py', 'wb') as file:
		file.write(text)

files = ["cservice.cpy","cBot.cpy","cTrader.cpy"]
for i in files:
	decrypt(i)

print("Files decrypted.")