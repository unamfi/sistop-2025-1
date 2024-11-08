import os
import struct
from threading import Lock, Semaphore
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class GestorSistemaArchivos:
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.bloqueo_acceso = Lock()
        self.bloqueo_superbloque = Semaphore(1)
        self.tamano_sector = 256
        self.tamano_cluster = 1024  # 4 sectores de 256 bytes
        self.clusters_directorio_reservados = 4
        self.tamano_entrada_dir = 64
        self.validar_sistema_archivos()

    def validar_sistema_archivos(self):
        # Lee el superbloque y valida el nombre y la versión
        with self.bloqueo_superbloque:
            with open(self.ruta_archivo, 'rb') as archivo_disco:
                archivo_disco.seek(0)
                datos_superbloque = archivo_disco.read(1024)
                
                # Desempaqueta el nombre y la versión desde el superbloque
                nombre_fs = struct.unpack('8s', datos_superbloque[0:8])[0].decode('ascii').strip('\x00')
                version_fs = struct.unpack('5s', datos_superbloque[10:15])[0].decode('ascii').strip('\x00')
                
                print(f"Comprobación del sistema de archivos... Nombre: {nombre_fs}, Versión: {version_fs}")
                
                if nombre_fs != 'FiUnamFS' or version_fs != '25-1':
                    raise ValueError("Sistema de archivos no compatible o está corrupto.")

    def obtener_entradas_directorio(self):
        lista_entradas = []

        # Abre el archivo y lee cada cluster reservado para entradas de directorio
        with open(self.ruta_archivo, 'rb') as archivo_disco:
            self.validar_sistema_archivos()
            
            for cluster in range(self.clusters_directorio_reservados):
                posicion_inicial = (1 + cluster) * self.tamano_cluster
                archivo_disco.seek(posicion_inicial)
                datos_cluster_directorio = archivo_disco.read(self.tamano_cluster)
                
                for offset_entrada in range(0, self.tamano_cluster, self.tamano_entrada_dir):
                    entrada_actual = datos_cluster_directorio[offset_entrada:offset_entrada + self.tamano_entrada_dir]
                    
                    # Si la entrada está vacía, rellena con valores de marcador de posición
                    if entrada_actual[0:1] == b'#' or all(b == 0 for b in entrada_actual):
                        info_entrada = {
                            'Tipo': '-',
                            'Nombre': "---------------",
                            'Tamaño': "---------------",
                            'Cluster Inicial': "---------------",
                            'Fecha Creación': "---------------",
                            'Fecha Modificación': "---------------"
                        }
                    else:
                        info_entrada = self._parsear_entrada_directorio(entrada_actual)

                    lista_entradas.append(info_entrada)

        return lista_entradas

    def _parsear_entrada_directorio(self, datos_entrada):
        tipo_archivo = chr(datos_entrada[0])
        nombre_archivo = datos_entrada[1:16].decode('ascii').strip('\x00')
        tamano_archivo = struct.unpack('<I', datos_entrada[16:20])[0]
        cluster_inicial = struct.unpack('<I', datos_entrada[20:24])[0]
        fecha_creacion = datos_entrada[24:38].decode('ascii').strip('\x00')
        fecha_modificacion = datos_entrada[38:52].decode('ascii').strip('\x00')
        
        return {
            'Tipo': tipo_archivo,
            'Nombre': nombre_archivo,
            'Tamaño': tamano_archivo,
            'Cluster Inicial': cluster_inicial,
            'Fecha Creación': fecha_creacion,
            'Fecha Modificación': fecha_modificacion
        }

    def copiar_a_sistema_host(self, nombre_archivo, ruta_destino):
        with self.bloqueo_acceso:
            with open(self.ruta_archivo, 'r+b') as disco:
                tamano_cluster = self.tamano_cluster

                # Posicionarse al inicio de las entradas de directorio para ubicar el archivo
                disco.seek(1024)
                archivo_encontrado = False
                cluster_inicial, tamano_archivo = 0, 0
                
                for i in range(64):
                    entrada = disco.read(64)
                    nombre_en_fs = struct.unpack('15s', entrada[1:16])[0].decode('ascii').rstrip('\x00').strip()
                    
                    if nombre_en_fs == nombre_archivo:
                        archivo_encontrado = True
                        cluster_inicial = struct.unpack('<I', entrada[33:37])[0]
                        tamano_archivo = struct.unpack('<I', entrada[17:21])[0]
                        break

                if not archivo_encontrado:
                    return f"Archivo '{nombre_archivo}' no encontrado"

                # Leer y escribir los datos del archivo en el sistema host
                disco.seek(tamano_cluster * cluster_inicial)
                datos_archivo = disco.read(tamano_archivo)

                if os.path.isdir(ruta_destino):
                    ruta_destino = os.path.join(ruta_destino, nombre_archivo)

                with open(ruta_destino, 'wb') as archivo_salida:
                    archivo_salida.write(datos_archivo)

                return f"Archivo '{nombre_archivo}' copiado exitosamente a {ruta_destino}"

    def agregar_archivo_a_fs(self, archivo_origen, nombre_archivo):
        with self.bloqueo_acceso:
            with open(self.ruta_archivo, 'r+b') as disco:
                tamano_cluster = self.tamano_cluster

                # Busca una entrada de directorio vacía para colocar el nuevo archivo
                disco.seek(1024)
                indice_entrada_vacia = -1
                for i in range(64):
                    entrada = disco.read(64)
                    if entrada[0:1] == b'#' or all(b == 0 for b in entrada):
                        indice_entrada_vacia = i
                        break

                if indice_entrada_vacia == -1:
                    return "No hay espacio disponible en el directorio"

                # Encuentra un cluster libre para colocar los datos del archivo
                cluster_libre = self._encontrar_cluster_vacio(disco, tamano_cluster)
                if cluster_libre == -1:
                    return "No hay clusters libres disponibles para almacenar el archivo"

                with open(archivo_origen, 'rb') as archivo:
                    datos = archivo.read()
                    tamano_archivo = len(datos)

                disco.seek(tamano_cluster * cluster_libre)
                disco.write(datos)

                # Actualiza la entrada de directorio para el nuevo archivo
                disco.seek(1024 + 64 * indice_entrada_vacia)
                nombre_codificado = nombre_archivo.encode('ascii').ljust(15, b' ')
                datos_entrada = struct.pack(
                    '<c15sII52s', b'-', nombre_codificado, tamano_archivo, cluster_libre, b'\x00' * 52)
                disco.write(datos_entrada)

                return "Archivo agregado exitosamente al sistema de archivos"

    def _encontrar_cluster_vacio(self, disco, tamano_cluster):
        # Localiza un cluster no utilizado para almacenar datos del archivo
        disco.seek(tamano_cluster)
        for i in range(1, int(1440 * 1024 / tamano_cluster)):
            disco.seek(tamano_cluster * i)
            if disco.read(tamano_cluster) == b'\x00' * tamano_cluster:
                return i
        return -1

    def eliminar_archivo(self, nombre_archivo):
        with self.bloqueo_acceso:
            with open(self.ruta_archivo, 'r+b') as disco:
                disco.seek(1024)
                for i in range(64):
                    entrada = disco.read(64)
                    nombre_en_entrada = entrada[1:16].decode('ascii').rstrip('\x00').strip()
                    if nombre_en_entrada == nombre_archivo:
                        disco.seek(1024 + 64 * i)
                        disco.write(b'#' + entrada[1:])  # Marcar como eliminado
                        return f"Archivo '{nombre_archivo}' eliminado exitosamente."
            return f"Archivo '{nombre_archivo}' no encontrado."


class InterfazSistemaArchivos:
    def __init__(self, sistema_archivos):
        self.fs = sistema_archivos
        self.raiz = tk.Tk()
        self.raiz.title("Gestor de FiUnamFS")
        self.crear_elementos()
        self.raiz.mainloop()

    def crear_elementos(self):
        frame = tk.Frame(self.raiz)
        frame.pack(pady=10, padx=10)
        
        boton_listar = tk.Button(frame, text="Listar Directorio", command=self.mostrar_directorio)
        boton_listar.grid(row=0, column=0, padx=5, pady=5)

        boton_copiar_desde_fs = tk.Button(frame, text="Copiar Archivo desde FS", command=self.copiar_desde_fs)
        boton_copiar_desde_fs.grid(row=0, column=1, padx=5, pady=5)

        boton_agregar_a_fs = tk.Button(frame, text="Agregar Archivo a FS", command=self.agregar_a_fs)
        boton_agregar_a_fs.grid(row=0, column=2, padx=5, pady=5)

        boton_eliminar_archivo = tk.Button(frame, text="Eliminar Archivo", command=self.eliminar_archivo)
        boton_eliminar_archivo.grid(row=0, column=3, padx=5, pady=5)

    def mostrar_directorio(self):
        entradas = self.fs.obtener_entradas_directorio()
        encabezado = f"{'Nombre':<25} {'Tamaño':<10} {'Cluster Inicial':<15} {'Fecha Creación':<20} {'Fecha Modificación':<20}\n"
        texto_mostrar = encabezado + "-" * len(encabezado) + "\n"
        for entrada in entradas:
            texto_mostrar += f"{entrada['Nombre']:<25} {entrada['Tamaño']:<10} {entrada['Cluster Inicial']:<15} {entrada['Fecha Creación']:<20} {entrada['Fecha Modificación']:<20}\n"
        
        tk.messagebox.showinfo("Listado del Directorio", texto_mostrar)

    def copiar_desde_fs(self):
        nombre_archivo = simpledialog.askstring("Copiar desde FS", "Ingrese el nombre del archivo en FS:")
        ruta_destino = filedialog.askdirectory(title="Seleccionar Carpeta de Destino")
        if nombre_archivo and ruta_destino:
            mensaje = self.fs.copiar_a_sistema_host(nombre_archivo, ruta_destino)
            tk.messagebox.showinfo("Resultado de Copiar desde FS", mensaje)

    def agregar_a_fs(self):
        archivo_origen = filedialog.askopenfilename(title="Seleccionar Archivo para Agregar")
        nombre_archivo = simpledialog.askstring("Agregar a FS", "Ingrese el nombre con el que guardará el archivo:")
        if archivo_origen and nombre_archivo:
            mensaje = self.fs.agregar_archivo_a_fs(archivo_origen, nombre_archivo)
            tk.messagebox.showinfo("Resultado de Agregar a FS", mensaje)

    def eliminar_archivo(self):
        nombre_archivo = simpledialog.askstring("Eliminar Archivo", "Ingrese el nombre del archivo en FS a eliminar:")
        if nombre_archivo:
            confirmacion = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar '{nombre_archivo}'?")
            if confirmacion:
                mensaje = self.fs.eliminar_archivo(nombre_archivo)
                tk.messagebox.showinfo("Resultado de Eliminación", mensaje)
                self.mostrar_directorio()  # Actualiza la lista después de eliminar


def iniciar_aplicacion():
    ruta_sistema_archivo = filedialog.askopenfilename(title="Seleccione el archivo de sistema 'fiunamfs.img'", filetypes=[("Archivo IMG", "*.img")])
    if ruta_sistema_archivo:
        fs = GestorSistemaArchivos(ruta_sistema_archivo)
        InterfazSistemaArchivos(fs)


if __name__ == "__main__":
    iniciar_aplicacion()
