from cryptography.fernet import Fernet
import os

key = os.environ['FERNET']
fernet = Fernet(key)

# decrypting
print("Loading crypted files...")
f = open("Strategies.enc","rb")
text = f.read()
f.close()
f = open("Strategies.py","wb")
f.write(fernet.decrypt(text))
f.close()

from cryptography.fernet import Fernet
import os

key = os.environ['FERNET']
fernet = Fernet(key)

def decrypt(fileName):
	with open(fileName,"rb") as file:
		ctext = file.read()
		text = fernet.decrypt(text)
	with open(f'{fileName.split(".")[0]}.py', 'wb') as file:
		file.write(text)

files = ["service.cpy","Bot.cpy","Trader.cpy"]
for i in files:
	decrypt(i)

print("Files decrypted.")