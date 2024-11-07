import os
from datetime import datetime

def contenido_archivo(archivo):

    A = [" ","-",":"]

    # Obtener contenido del archivo
    with open(archivo, 'r') as file:
        content = file.read()

    _ , name = os.path.split(archivo)

    # Obtener la fecha de creación del archivo
    fecha_creacion = os.path.getctime(archivo)

    fecha = str(datetime.fromtimestamp(fecha_creacion))

    i = 0

    for letra in fecha:
        if letra == ".":
            fecha = fecha[0:i]
            break
        i = i+1
    
    for simbolo in A:
        fecha = fecha.replace(simbolo,'')
    
    return content,fecha,name


if __name__ == "__main__":
    contenido_archivo("C:\\Users\\tenor\\OneDrive\\Escritorio\\FI\\Sistemas_Operativos\\Proyecto1\\proyecto.py")