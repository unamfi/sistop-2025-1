import getpass
from time import gmtime, strftime

print(f"Hola %s, son las %s"% (getpass.getuser(), strftime("%H:%M:%S", gmtime())))