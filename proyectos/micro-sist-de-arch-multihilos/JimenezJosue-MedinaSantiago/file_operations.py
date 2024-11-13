from filesystem import FiUnamFS
from directory import Directory

class FileOperations:
    def __init__(self, fs, directory):
        self.fs = fs
        self.directory = directory

    def copy_from_fs(self, filename):
        #Obtener lista de archivos en el directorio usando list_files de Directory
        try:
            files = self.directory.list_files()
            print("Archivos en el directorio:", files)

            file_found = False 
            #Eliminamos espacios en blanco del nombre del archivo por copiar
            filename_cleaned = filename.strip()

            #Buscar el archivo ingresado en la lista
            for file in files:
                #Remplazamos \x00 por espacios para eliminarlos
                file_name_cleaned = file[0].replace('\x00', '').strip()

                #Verificar si el nombre coincide con el archivo por copiar
                if file_name_cleaned == filename_cleaned:
                    file_found = True
                    cluster_num = file[2]
                    #Tamaño del archivo
                    filesize = file[1]

                    #Leer todos los clústeres necesarios para el archivo
                    data = b""
                    bytes_read = 0

                    try:
                        while bytes_read < filesize:
                            #Leer el clúster actual
                            cluster_data = self.fs.read_cluster(cluster_num)
                            data += cluster_data
                            bytes_read += len(cluster_data)

                            #Si hemos leído el tamaño completo del archivo, salir
                            if bytes_read >= filesize:
                                data = data[:filesize]
                                break

                            #Obtener el siguiente clúster
                            cluster_num = self.fs.get_next_cluster(cluster_num)
                            if cluster_num is None:
                                #Termina si no hay más clústeres, llegamos al final
                                break

                        #Escribir el archivo en el sistema de archivos actual, manejando excepciones
                        with open(filename_cleaned, 'wb') as f:
                            f.write(data)
                        print(f"Archivo {filename_cleaned} copiado exitosamente.")
                    except Exception as e:
                        print(f"Error al leer el clúster o escribir el archivo: {e}")
                    return

            #Variable booleana file_found False, archivo no encontrado
            if not file_found:
                print(f"Archivo {filename_cleaned} no encontrado en el directorio.")
        except Exception as e:
            print(f"Error al intentar listar archivos: {e}")

    def copy_to_fs(self, source_file, dest_name):
        #dest_name es el nombre en fiunamfs
        try:
            with open(source_file, 'rb') as f:
                data = f.read()
                #Seleccionamos un cluster de datos libre
                cluster_num = 5
                self.fs.write_cluster(cluster_num, data)
                if self.directory.add_file(dest_name, len(data), cluster_num):
                    print(f"Archivo {source_file} copiado como {dest_name}.")
                else:
                    print("Error al añadir al directorio.")
        except FileNotFoundError:
            print("Archivo de origen no encontrado")
