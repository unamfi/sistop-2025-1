# Facultad de Ingenieria UNAM
# Autores: Suarez Guzman Dayna Yarelly
#	   Gonzalez Iniestra Emilio
# Asignatura: Sistemas Operativos

import struct
import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox

# Parámetros del sistema de archivos FiUnamFS
disk_file = "fiunamfs.img"
DISK_SIZE = 1440 * 1024  # Tamaño total del "disco" en bytes
CLUSTER_SIZE = 256 * 4   # Tamaño de cada cluster en bytes
DIRECTORY_START_CLUSTER = 1  # Cluster de inicio del directorio
DIRECTORY_END_CLUSTER = 4    # Cluster final del directorio
DIRECTORY_ENTRY_SIZE = 64    # Tamaño de cada entrada del directorio
FILE_NAME_SIZE = 15          # Tamaño máximo del nombre de archivo
IDENTIFICATION = b"FiUnamFS" # Identificación del sistema de archivos
VERSION = b"25-1"            # Versión del sistema de archivos
