import struct
from datetime import datetime

"""
FUNCION QUE ESCRIBE UN ARCHIVO EN FIUNAMFS

SE ASIGNA AL PRIMER CLSUTER DISPONIBLE
SE IMPLEMENTA UNA VERIFICACION EN CASO DE QUE NO EXISTA ESPACIO EN EL SISTEMA FIUNAMFS
EL TAMAÑO MAXIMO DE UN ARCHIVO ES DE 15 B, PORQUE TIENE ASIGNADO [1-15]
CLUSTER INICIAL: 4 BYTES
FECHA Y HORA: 14 B
"""

def copiar_archivo_a_Fiunamfs(disco,nombre_archivo,contenido,fecha):

    contenido = contenido.encode(encoding="utf-8")

    # Tamaños y offsets
    cluster_size = 1024
    inicio_directorio = 1024  # Offset donde empieza el directorio
    max_nombre = 15  # Tamaño maximo de nombre
    encontrado = False #Bandera util

    # no aceptar si el nombre es demasiado largo 
    if len(nombre_archivo) > max_nombre:
        print("\n El nombre es demasiado largo!")
        return

    # Buscar una entrada vacia en el directorio
    for i in range(4 * (cluster_size // 64)):  # Directorio tiene 4 clusters de 64 bytes por entrada
        # Posicionamos la cabeza en la sig entrada
        disco.seek(inicio_directorio + i * 64)
        # Leemos la entrada
        entry = disco.read(64)

        # Verificamos si la entrada es vacia
        if entry[0] == ord('#') or entry == 35:

            # Posicionamos en la entrada vacia encontrada
            disco.seek(inicio_directorio + i * 64)

            # 0 Tipo de archivo (1 byte)
            disco.write(b'.')  # Indicador de archivo válido

            # 1-15 Nombre del archivo 
            nombre_formateado = nombre_archivo.ljust(max_nombre)
            disco.write(nombre_formateado.encode('ascii'))

            # 16-19 Tamaño del archivo (4 bytes)
            tamano = len(contenido)
            disco.write(struct.pack('<I', tamano))

            # 20-23 Cluster inicial (4 bytes)
            # Usamos el primer cluster disponible 
            cluster_inicial = 4  
            disco.write(struct.pack('<I', cluster_inicial))

            # 24-37 Fecha y hora de creacion (14 bytes en formato AAAAMMDDHHMMSS)
            disco.write(fecha.encode('ascii'))

            # 38-51 Fecha y hora de última modificacion (14 bytes en formato AAAAMMDDHHMMSS)
            fecha_modificacion = datetime.now().strftime('%Y%m%d%H%M%S') #Con esta linea se puede ajustar el 
            # formato de fecha (recomendado por chatgpt)
            disco.write(fecha_modificacion.encode('ascii'))

            # 52-63 Espacio reservado (12 bytes)
            disco.write(b'\x00' * 12)  # Espacio reservado vacío

            encontrado = True # Activamos Bandera

            break
    
    # En caso de no encontrar espacio, la bandera sera falsa
    if not encontrado:
            print("No hay espacio en el directorio para un nuevo archivo.")
            return

    # Escribimos los datos en el cluster de datos correspondiente
    disco.seek(cluster_inicial * cluster_size)
    disco.write(contenido[:tamano])

    print(f"Archivo '{nombre_archivo}' escrito exitosamente en FiUnamFS.")
