import struct

"""""
ESTE PROGRAMA MUESTRA LOS ARCHIVOS Y SUS CARACTERISTICAS SIMULANDO UNA VENTANA DE UN
SISTEMA WINDOWS, MUESTRA EL MODO DE LECTURA (INVENTADOS PUES NO SE PIDIO COMO REQUISITO),
LA FECHA Y HORA DE LA ULTIMA MODIFICACION, LONGITUD Y NOMBRE
"""""

def mostrarArchivos(fiunamfs):

    NameFiles = []

    print("Mode                 LastWriteTime         Length Name")
    # No olvidando los directorios . y ..
    print("----                 -------------         ------ ----")
    print("----                 ------------          10      .")
    print("----                 ------------          11      ..")

    for i in range(4 * ((4*256) // 64)):  # Cada entrada del directorio ocupa 64 bytes
        entry = fiunamfs.read(64)
        
        # Tipo de archivo
        tipo = entry[0]
        if tipo == ord('#'):  # Entrada vacía
            continue
            
        # Leemos nombre del archivo
        nombre = entry[1:14].decode('ascii').strip('-').strip()
        NameFiles.append(nombre)

        # Leemos tamaño del archivo
        tamano = struct.unpack('<I', entry[16:20])[0]

        fecha_modificacion = entry[38:52].decode('ascii', errors='replace')

        # Imprimimos detalles del archivo
        if tamano != 0 and nombre.strip() != '#':
           
            print(f"-a---l     {fecha_modificacion[0:4]}\{fecha_modificacion[4:6]}\{fecha_modificacion[6:8]}   {fecha_modificacion[8:10]}:{fecha_modificacion[10:12]}:{fecha_modificacion[12:14]}        {tamano} {nombre}")

    print("\n")

    # Regresamos el arrglo para buscar en otros metodos
    return NameFiles 
