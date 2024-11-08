import os
import subprocess
import time
from datetime import datetime
import math
import getpass
import threading
import queue


username = getpass.getuser()

file_names = []
file_content_locator = []
file_sizes = []

file_system_name = 'FiUnamFS'
file_system_version = '25-1'
volume_tag = 'FiUnamFS.img' 
cluster_length = 1024
num_of_clusters_dir = 4
num_of_clusters_unit = 1440
init_dir = 1024
info_size = 64

disk_name = 'FiUnamFS.img'
actual_pointer = init_dir

limit_of_files = 16
no_file_name = '---------------'
no_size = 0
no_init_cluster = 0
no_date = '00000000000000'


def create_file_system_disk():
    global file_system_name, file_system_version
    global volume_tag, cluster_length, num_of_clusters_dir, num_of_clusters_unit
    global actual_pointer, no_file_name, no_size, no_init_cluster, no_date

    insert_bytes(0,  8,  file_system_name)
    insert_bytes(10, 14, file_system_version)
    insert_bytes(20, 35, volume_tag)
    insert_bytes(40, 44, cluster_length)
    insert_bytes(45, 49, num_of_clusters_dir)
    insert_bytes(50, 54, num_of_clusters_unit)

    for i in range(limit_of_files):
        insert_bytes(actual_pointer + 1,  actual_pointer + 15, no_file_name)
        insert_bytes(actual_pointer + 16, actual_pointer + 20, no_size)
        insert_bytes(actual_pointer + 20, actual_pointer + 23, no_init_cluster)
        insert_bytes(actual_pointer + 24, actual_pointer + 37, no_date)
        insert_bytes(actual_pointer + 38, actual_pointer + 51, no_date)
        actual_pointer = actual_pointer + 64


def get_existing_files():
    global disk_name
    file_system_disk = open(disk_name,'r')
    actual_pointer_aux = init_dir
    while actual_pointer_aux < 5120:
        file_system_disk.seek(actual_pointer_aux)
        query = file_system_disk.read(15)
        if query != 'AQUI_NO_VA_NADA':
            file_names.append(query.replace(" ",""))
            file_system_disk.seek(actual_pointer_aux+16)
            file_sizes.append(int(file_system_disk.read(8)))
            file_position = 0 
            for i in range(len(file_content_locator)):
                file_position += file_sizes[i] + 4
            file_position += 5120
            file_content_locator.append(file_position)
        actual_pointer_aux = actual_pointer_aux + 64
    file_system_disk.close()


def insert_bytes(init_byte, limit_byte, word):
    if len(word) < (limit_byte - init_byte):
        word = word.rjust(limit_byte - init_byte, ' ')  # Asegura que la longitud sea correcta
    with open(disk_name, 'r+b') as file_system_disk:
        file_system_disk.seek(init_byte)
        file_system_disk.write(word.encode('ascii'))


def copy_from_computer_to_disk(route, queue):
    global disk_name
    global init_dir, file_content_locator
    file_name = os.path.basename(route)
    sizeof_file = str(os.path.getsize(route))
    init_cluster = str(int((file_content_locator[-1] + file_sizes[-1]) / 1024)) if file_content_locator else '5'
    c_date = time.strftime('%Y%m%d%H%M%S', time.gmtime(os.path.getctime(route)))
    m_date = time.strftime('%Y%m%d%H%M%S', time.gmtime(os.path.getmtime(route)))

    try:
        with open(route, 'rb') as computer_file, open(disk_name, 'r+b') as file_system_disk:
            file_content = computer_file.read()
            actual_pointer_for_insert = init_dir
            while True:
                file_system_disk.seek(actual_pointer_for_insert)
                query = file_system_disk.read(15)
                if query == 'AQUI_NO_VA_NADA':
                    insert_bytes(actual_pointer_for_insert, actual_pointer_for_insert + 15, file_name)
                    insert_bytes(actual_pointer_for_insert + 16, actual_pointer_for_insert + 24, sizeof_file)
                    insert_bytes(actual_pointer_for_insert + 25, actual_pointer_for_insert + 30, init_cluster)
                    insert_bytes(actual_pointer_for_insert + 31, actual_pointer_for_insert + 45, c_date)
                    insert_bytes(actual_pointer_for_insert + 46, actual_pointer_for_insert + 60, m_date)
                    sum_file_sizes = sum(file_sizes) + 5120
                    file_content_locator.append(sum_file_sizes)
                    insert_bytes(sum_file_sizes, sum_file_sizes + os.path.getsize(route), file_content)
                    file_names.append(file_name)
                    file_sizes.append
                    break
                actual_pointer_for_insert += 64
        print(f"Archivo {file_name} copiado desde la computadora a FiUnamFs")
        
    except Exception as e:
        print(f"Error al copiar el archivo: {e}")
    
    # Enviar mensaje a la cola para otras operaciones
    queue.put(f"Archivo {file_name} copiado exitosamente.")


def copy_from_disk_to_computer(file_name, queue):
    global disk_name
    new_file = open(file_name, 'w')
    file_system_disk = open(disk_name, 'r')
    file_position = file_names.index(file_name)
    file_size = file_sizes[file_position]
    file_pointer = file_content_locator[file_position]
    file_system_disk.seek(file_pointer)
    new_file.write(file_system_disk.read(file_size))
    file_system_disk.close()
    new_file.close()
    queue.put(f"Archivo {file_name} copiado desde FiUnamFS a la computadora.")


def delete_file(file_name, queue):
    global disk_name
    global no_file_name, no_size, no_init_cluster, no_date
    actual_pointer_for_delete = init_dir
    file_system_disk = open(disk_name, 'r+', encoding='latin-1')
    flag = 0
    while flag == 0: 
        file_system_disk.seek(actual_pointer_for_delete)
        query = file_system_disk.read(15)
        if query.replace(" ", "") == file_name:
            insert_bytes(actual_pointer_for_delete, actual_pointer_for_delete + 15, no_file_name)
            insert_bytes(actual_pointer_for_delete + 16, actual_pointer_for_delete + 24, no_size)
            insert_bytes(actual_pointer_for_delete + 25, actual_pointer_for_delete + 30, no_init_cluster)
            insert_bytes(actual_pointer_for_delete + 31, actual_pointer_for_delete + 45, no_date)
            insert_bytes(actual_pointer_for_delete + 46, actual_pointer_for_delete + 60, no_date)
            index = file_names.index(file_name)
            location = file_content_locator[index]
            file_system_disk.seek(location)
            total_file_sizes = 0
            sum_file_sizes = 0 
            for i in range(len(file_sizes)):
                total_file_sizes += file_sizes[i] + 4
            for i in range(index + 1, len(file_names)):
                sum_file_sizes += file_sizes[i] + 4
            for i in range(total_file_sizes):
                if i < sum_file_sizes - 4:
                    file_system_disk.seek(file_content_locator[index + 1] + i)
                    content2 = file_system_disk.read(1)
                    file_system_disk.seek(location)
                    file_system_disk.write(content2)
                    location += 1
                else:
                    file_system_disk.seek(location)
                    file_system_disk.write(no_file_name)
            flag = 1
            file_names.pop(index)
            file_sizes.pop(index)
            file_content_locator.pop(index)
        actual_pointer_for_delete = actual_pointer_for_delete + 64
    file_system_disk.close()
    queue.put(f"Archivo {file_name} eliminado")


def user_interface():
    global file_names, file_sizes
    queue = queue.Queue()

    # Threads for file operations
    def thread_copy_from_computer():
        file_path = input("Introduce la ruta del archivo a copiar desde la computadora: ")
        threading.Thread(target=copy_from_computer_to_disk, args=(file_path, queue)).start()

    def thread_copy_from_disk():
        file_name = input("Introduce el nombre del archivo en FiUnamFS a copiar: ")
        threading.Thread(target=copy_from_disk_to_computer, args=(file_name, queue)).start()

    def thread_delete_file():
        file_name = input("Introduce el nombre del archivo a eliminar: ")
        threading.Thread(target=delete_file, args=(file_name, queue)).start()

    def list_files():
        print("Archivos almacenados en FiUnamFS:")
        for file_name in file_names:
            print(file_name)

    while True:
        print("\nElige la opción ue quieras realizar")
        print("listar")
        print("copiar desde compu a FiUnamFs")
        print("copiar desde FiUnamFs a compu")
        print("eliminar un archivo de FiUnamFS")
        print("exit")

        command = input("> ")
        if command == "listar":
            list_files()
        elif command.startswith("copiar desde compu a FiUnamFs"):
            thread_copy_from_computer()
        elif command.startswith("copiar desde FiUnamFs a compu"):
            thread_copy_from_disk()
        elif command.startswith("eliminar un archivo de FiUnamFS"):
            thread_delete_file()
        elif command == "exit":
            break
        else:
            print("opcion no valida")

        # Check the queue for thread messages
        while not queue.empty():
            print(queue.get())
