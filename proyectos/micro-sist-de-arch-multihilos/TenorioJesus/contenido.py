import os
from datetime import datetime

def contenido_archivo(archivo):

    A = [" ","-",":"] #Arreglo para guardar caracteres que vamos a elimiar de la fecha

    # Obtenemos contenido del archivo
    with open(archivo, 'r') as file:
        content = file.read()

    _ , name = os.path.split(archivo) # Obtenenemos el nombre del archivo

    # Obtenemos la fecha de creación del archivo
    fecha_creacion = os.path.getctime(archivo)

    fecha = str(datetime.fromtimestamp(fecha_creacion))

    i = 0

    for letra in fecha: #Eliminamos cadenas no deseados
        if letra == ".":
            fecha = fecha[0:i]
            break
        i = i+1
    
    for simbolo in A: #Eliminaos caracteres no deseados 
        fecha = fecha.replace(simbolo,'')
    
    return content,fecha,name 


if __name__ == "__main__":
    contenido_archivo("C:\\Users\\tenor\\OneDrive\\Escritorio\\FI\\Sistemas_Operativos\\Proyecto1\\proyecto.py")