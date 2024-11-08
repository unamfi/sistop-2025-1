import re

"""""
ESTE PROGRAMA SIMPLEMENTE RECONOCE DIRECTORIOS QUE EL USUARIO
INGRESARA EN ALGUN PUNTO

"""""
def Reconocer(entrada):

    # Expresion regular para identificar directorios
    patron = r'"([^"]+)"'

    # funcion para encontrar las rutas
    rutas = re.findall(patron, entrada)

    if len(rutas) == 2:
        # Separamos y obetenemos las dos rutas obtenidas
        ruta_origen, ruta_destino = rutas

        return ruta_origen, ruta_destino
    
    else: 
        return -1