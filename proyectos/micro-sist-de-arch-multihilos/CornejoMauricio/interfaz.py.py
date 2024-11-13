# Cornejo Gonzalez Mauricio PROYECTO 2
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from fiunamfs import FiUnamFS  # Importa la clase FiUnamFS 
import threading  

# Instancia de FiUnamFS con la ruta a la imagen del sistema de archivos
fs = FiUnamFS('C:\\Users\\corm3\\proyecto2\\fiunamfs.img')

class InterfazFiUnamFS:
    def __init__(self, root, fs):
        self.fs = fs  # Guarda la instancia del sistema de archivos
        self.root = root  # Referencia a la ventana principal
        self.root.title('FiUnamFS Manager')  # Título de la ventana
        
        # Llama a la función que crea los elementos gráficos de la interfaz
        self.crear_interfaz()

    def crear_interfaz(self):
        # Crea un marco (frame) para los botones
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        # Botón para listar archivos
        btn_listar = tk.Button(frame_botones, text='Listar Archivos', command=self.listar_archivos)
        btn_listar.grid(row=0, column=0, padx=5)

        # Botón para copiar un archivo desde el sistema de archivos FiUnamFS
        btn_copiar_desde_fs = tk.Button(frame_botones, text='Copiar desde FiUnamFS', command=self.copiar_desde_fs)
        btn_copiar_desde_fs.grid(row=0, column=1, padx=5)

        # Botón para copiar un archivo al sistema de archivos FiUnamFS
        btn_copiar_a_fs = tk.Button(frame_botones, text='Copiar a FiUnamFS', command=self.copiar_a_fs)
        btn_copiar_a_fs.grid(row=0, column=2, padx=5)

        # Botón para eliminar un archivo en el sistema de archivos FiUnamFS
        btn_eliminar = tk.Button(frame_botones, text='Eliminar Archivo', command=self.eliminar_archivo)
        btn_eliminar.grid(row=0, column=3, padx=5)

        # Configura la lista de archivos como una tabla con columnas
        self.lista_archivos = ttk.Treeview(self.root, columns=('nombre', 'tamano', 'fecha_modificacion'), show='headings')
        self.lista_archivos.heading('nombre', text='Nombre')
        self.lista_archivos.heading('tamano', text='Tamaño')
        self.lista_archivos.heading('fecha_modificacion', text='Fecha Modificación')
        self.lista_archivos.pack(pady=10, fill=tk.BOTH, expand=True)

    def listar_archivos(self):
        # Elimina el contenido actual de la lista para actualizarla
        self.lista_archivos.delete(*self.lista_archivos.get_children())
        # Llama a la función listar_directorio del sistema de archivos
        archivos = self.fs.listar_directorio()
        # Inserta cada archivo en la lista
        for archivo in archivos:
            self.lista_archivos.insert('', tk.END, values=(archivo['nombre'], archivo['tamano'], archivo['tiempo_modificacion']))

    def copiar_a_fs(self):
        # Selecciona un archivo del sistema local para copiar a FiUnamFS
        ruta_origen = filedialog.askopenfilename(title='Seleccionar archivo para copiar a FiUnamFS')
        if ruta_origen:
            # Extrae el nombre del archivo de la ruta completa
            nombre_archivo = ruta_origen.split('/')[-1]
            # Ejecuta la copia en un hilo separado para no bloquear la interfaz
            threading.Thread(target=self.fs.copiar_a_fs, args=(ruta_origen, nombre_archivo)).start()

    def copiar_desde_fs(self):
        # Método de marcador de posición para copiar desde FiUnamFS
        pass

    def eliminar_archivo(self):
        # Verifica si hay un archivo seleccionado
        seleccionado = self.lista_archivos.focus()
        if not seleccionado:
            messagebox.showwarning('Advertencia', 'Selecciona un archivo para eliminar.')
            return
        # Obtiene el nombre del archivo seleccionado
        nombre_archivo = self.lista_archivos.item(seleccionado, 'values')[0]
        # Pide confirmación al usuario
        if messagebox.askyesno('Confirmación', f'¿Estás seguro de que deseas eliminar \"{nombre_archivo}\"?'):
            # Ejecuta la eliminación en un hilo separado para no bloquear la interfaz
            threading.Thread(target=self.fs.eliminar_archivo, args=(nombre_archivo,)).start()

# Código principal para ejecutar la aplicación
if __name__ == '__main__':
    root = tk.Tk()
    app = InterfazFiUnamFS(root, fs)
    root.geometry('600x400')  # Tamaño inicial de la ventana
    root.mainloop()  # Inicia el bucle principal de la interfaz gráfica
