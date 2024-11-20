import os  # Importa el módulo 'os' para interactuar con el sistema de archivos.
import struct  # Importa 'struct' para realizar conversiones entre cadenas de bytes y otros tipos de datos.

# Definición de constantes del sistema de archivos.
CLUSTER_SIZE = 1024  # Define el tamaño de cada clúster en bytes.
ENTRY_SIZE = 64  # Define el tamaño de cada entrada en el directorio.
DIR_START = CLUSTER_SIZE  # Establece el inicio del directorio en el primer clúster (clúster 1).
DIR_SIZE = 4 * CLUSTER_SIZE  # Define el tamaño del directorio (4 clústeres).
MAX_CLUSTERS = 1440 // 4  # Número máximo de clústeres asumido en 1440 KB de espacio total.

# Función para leer el superbloque de la imagen de sistema de archivos.
def read_superblock(image_path):
    with open(image_path, 'rb') as img:  # Abre la imagen en modo de lectura binaria.
        img.seek(0)  # Posiciona el cursor al inicio del archivo.
        fs_name = img.read(8).decode('ascii').strip()  # Lee y decodifica el nombre del sistema de archivos.
        img.seek(10)  # Posiciona el cursor en la posición 10.
        fs_version = img.read(5).decode('ascii').rstrip('\x00').strip()  # Lee y decodifica la versión del sistema.
        print(f"Sistema de archivos: {fs_name}, Versión: {fs_version}")  # Muestra el nombre y versión del sistema.
        
        # Verifica si los valores leídos coinciden con los esperados.
        if fs_name != "FiUnamFS" or fs_version != "25-1":
            print("Valores incorrectos, se esperaba FiUnamFS y 25-1")  # Mensaje si el nombre o versión no coinciden.
        else:
            print("Superbloque válido")  # Mensaje si el superbloque es válido.

# Función para listar los archivos del directorio en la imagen del sistema.
def list_directory(image_path):
    with open(image_path, 'rb') as img:  # Abre la imagen en modo de lectura binaria.
        img.seek(DIR_START)  # Posiciona el cursor al inicio del directorio.
        for _ in range(DIR_SIZE // ENTRY_SIZE):  # Itera sobre cada entrada del directorio.
            entry = img.read(ENTRY_SIZE)  # Lee una entrada completa.
            file_type = entry[0:1]  # Identifica el tipo de archivo (byte 0).
            name = entry[1:16].decode('ascii').rstrip()  # Extrae y decodifica el nombre del archivo (bytes 1-15).
            if file_type == b'.' and name:  # Verifica si la entrada representa un archivo válido.
                print(f"Archivo: {name}")  # Imprime el nombre del archivo.

# Función para extraer un archivo desde FiUnamFS al sistema local.
def extract_file(image_path, filename, destination):
    with open(image_path, 'rb') as img:  # Abre la imagen en modo de lectura binaria.
        img.seek(DIR_START)  # Posiciona el cursor al inicio del directorio.
        for _ in range(DIR_SIZE // ENTRY_SIZE):  # Itera sobre cada entrada del directorio.
            entry = img.read(ENTRY_SIZE)  # Lee una entrada completa.
            file_type = entry[0:1]  # Tipo de archivo (byte 0).
            if file_type == b'.':  # Verifica si la entrada es un archivo.
                # Extrae el nombre, tamaño y clúster inicial del archivo.
                name, size, start_cluster = (
                    entry[1:16].decode('ascii').rstrip(),
                    struct.unpack('<I', entry[16:20])[0],
                    struct.unpack('<I', entry[20:24])[0]
                )
                if name.strip() == filename.strip():  # Comprueba si el nombre coincide con el archivo deseado.
                    img.seek(start_cluster * CLUSTER_SIZE)  # Posiciona en el clúster inicial del archivo.
                    data = img.read(size)  # Lee los datos del archivo.
                    with open(destination, 'wb') as dest_file:  # Abre el archivo de destino en modo binario.
                        dest_file.write(data)  # Escribe los datos en el archivo de destino.
                    return
    raise FileNotFoundError("Archivo no encontrado en FiUnamFS")  # Error si no se encuentra el archivo.

# Función para agregar un archivo desde el sistema local a FiUnamFS.
def add_file(image_path, source_path, dest_name):
    with open(image_path, 'r+b') as img:  # Abre la imagen en modo lectura/escritura binaria.
        source_size = os.path.getsize(source_path)  # Obtiene el tamaño del archivo origen.
        next_free_cluster = 5  # Asume que el siguiente clúster libre es el 5.
        free_entry_pos = None  # Inicializa la posición de entrada libre como nula.

        img.seek(DIR_START)  # Posiciona el cursor al inicio del directorio.
        for _ in range(DIR_SIZE // ENTRY_SIZE):  # Itera sobre cada entrada del directorio.
            pos = img.tell()  # Guarda la posición actual.
            entry = img.read(ENTRY_SIZE)  # Lee una entrada completa.
            file_type = entry[0:1]  # Tipo de archivo (byte 0).
            entry_cluster = struct.unpack('<I', entry[20:24])[0]  # Extrae el clúster inicial.

            if file_type == b'#' and free_entry_pos is None:
                free_entry_pos = pos  # Guarda la posición de la primera entrada libre.

            if entry_cluster >= next_free_cluster:
                next_free_cluster = entry_cluster + 1  # Calcula el siguiente clúster libre.

        if free_entry_pos is None:
            raise Exception("No hay espacio en el directorio")  # Error si no hay entradas libres.
        
        with open(source_path, 'rb') as src_file:  # Abre el archivo origen en modo binario.
            img.seek(next_free_cluster * CLUSTER_SIZE)  # Posiciona en el clúster libre.
            img.write(src_file.read())  # Escribe el contenido del archivo en la imagen.

        img.seek(free_entry_pos)  # Posiciona en la entrada libre encontrada.
        img.write(b'.' + dest_name.ljust(15).encode('ascii'))  # Escribe el nombre del archivo en la entrada.
        img.write(struct.pack('<I', source_size))  # Guarda el tamaño del archivo.
        img.write(struct.pack('<I', next_free_cluster))  # Guarda el clúster inicial del archivo.

# Función para eliminar un archivo en FiUnamFS.
def delete_file(image_path, filename):
    with open(image_path, 'r+b') as img:  # Abre la imagen en modo lectura/escritura binaria.
        img.seek(DIR_START)  # Posiciona el cursor al inicio del directorio.
        for _ in range(DIR_SIZE // ENTRY_SIZE):  # Itera sobre cada entrada del directorio.
            pos = img.tell()  # Guarda la posición actual.
            entry = img.read(ENTRY_SIZE)  # Lee una entrada completa.
            name = entry[1:16].decode('ascii').rstrip()  # Extrae y decodifica el nombre del archivo.
            if name.strip() == filename.strip():  # Comprueba si el nombre coincide con el archivo a eliminar.
                img.seek(pos)  # Posiciona en la entrada del archivo.
                img.write(b'#' + b' ' * 15)  # Marca la entrada como eliminada.
                print("Archivo eliminado")  # Informa que el archivo fue eliminado.
                return
    raise FileNotFoundError("Archivo no encontrado en FiUnamFS")  # Error si no se encuentra el archivo.

# Función para desfragmentar el sistema de archivos.
def defragment_fs(image_path):
    entries = []  # Lista para almacenar entradas válidas.
    with open(image_path, 'r+b') as img:  # Abre la imagen en modo lectura/escritura binaria.
        img.seek(DIR_START)  # Posiciona el cursor al inicio del directorio.
        for _ in range(DIR_SIZE // ENTRY_SIZE):  # Itera sobre cada entrada del directorio.
            entry = img.read(ENTRY_SIZE)  # Lee una entrada completa.
            if entry[0:1] != b'#' and entry[1:16].strip(b' '):
                entries.append(entry)  # Almacena entradas válidas en la lista.

    entries.sort(key=lambda e: struct.unpack('<I', e[20:24])[0])  # Ordena las entradas por clúster inicial.
    current_cluster = 5  # Define el clúster inicial para desfragmentar.
    for entry in entries:
        name, size, start_cluster = (
            entry[1:16].decode('ascii').rstrip(),
            struct.unpack('<I', entry[16:20])[0],
            struct.unpack('<I', entry[20:24])[0]
        )

        img.seek(start_cluster * CLUSTER_SIZE)  # Posiciona en el clúster inicial.
        data = img.read(size)  # Lee los datos del archivo.
        img.seek(current_cluster * CLUSTER_SIZE)  # Posiciona en el nuevo clúster.
        img.write(data)  # Escribe los datos en el clúster actual.

        new_entry = (
            entry[0:20] + struct.pack('<I', current_cluster) + entry[24:]
        )
        img.seek(DIR_START + ENTRY_SIZE * entries.index(entry))
        img.write(new_entry)
        current_cluster += (size + CLUSTER_SIZE - 1) // CLUSTER_SIZE  # Avanza al siguiente clúster disponible.

    print("Desfragmentación completada.")  # Mensaje de finalización.

def presentar_datos():
    # Datos personales
    nombre = "Gabriela Aquino Lozada"
    facultad = "Facultad de Ingeniería"
    carrera = "Ingeniería en Computación"
    
    # Presentación de datos
    print("Nombre:", nombre)
    print("Facultad:", facultad)
    print("Carrera:", carrera)
    
# Menú principal para interacción con el usuario.
def main_menu():
    # Llamada a la función datos del autor
    presentar_datos()
    while True:
        print("\nMenú Principal - Sistema de Archivos FiUnamFS")
        print("1. Leer el superbloque")
        print("2. Listar directorio")
        print("3. Copiar archivo de FiUnamFS a sistema")
        print("4. Copiar archivo de sistema a FiUnamFS")
        print("5. Eliminar archivo de FiUnamFS")
        print("6. Salir")
        choice = input("Selecciona una opción: ")  # Solicita la opción del usuario.

        if choice == '1':
            read_superblock(image_path)
        elif choice == '2':
            list_directory(image_path)
        elif choice == '3':
            file_name = input("Nombre del archivo en FiUnamFS: ")
            dest_path = input("Ruta de destino en el sistema (dejar en blanco para carpeta actual): ")
            if not dest_path:
                dest_path = os.path.join(os.getcwd(), file_name)
            try:
                extract_file(image_path, file_name, dest_path)
                print("Archivo copiado con éxito a", dest_path)
            except Exception as e:
                print("Error al copiar el archivo:", e)
        elif choice == '4':
            src_path = input("Ruta del archivo en el sistema: ")
            dest_name = input("Nombre del archivo en FiUnamFS: ")
            add_file(image_path, src_path, dest_name)
        elif choice == '5':
            file_name = input("Nombre del archivo a eliminar de FiUnamFS: ")
            delete_file(image_path, file_name)
        elif choice == '6':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

image_path = "fiunamfs.img"  # Ruta de la imagen de sistema de archivos.
main_menu()  # Llama al menú principal para iniciar el programa.
