import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from fiunamfs import FiUnamFS  # Importa la clase del archivo fiunamfs.py
import threading

# Inicializar FiUnamFS con la ruta de tu archivo
fs = FiUnamFS('C:\\Users\\corm3\\proyecto2\\fiunamfs.img')

class InterfazFiUnamFS:
    def __init__(self, root, fs):
        self.fs = fs
        self.root = root
        self.root.title('FiUnamFS Manager')
        
        # Crear botones y lista de archivos
        self.crear_interfaz()

    def crear_interfaz(self):
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        btn_listar = tk.Button(frame_botones, text='Listar Archivos', command=self.listar_archivos)
        btn_listar.grid(row=0, column=0, padx=5)

        btn_copiar_desde_fs = tk.Button(frame_botones, text='Copiar desde FiUnamFS', command=self.copiar_desde_fs)
        btn_copiar_desde_fs.grid(row=0, column=1, padx=5)

        btn_copiar_a_fs = tk.Button(frame_botones, text='Copiar a FiUnamFS', command=self.copiar_a_fs)
        btn_copiar_a_fs.grid(row=0, column=2, padx=5)

        btn_eliminar = tk.Button(frame_botones, text='Eliminar Archivo', command=self.eliminar_archivo)
        btn_eliminar.grid(row=0, column=3, padx=5)

        self.lista_archivos = ttk.Treeview(self.root, columns=('nombre', 'tamano', 'fecha_modificacion'), show='headings')
        self.lista_archivos.heading('nombre', text='Nombre')
        self.lista_archivos.heading('tamano', text='Tamaño')
        self.lista_archivos.heading('fecha_modificacion', text='Fecha Modificación')
        self.lista_archivos.pack(pady=10, fill=tk.BOTH, expand=True)

    def listar_archivos(self):
        self.lista_archivos.delete(*self.lista_archivos.get_children())
        archivos = self.fs.listar_directorio()
        for archivo in archivos:
            self.lista_archivos.insert('', tk.END, values=(archivo['nombre'], archivo['tamano'], archivo['tiempo_modificacion']))

    def copiar_a_fs(self):
        # Mostrar un cuadro de diálogo para seleccionar un archivo a copiar al sistema de archivos
        ruta_origen = filedialog.askopenfilename(title='Seleccionar archivo para copiar a FiUnamFS')
        if ruta_origen:
            nombre_archivo = ruta_origen.split('/')[-1]  # Obtener el nombre del archivo
            threading.Thread(target=self.fs.copiar_a_fs, args=(ruta_origen, nombre_archivo)).start()

    def copiar_desde_fs(self):
        # Placeholder function - actual implementation would depend on self.fs.copiar_desde_fs
        pass

    def eliminar_archivo(self):
        seleccionado = self.lista_archivos.focus()
        if not seleccionado:
            messagebox.showwarning('Advertencia', 'Selecciona un archivo para eliminar.')
            return
        nombre_archivo = self.lista_archivos.item(seleccionado, 'values')[0]
        if messagebox.askyesno('Confirmación', f'¿Estás seguro de que deseas eliminar \"{nombre_archivo}\"?'):
            threading.Thread(target=self.fs.eliminar_archivo, args=(nombre_archivo,)).start()

# Código principal para ejecutar la aplicación
if __name__ == '__main__':
    root = tk.Tk()
    app = InterfazFiUnamFS(root, fs)
    root.geometry('600x400')  # Establecer tamaño de la ventana
    root.mainloop()  # Iniciar el bucle de eventos
