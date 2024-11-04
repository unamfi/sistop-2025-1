import os
import struct
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
from threading import Lock

# Ruta del sistema de archivos
sistema_archivos = "fiunamfs.img"
archivo_sist = []  # Lista de datos de los archivos a imprimir
buffer_archivos = Lock()

# Clase para gestionar el sistema de archivos FiUnamFS
class FiUnamFS:
    def __init__(self, disk_file):
        self.disk_file = disk_file
        self.load_superblock()  # Verificación del archivo y carga inicial del superbloque
    
    def load_superblock(self):
        with open(self.disk_file, 'rb') as file:
            file.seek(0)
            superbloque = file.read(1024)
            nombre = superbloque[0:8].decode().strip('\x00')
            version = superbloque[10:15].decode().strip('\x00')
            if nombre != "FiUnamFS" or version != "25-1":
                messagebox.showerror("Error", "El sistema de archivos no es FiUnamFS o la versión no es compatible")
                exit(1)
