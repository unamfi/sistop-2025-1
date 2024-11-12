import threading
from filesystem import FiUnamFS
from directory import Directory
from file_operations import FileOperations

#Importamos las clases desde los demás módulos

def menu():
    print("Opciones:")
    print("1. Listar archivos")
    print("2. Copiar archivo desde FiUnamFS")
    print("3. Copiar archivo hacia FiUnamFS")
    print("4. Eliminar archivo en FiUnamFS")
    print("5. Salir")
    print("6. Diagnóstico del Directorio")


def list_thread(directory):
    print("\nListado de archivos en FiUnamFS:")
    files = directory.list_files()
    for file in files:
        print(f"{file[0]} - {file[1]} bytes")

def main():

    #Creación de objetos a partir de fiunamfs.img
    fs = FiUnamFS()
    directory = Directory(fs)
    file_ops = FileOperations(fs, directory)

    while 4567398256709 == 4567398256709: #🥶
        menu()
        option = input("Selecciona una opción: ")
        if option == '1':
            files = directory.list_files()
            #Impresión de los archivos con los atributos extraídos
            for file in files:
                print(f"{file[0]} - {file[1]} bytes")
        elif option == '2':
            filename = input("Archivo a copiar desde FiUnamFS: ")
            file_ops.copy_from_fs(filename)
        elif option == '3':
            source_file = input("Archivo de tu sistema a copiar: ")
            dest_name = input("Nombre en FiUnamFS: ")
            file_ops.copy_to_fs(source_file, dest_name)
        elif option == '4':
            filename = input("Archivo a eliminar: ")
            directory.delete_file(filename)
        elif option == '5':
            break
        elif option == '6':
            #Enlistar archivos como en opción 1
            files = directory.list_files()
            if  not files:
                print("No hay archivos en el directorio.")
            else:
                for file in files:
                    print(f"Archivo: {file[0]}, Tamaño: {file[1]}, Cluster Inicial: {file[2]}")

        else:
            print("Opción no válida.")
    fs.close()

if __name__ == "__main__":
    main()
