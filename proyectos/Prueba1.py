import os
import time

# Función para buscar un archivo por su nombre dentro del sistema de archivos.
# Retorna el tamaño del archivo y el cluster inicial si se encuentra, o 0, 0 si no existe.
def buscarArchivo(nombre, fs, cl_size):
    """Busca un archivo por nombre y devuelve su tamaño y cluster inicial."""
    fs.seek(cl_size)  # Posiciona el puntero en el inicio del área de directorio
    for i in range(0, cl_size * 4, 64):  # Itera en bloques de 64 bytes
        fs.seek(cl_size + i)
        arch = fs.read(16).decode("utf-8").strip()[:-1]  # Lee el nombre del archivo
        if arch == nombre:  # Si el archivo coincide con el nombre buscado
            size = int(fs.read(9).decode("utf-8")[:-1])  # Lee el tamaño del archivo
            start_cl = int(fs.read(6).decode("utf-8")[:-1])  # Lee el cluster inicial
            return size, start_cl
    return 0, 0  # Retorna 0, 0 si el archivo no se encuentra

# Función para listar el contenido del sistema de archivos.
def listarContenido(fs, cl_size):
    """Lista todos los archivos en el directorio del sistema de archivos."""
    print("\n\n   << LISTA DE CONTENIDO >>\n")
    fs.seek(cl_size)  # Posiciona el puntero en el inicio del área de directorio
    for i in range(0, cl_size * 4, 64):  # Itera en bloques de 64 bytes
        fs.seek(cl_size + i)
        arch = fs.read(16).decode("utf-8")  # Lee el nombre del archivo
        if arch[:15] != "Xx.xXx.xXx.xXx.":  # Verifica si no es un archivo eliminado
            print(f"\n---> Archivo: {arch.strip()[:-1]}")
            size = int(fs.read(9).decode("utf-8")[:-1])  # Lee el tamaño del archivo
            start_cl = int(fs.read(6).decode("utf-8")[:-1])  # Lee el cluster inicial
            print(f"     Tamaño: {size} | Cluster inicial: {start_cl}")

# Función para copiar un archivo desde el sistema de archivos hacia el sistema operativo local.
def copiarASistema(fs, cl_size):
    """Copia un archivo desde el sistema de archivos a tu sistema."""
    print("\n\n   << COPIAR HACIA EL SISTEMA >>\n")
    nombre = input("Nombre del archivo a copiar: ")
    size, start_cl = buscarArchivo(nombre, fs, cl_size)  # Busca el archivo en el sistema de archivos

    if size == 0:  # Verifica si el archivo no fue encontrado
        print("El archivo no se encontró en FiUnamFS.")
    else:
        print(f"\n---> Archivo encontrado: {nombre}")
        print(f"     Tamaño: {size} | Cluster inicial: {start_cl}")
        # Crea un nuevo archivo en el sistema operativo y copia los datos desde el sistema de archivos
        with open("(Desde FiUnamFS)" + nombre, "wb") as new_file:
            fs.seek(cl_size * start_cl)  # Posiciona el puntero en el cluster inicial
            new_file.write(fs.read(size))  # Copia los datos al archivo local
        print("\n¡Archivo copiado con éxito!")

# Función para calcular el inicio del siguiente cluster
def siguienteCluster(start_cl, size, cl_size):
    """Calcula el inicio del siguiente cluster."""
    sobra = size % cl_size
    return (start_cl) * 1024 + size + (1024 - sobra)

# Función para encontrar el primer espacio libre en el área de directorio
def espacioDirectorio(fs, cl_size):
    """Busca el primer espacio libre en el directorio."""
    fs.seek(cl_size)  # Posiciona el puntero en el área de directorio
    for i in range(0, cl_size * 4, 64):  # Itera en bloques de 64 bytes
        fs.seek(cl_size + i)
        arch = fs.read(16).decode("utf-8")  # Lee el nombre del archivo
        if arch[:15] == "Xx.xXx.xXx.xXx.":  # Busca un espacio marcado como vacío
            return cl_size + i  # Retorna la posición del espacio libre
    return -1  # Retorna -1 si no hay espacio disponible

# Función para buscar un cluster disponible para un archivo de tamaño específico
def clusterDisponible(size, fs, cl_size, fs_size):
    """Busca un cluster disponible para un archivo de un tamaño específico."""
    fs.seek(cl_size)
    data = []
    for i in range(0, cl_size * 4, 64):  # Lee la información de archivos existentes
        fs.seek(cl_size + i)
        arch = fs.read(16).decode("utf-8").strip()[:-1]
        if arch[:15] != "Xx.xXx.xXx.xXx.":
            file_size = int(fs.read(9).decode("utf-8")[:-1])
            start_cl = int(fs.read(6).decode("utf-8")[:-1])
            data.append((start_cl, file_size))
    
    data.sort(key=lambda x: x[0])  # Ordena los archivos por su cluster inicial

    for i in range(len(data)):
        next_cl = siguienteCluster(data[i][0], data[i][1], cl_size)
        if i == len(data) - 1:
            free_space = fs_size - next_cl
        else:
            next_start = data[i+1][0] * 1024
            free_space = next_start - next_cl
        if free_space >= size:
            return next_cl  # Retorna el inicio del cluster disponible
    return -1  # Retorna -1 si no hay espacio suficiente

# Función para copiar un archivo desde el sistema operativo local hacia FiUnamFS
def copiarAFiUnamFS(fs, fs_size, cl_size):
    """Copia un archivo desde el sistema al sistema de archivos FiUnamFS."""
    print("\n\n   << COPIAR HACIA FIUNAMFS >>\n")
    nombre = input("Nombre del archivo a copiar: ")

    if len(nombre) > 15:  # Verifica que el nombre no sea demasiado largo
        print("El nombre del archivo no puede ser mayor a 15 caracteres.")
        return

    if not os.path.isfile(nombre):  # Verifica que el archivo existe en el sistema operativo
        print("El archivo no existe o es inválido.")
        return

    size = os.stat(nombre).st_size  # Obtiene el tamaño del archivo
    dir_space = espacioDirectorio(fs, cl_size)  # Busca un espacio libre en el directorio

    if dir_space == -1:  # Si no hay espacio en el directorio
        print("El directorio está lleno.")
        return

    start_cl = clusterDisponible(size, fs, cl_size, fs_size)  # Busca un cluster libre
    if start_cl == -1:  # Si no hay espacio en el sistema de archivos
        print("No hay espacio disponible.")
        return

    # Escribe la información del archivo en el sistema de archivos
    fs.seek(dir_space)
    fs.write("                ".encode("utf-8"))
    fs.seek(dir_space)
    fs.write((nombre + ".").encode("utf-8"))

    fs.seek(dir_space + 16)
    fs.write("000000000".encode("utf-8"))
    str_size = f"{size}."
    fs.seek(dir_space + 16 + (9 - len(str_size)))
    fs.write(str_size.encode("utf-8"))

    fs.seek(dir_space + 25)
    fs.write("000000".encode("utf-8"))
    str_start = f"{int(start_cl / 1024)}."
    fs.seek(dir_space + 25 + (6 - len(str_start)))
    fs.write(str_start.encode("utf-8"))

    str_date = time.strftime("%Y%m%d%H%M%S", time.localtime()) + "."
    fs.seek(dir_space + 31)
    fs.write(str_date.encode("utf-8"))

    fs.seek(dir_space + 46)
    fs.write(str_date.encode("utf-8"))

    # Copia el contenido del archivo
    with open(nombre, "rb") as f:
        fs.seek(start_cl)
        fs.write(f.read())

    print("Archivo copiado con éxito.")

# Función para eliminar un archivo del sistema de archivos FiUnamFS
def eliminarDeFiUnamFS(fs, cl_size):
    """Elimina un archivo del sistema de archivos."""
    print("\n\n   << ELIMINAR ARCHIVO >>\n")
    nombre = input("Nombre del archivo a eliminar: ")

    fs.seek(cl_size)
    for i in range(0, cl_size * 4, 64):
        fs.seek(cl_size + i)
        arch = fs.read(16).decode("utf-8").strip()[:-1]
        if arch == nombre:  # Si el archivo es encontrado
            fs.seek(cl_size + i)
            fs.write("Xx.xXx.xXx.xXx.".encode("utf-8"))  # Marca el archivo como eliminado
            print("Archivo eliminado con éxito.")
            return
    print("Archivo no encontrado.")

# Función principal que muestra el menú y gestiona las opciones
def main():
    sector_size = 256
    cl_size = sector_size * 4

    with open("fiunamfs/fiunamfs.img", "r+b") as fs:
        while True:
            fs_size = os.stat("fiunamfs").st_size
            print("\n<< MENU >>")
            print("1. Listar contenido")
            print("2. Copiar archivo a sistema")
            print("3. Copiar archivo a FiUnamFS")
            print("4. Eliminar archivo")
            print("5. Salir")
            opt = input("Opción: ")

            if opt == "1":
                listarContenido(fs, cl_size)
            elif opt == "2":
                copiarASistema(fs, cl_size)
            elif opt == "3":
                copiarAFiUnamFS(fs, fs_size, cl_size)
            elif opt == "4":
                eliminarDeFiUnamFS(fs, cl_size)
            elif opt == "5":
                break
            else:
                print("Opción inválida.")

main()