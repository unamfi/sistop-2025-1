import getpass
from time import localtime, strftime

print(f"Hola %s, son las %s"% (getpass.getuser(), strftime("%H:%M:%S", localtime())))