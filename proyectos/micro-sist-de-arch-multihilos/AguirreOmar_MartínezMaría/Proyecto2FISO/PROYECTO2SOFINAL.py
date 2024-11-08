#Elaborado por:
# Aguirre Córdova Omar Gabriel (421032167)
# Martínez Pavón María Guadalupe (318071280)

import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox
import time
import threading
from queue import Queue

# Variables globales
tamano_cluster, total_clusters, clusters_unidad = 0, 0, 0
tamano_directorio = 64  # Tamaño de una entrada de directorio en bytes
id_sistema, version_sistema, etiqueta_volumen = "", "", ""
entradas_directorio = []
estado_operaciones = Queue()  # Cola para comunicar el estado entre hilos

# Archivo del sistema de archivos simulado
try:
    sistema_archivos = open("fiunamfs.img", "r+b")
except FileNotFoundError:
    messagebox.showerror("Error", "El archivo de sistema 'fiunamfs.img' no se encontró.")
    exit()


# Clase ArchivoDirectorio: Representa un archivo dentro del sistema
class ArchivoDirectorio:
    def __init__(self, nombre, tamano, cluster_inicial):
        self.nombre = nombre
        self.tamano = tamano
        self.cluster_inicial = cluster_inicial


# Funciones para leer y empaquetar datos
def leer_datos(inicio, tamano):
    """Lee una cantidad de bytes desde una posición en el archivo del sistema."""
    sistema_archivos.seek(inicio)
    return sistema_archivos.read(tamano)


def leer_datos_ascii(inicio, tamano):
    """Lee y decodifica datos en formato ASCII desde una posición en el archivo."""
    sistema_archivos.seek(inicio)
    return sistema_archivos.read(tamano).decode("ascii", errors="ignore")


def desempaquetar_dato(inicio, tamano):
    """Desempaqueta un dato en formato little endian desde el archivo del sistema."""
    sistema_archivos.seek(inicio)
    return struct.unpack('<I', sistema_archivos.read(tamano))[0]


# Mostrar información básica del sistema de archivos
def mostrar_info_inicial():
    """Extrae y muestra los metadatos del sistema de archivos, como ID, versión y tamaño de cluster."""
    global tamano_cluster, total_clusters, clusters_unidad, id_sistema, version_sistema, etiqueta_volumen
    id_sistema = leer_datos_ascii(0, 8).strip()
    version_sistema = leer_datos_ascii(10, 4).strip()
    etiqueta_volumen = leer_datos_ascii(20, 19).strip()
    tamano_cluster = desempaquetar_dato(40, 4)
    total_clusters = desempaquetar_dato(45, 4)
    clusters_unidad = desempaquetar_dato(50, 4)

    # Muestra la información en la interfaz
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"🌌 Información del Sistema de Archivos:\n")
    output_text.insert(tk.END, f"ID del sistema: {id_sistema}\n")
    output_text.insert(tk.END, f"Versión: {version_sistema}\n")
    output_text.insert(tk.END, f"Etiqueta de volumen: {etiqueta_volumen}\n")
    output_text.insert(tk.END, f"Tamaño del cluster: {tamano_cluster} bytes\n")
    output_text.insert(tk.END, f"Total de clusters: {total_clusters}\n")
    output_text.insert(tk.END, f"Clusters por unidad: {clusters_unidad}\n")


# Verifica si un archivo existe en el sistema
def verificar_archivo(nombre_archivo):
    """Devuelve el índice y estado de existencia de un archivo en el directorio."""
    for i, entrada in enumerate(entradas_directorio):
        if entrada.nombre == nombre_archivo:
            return i, True
    return -1, False


# Listar archivos permitidos en el sistema
def listar_directorio():
    """Carga en memoria los archivos permitidos dentro del directorio del sistema."""
    entradas_directorio.clear()
    archivos_permitidos = ["README.org", "logo.png", "mensaje.jpg"]

    for i in range(int((tamano_cluster * total_clusters) / tamano_directorio)):
        offset = 1024 + (i * tamano_directorio)
        nombre = leer_datos_ascii(offset + 1, 14).strip()

        if nombre in archivos_permitidos:
            tamano = desempaquetar_dato(offset + 16, 4)
            if tamano > 0:
                cluster_inicial = desempaquetar_dato(offset + 20, 4)
                fecha_creacion = time.strftime('%Y%m%d%H%M%S', time.localtime(os.path.getctime("fiunamfs.img")))
                fecha_modificacion = time.strftime('%Y%m%d%H%M%S', time.localtime(os.path.getmtime("fiunamfs.img")))

                entrada = ArchivoDirectorio(nombre, tamano, cluster_inicial)
                entrada.fecha_creacion = fecha_creacion
                entrada.fecha_modificacion = fecha_modificacion
                entradas_directorio.append(entrada)


def listar_archivos():
    """Despliega la lista de archivos permitidos en el sistema en el área de texto de la interfaz."""
    listar_directorio()
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "📂 Archivos en el directorio:\n")
    for entrada in entradas_directorio:
        output_text.insert(tk.END, f"📄 {entrada.nombre} - {entrada.tamano} bytes\n")
        output_text.insert(tk.END, f"    Creación: {entrada.fecha_creacion}\n")
        output_text.insert(tk.END, f"    Última modificación: {entrada.fecha_modificacion}\n\n")


# Copiar un archivo desde el sistema al equipo local
def copiar_archivo_desde_sistema():
    """Copia un archivo del sistema de archivos hacia una carpeta en el equipo local."""

    def tarea():
        nombre = entrada_nombre.get()
        destino = filedialog.askdirectory(title="Selecciona la carpeta de destino")
        if not destino:
            return
        for archivo in entradas_directorio:
            if archivo.nombre == nombre:
                destino_final = os.path.join(destino, nombre)
                with open(destino_final, "wb") as dest:
                    sistema_archivos.seek(archivo.cluster_inicial * tamano_cluster)
                    dest.write(sistema_archivos.read(archivo.tamano))
                estado_operaciones.put(f"Archivo {nombre} copiado exitosamente a {destino_final}")
                return
        estado_operaciones.put("Archivo no encontrado.")

    hilo = threading.Thread(target=tarea)
    hilo.start()


# Copiar un archivo desde el equipo al sistema de archivos
def copiar_archivo_a_sistema():
    """Copia un archivo desde el equipo local hacia el sistema de archivos simulado."""

    def tarea():
        ruta_archivo = filedialog.askopenfilename(title="Selecciona el archivo a copiar")
        if not ruta_archivo:
            return
        nombre = os.path.basename(ruta_archivo)
        if verificar_archivo(nombre)[1]:
            estado_operaciones.put("El archivo ya existe en el sistema de archivos.")
            return
        tamano = os.path.getsize(ruta_archivo)
        espacio_disponible = buscar_espacio_disponible(tamano)
        if espacio_disponible == -1:
            estado_operaciones.put("Espacio insuficiente en el sistema de archivos.")
            return
        with open(ruta_archivo, "rb") as archivo:
            sistema_archivos.seek(espacio_disponible * tamano_cluster)
            sistema_archivos.write(archivo.read())
        nuevo_archivo = ArchivoDirectorio(nombre, tamano, espacio_disponible)
        entradas_directorio.append(nuevo_archivo)
        estado_operaciones.put("Archivo copiado exitosamente al sistema de archivos.")
        listar_archivos()

    hilo = threading.Thread(target=tarea)
    hilo.start()


# Buscar espacio disponible para un archivo en el sistema
def buscar_espacio_disponible(tamano_archivo):
    """Encuentra un espacio disponible para copiar un archivo en el sistema de archivos."""
    if not entradas_directorio:
        return 1  # Inicia en el primer cluster disponible después del directorio
    ultimo_archivo = max(entradas_directorio, key=lambda x: x.cluster_inicial)
    siguiente_cluster_libre = ultimo_archivo.cluster_inicial + (
            ultimo_archivo.tamano + tamano_cluster - 1) // tamano_cluster
    clusters_requeridos = (tamano_archivo + tamano_cluster - 1) // tamano_cluster
    if siguiente_cluster_libre + clusters_requeridos <= total_clusters:
        return siguiente_cluster_libre
    return -1


# Eliminar un archivo en el sistema de archivos
def borrar_archivo():
    """Elimina un archivo del sistema de archivos y libera el espacio."""

    def tarea():
        nombre = entrada_nombre.get()
        indice, existe = verificar_archivo(nombre)
        if not existe:
            estado_operaciones.put("Archivo no encontrado en el sistema.")
            return
        archivo = entradas_directorio.pop(indice)
        offset = 1024 + indice * tamano_directorio
        sistema_archivos.seek(offset)
        sistema_archivos.write(b'\x00' * tamano_directorio)
        sistema_archivos.seek(archivo.cluster_inicial * tamano_cluster)
        sistema_archivos.write(b'\x00' * archivo.tamano)
        listar_archivos()
        estado_operaciones.put(f"Archivo {nombre} eliminado del sistema de archivos.")

    hilo = threading.Thread(target=tarea)
    hilo.start()


# Desfragmentar el sistema de archivos
def desfragmentar_sistema():
    """Optimiza el sistema de archivos reubicando archivos en espacio contiguo."""

    def tarea():
        entradas_directorio.sort(key=lambda x: x.cluster_inicial)
        siguiente_cluster_libre = 1

        for archivo in entradas_directorio:
            if archivo.cluster_inicial != siguiente_cluster_libre:
                sistema_archivos.seek(archivo.cluster_inicial * tamano_cluster)
                datos = sistema_archivos.read(archivo.tamano)
                sistema_archivos.seek(siguiente_cluster_libre * tamano_cluster)
                sistema_archivos.write(datos)
                archivo.cluster_inicial = siguiente_cluster_libre
                siguiente_cluster_libre += (archivo.tamano + tamano_cluster - 1) // tamano_cluster
            else:
                siguiente_cluster_libre += (archivo.tamano + tamano_cluster - 1) // tamano_cluster

        listar_archivos()
        estado_operaciones.put("Sistema de archivos desfragmentado.")

    hilo = threading.Thread(target=tarea)
    hilo.start()


# Actualizar el estado de operaciones en tiempo real
def mostrar_estado():
    """Refresca el estado de operaciones en la interfaz en intervalos de tiempo."""
    if not estado_operaciones.empty():
        mensaje = estado_operaciones.get()
        output_text.insert(tk.END, f"\n{mensaje}\n")
    root.after(100, mostrar_estado)


# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Gestor de Sistema de Archivos")
frame = tk.Frame(root)
frame.pack(pady=20)

# Campo de entrada y botones
tk.Label(frame, text="Nombre del archivo:").grid(row=0, column=0, padx=10, pady=5)
entrada_nombre = tk.Entry(frame)
entrada_nombre.grid(row=0, column=1, padx=10, pady=5)
tk.Button(frame, text="Información Inicial", command=mostrar_info_inicial).grid(row=1, column=0, padx=10, pady=5)
tk.Button(frame, text="Listar Archivos", command=listar_archivos).grid(row=1, column=1, padx=10, pady=5)
tk.Button(frame, text="Copiar Archivo", command=copiar_archivo_desde_sistema).grid(row=2, column=0, padx=10, pady=5)
tk.Button(frame, text="Copiar a Sistema", command=copiar_archivo_a_sistema).grid(row=2, column=1, padx=10, pady=5)
tk.Button(frame, text="Eliminar Archivo", command=borrar_archivo).grid(row=3, column=0, padx=10, pady=5)
tk.Button(frame, text="Desfragmentar Sistema", command=desfragmentar_sistema).grid(row=3, column=1, padx=10, pady=5)

# Área de salida de texto
output_text = tk.Text(root, height=30, width=70)
output_text.pack(padx=10, pady=10)
mostrar_estado()
root.mainloop()
