import re

def Reconocer(entrada):

    patron = r'"([^"]+)"'

    rutas = re.findall(patron, entrada)

    if len(rutas) == 2:
        ruta_origen, ruta_destino = rutas

        print(f"Ruta origen: {ruta_origen} \n Ruta destino: {ruta_destino}")
        return ruta_origen, ruta_destino
    
    else: 
        return -1