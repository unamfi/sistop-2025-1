"""""
FUNCION PARA ELIMINAR UN ARCHIVO EN EL SISTEMA FIUNAMFS

SE BUSCA EL ARCHIVO Y MARCA LA ENTRADA COMO VACIA (SE CAMBIA EL CARACTER A #)

SOLO SE MARCA LA ENTRADA, NO SE LIMPIA EL CLUSTER 

RECORREMOS CADA UNA DE LAS ENTRADAS DEL DIRECTORIO, VERIFCANDO SI LLEGA A COINCIR CON EL ARCHIVO 
A BORRAR 
UNA VEZ QUE SE ENCUENTRA LA ENTRADA SE MARCA COMO VACIA Y SE IMPRIME UN MENSAJE DE CONFIRMACION
PARA INDICAR O NO QUE SE ELIMINO EL ARCHIVO :)
"""""

def eliminar_archivo(disco, nombre_archivo):
    cluster_size = 1024  # Tamaño del cluster
    inicio_directorio = 1024  # Offset donde comienza el directorio
    encontrado = False

    # Recorremos cada entrada en el directorio para encontrar el archivo
    for i in range(4 * (cluster_size // 64)):  # 4 clusters de directorio, cada entrada ocupa 64 bytes
        disco.seek(inicio_directorio + i * 64)
        entry = disco.read(64)
        
        # Leemos el tipo de archivo y nombre
        tipo = entry[0]
        nombre = entry[1:14].decode('ascii').strip()
        
        # Verificamos si es el archivo que queremos eliminar
        if tipo == ord('.') and nombre.strip() == nombre_archivo.strip():
            # Marcamos la entrada como vacía, sobrescribiendo el tipo
            disco.seek(inicio_directorio + i * 64)
            disco.write(b'#')  # Indicamos entrada vacía
            encontrado = True
            print(f"Archivo '{nombre_archivo}' eliminado exitosamente.")
            break

    if not encontrado:
        print(f"Archivo '{nombre_archivo}' no encontrado en FiUnamFS.")