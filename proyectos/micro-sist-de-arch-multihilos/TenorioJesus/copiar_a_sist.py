import struct
from pathlib import Path

"""""
CODIGO QUE COPEA UN ARCHIVO DESDE FIUNAMFS HACIA EL SISTEMA DE ARCHIVOS DEL USUARIO

PRIMERO DEFINIMOS EL TAMAÑO DE CADA CLUSTER Y DEL OFFSET INICIAL DEL DIRECTORIO

BUSCAMOS EN LAS ENTRADA DEL DIRECORIO Y COMPROBAMOS EL NOMBRE DE LOS ARCHIVOS, SI 
COINCIDE CON nombre_archivo SE HE ENCONTRADO

DESPUES SE OBTIENE EL TAMAÑI DEL ARCHIVO Y EL CLUSTER INICIAL, MEDIATE STRUCT.UNPACK

DESPUES MOVEMOS EL CURSOR HACIA EL CLUSTER INICIAL, Y LEEMOS LOS DATOS 

Y YA DESPUES ESCRIBIMOS EL CONTENIDO EN UN ARCHIVO EN UNA RUTA ESPECIFICADO
"""""

def copiar_archivo_a_sistema(disco, nombre_archivo, destino):

    size = 1024
    inicio = 1024

    # BuscaMOS el archivo en el directorio
    encontrado = False
    for i in range(4 * (size // 64)):  # 4 clusters de directorio, cada entrada tiene 64 bytes
        disco.seek(inicio + i * 64)
        entry = disco.read(64)
            
        # Tipo de archivo
        tipo = entry[0]
        if tipo != ord('.'):
            continue  # Si no es un archivo valido, pasar a la siguiente entrada
        
        # Nombre del archivo
        nombre = entry[1:14].decode('ascii')
        if nombre.strip() != nombre_archivo.strip():
            continue
        
        # Tamaño del archivo y cluster inicial
        tamano = struct.unpack('<I', entry[16:20])[0]
        clusterInicial = struct.unpack('<I', entry[20:24])[0]
        encontrado = True
        break
    
    if not encontrado:
        print("Archivo no encontrado en FiUnamFS.")
        return

    # Leemos los datos del archivo
    disco.seek(clusterInicial * size)  # vamos al cluster inicial de datos
    datos = disco.read(tamano)

    Ruta_destino = Path(destino)

    # Escribimos los datos en un nuevo archivo en el sistema
    with Ruta_destino.open('wb') as salida:
        salida.write(datos)
        
    print(f"\nArchivo '{nombre_archivo}' copiado a '{destino}'\n")