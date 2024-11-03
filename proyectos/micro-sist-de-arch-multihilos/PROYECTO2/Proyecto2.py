# Creado por:
#
#Martínez Pavón María Guadalupe 

import struct  # Módulo para manejar conversiones entre enteros y bytes en formato little endian
import threading  # Módulo para manejar concurrencia con hilos


class FiUnamFS:
    def __init__(self, filename):
        """
        Inicializa el sistema de archivos FiUnamFS.

        :param filename: Nombre del archivo que simula el diskette de 1440 KB.
        """
        self.filename = filename  # Nombre del archivo que representa el sistema de archivos
        self.lock = threading.Lock()  # Lock para manejar la sincronización entre hilos
        self.init_fs()  # Llama a la función para inicializar el sistema de archivos

    def init_fs(self):
        """
        Inicializa el archivo del sistema de archivos y lo llena con ceros para simular
        el tamaño de 1440 KB. Luego, escribe el superbloque.
        """
        with open(self.filename, 'wb') as f:
            f.write(b'\x00' * 1440 * 1024)  # Escribe 1440 KB de ceros en el archivo
        self.write_superblock()  # Escribe el superbloque al inicio del archivo

    def write_superblock(self):
        """
        Escribe la información del superbloque en el primer cluster del archivo.
        Incluye el nombre del sistema de archivos, la versión, y otros campos clave.
        """
        with open(self.filename, 'r+b') as f:
            f.seek(0)  # Posiciona el cursor al inicio del archivo
            f.write(b'FiUnamFS')  # Escribe el nombre del sistema de archivos (8 bytes)
            f.seek(10)  # Posiciona el cursor en la posición 10
            f.write(b'25-1')  # Escribe la versión (5 bytes)
            # Aquí puedes agregar más lógica para escribir el tamaño del cluster y otros detalles

    def list_contents(self):
        """
        Lista los archivos en el directorio del sistema de archivos.
        Esta función debe recorrer las entradas del directorio y mostrar los archivos activos.
        """
        with self.lock:  # Bloquea el acceso al archivo para garantizar seguridad en concurrencia
            # TODO: Implementar la lógica para listar los contenidos del directorio
            pass

    def delete_file(self, file_name):
        """
        Elimina un archivo del sistema de archivos marcándolo como vacío
        y liberando los clusters asignados.

        :param file_name: Nombre del archivo a eliminar.
        """
        with self.lock:  # Bloquea el acceso al archivo para garantizar seguridad en concurrencia
            # TODO: Implementar la lógica para eliminar el archivo y liberar el espacio
            pass


# Instancia del sistema de archivos con el nombre del archivo simulado
fs = FiUnamFS("fiunamfs.img")

# Crea dos hilos de ejecución
thread1 = threading.Thread(target=fs.list_contents)  # Hilo para listar los contenidos
thread2 = threading.Thread(target=lambda: fs.delete_file("archivo.txt"))  # Hilo para eliminar un archivo

# Inicia los hilos
thread1.start()
thread2.start()

# Espera a que los hilos terminen
thread1.join()
thread2.join()



