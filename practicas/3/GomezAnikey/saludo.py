import sys

if len(sys.argv) > 1:
    nombre = sys.argv[1]
else:
    nombre = "Mundo"

print(f"Hola {nombre}")
