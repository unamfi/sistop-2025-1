# Proyecto FiUnamFS - Gestor de Sistema de Archivos

## 1. Autores

-   **González Iniestra Emilio**
-   **Suarez Guzman Dayna Yarelly**

**Fecha de entrega:** 07/11/2024

----------

## 2. Descripción General

El proyecto consiste en el desarrollo de un gestor para el sistema de archivos **FiUnamFS**, utilizado en un entorno académico. Este gestor permite realizar operaciones esenciales, como listar contenidos, copiar archivos desde y hacia el sistema de archivos, y eliminar archivos. Además, el programa incluye la implementación de hilos para manejar operaciones concurrentes y la sincronización entre estos.

----------

## 3. Requisitos y Entorno

-   **Lenguaje de programación:** Python 3.6 o superior
    
-   **Módulos necesarios:**
    
    -   `struct`: Para manejar la manipulación de datos binarios.
    -   `os`: Para funciones de sistema y manejo de archivos.
    -   `time`: Para obtener y formatear timestamps.
    -   `threading`: Para crear y manejar hilos.
    -   `tkinter`: Para construir la interfaz gráfica de usuario.
-   **Entorno de ejecución:** Windows, macOS o Linux con Python 3.6+.
    

----------

## 4. Funcionalidades del Programa

El programa desarrollado permite:

1.  **Listar los contenidos del directorio:** Muestra los archivos almacenados en FiUnamFS, incluyendo detalles como el tamaño, la fecha de creación y la última modificación.
2.  **Copiar un archivo de FiUnamFS al sistema local:** Permite al usuario seleccionar un archivo y copiarlo al sistema de archivos local.
3.  **Copiar un archivo del sistema local a FiUnamFS:** Copia un archivo desde la computadora del usuario al sistema de archivos FiUnamFS, verificando el espacio disponible.
4.  **Eliminar un archivo de FiUnamFS:** Elimina un archivo del sistema de archivos.
5.  **Sincronización y uso de hilos:** El programa utiliza hilos para ejecutar las operaciones de E/S de forma concurrente y evitar el bloqueo de la interfaz gráfica.

----------

## 5. Explicación del Código

### Importación de Módulos

Se importan los módulos necesarios:

-   `struct`: Para manipulación de datos binarios en formato little endian, esencial para leer y escribir en el sistema de archivos.
-   `os`: Para operaciones de manejo de archivos y rutas.
-   `time`: Para trabajar con fechas y formatearlas en el formato requerido (AAAAMMDDHHMMSS).
-   `threading`: Para crear y manejar hilos que ejecuten operaciones en paralelo.
-   `tkinter`: Para crear la interfaz gráfica de usuario (GUI).
    -   `filedialog`, `messagebox`, `Listbox`: Componentes de tkinter para interacciones de usuario, mostrar mensajes y listas.

### Parámetros del Sistema de Archivos

Estas constantes definen los parámetros de FiUnamFS, como el tamaño del "disco", la estructura de clusters y la identificación del sistema.

### Validación y Lectura del Superbloque

Esta función valida que el archivo `fiunamfs.img` sea un sistema de archivos válido y devuelve información importante como la etiqueta del volumen y el tamaño de clusters. Si la identificación o la versión no coinciden, se muestra un mensaje de error y la función retorna `None`.

### Listar los Contenidos del Directorio

Recorre las entradas del directorio en los clusters correspondientes y recopila información sobre los archivos, como el nombre, el tamaño y las fechas de creación y modificación. Las entradas vacías (marcadas con `#`) se omiten.

### Copiar un Archivo de FiUnamFS al Sistema Local

La función `copy_to_local` inicia un hilo que ejecuta `copy_to_local_thread`, la cual busca el archivo en FiUnamFS y lo copia al sistema local. Se utiliza un `threading.Lock` para asegurar que la operación sea segura cuando se accede al archivo compartido.

### Copiar un Archivo del Sistema Local a FiUnamFS

Esta función busca un espacio disponible en el directorio y copia un archivo desde el sistema local a FiUnamFS. Si no hay suficiente espacio, muestra un mensaje de error. La operación se realiza en un hilo para evitar bloquear la interfaz gráfica.

### Eliminar un Archivo de FiUnamFS

La función `delete_file` inicia un hilo que ejecuta `delete_file_thread`, la cual marca la entrada del archivo como vacía, eliminándolo del sistema de archivos. La operación se sincroniza con un `threading.Lock`.

### Cálculo del Espacio Total Usado

Calcula el espacio total usado en FiUnamFS recorriendo las entradas ocupadas en el directorio y sumando el tamaño de los archivos.

### Interfaz Gráfica y Manejo de Estado

La interfaz gráfica se configura con `tkinter`. Los botones permiten al usuario realizar las operaciones de listar, copiar y eliminar archivos. La función `check_operation_status` monitorea el estado de las operaciones realizadas en los hilos y muestra mensajes de éxito o error.

----------

## 6. Estrategia de Implementación y Sincronización

El programa utiliza hilos para manejar operaciones de E/S sin bloquear la interfaz, proporcionando una experiencia fluida para el usuario. El `threading.Lock` asegura que las operaciones críticas (como escribir o leer del archivo `fiunamfs.img`) no interfieran entre sí.

----------

## 7. Ejemplos de Uso

### Listar Archivos en FiUnamFS

-   **Acción:** Presiona el botón **"Listar Archivos"**.
-   **Resultado esperado:** Aparecerá una lista de archivos en la interfaz, mostrando el nombre, el tamaño, la fecha de creación y la última modificación.
-   **Caso de error:** Si el archivo `fiunamfs.img` no existe o no es un sistema de archivos válido, se mostrará un mensaje de error.

### Copiar un Archivo de FiUnamFS al Sistema Local

-   **Acción:** Selecciona un archivo de la lista y presiona el botón **"Copiar a Local"**.
-   **Resultado esperado:** Se abrirá un cuadro de diálogo para guardar el archivo en el sistema local. El archivo se copiará y se mostrará un mensaje de éxito.
-   **Caso de error:** Si el archivo seleccionado no existe (por ejemplo, se elimina mientras se visualiza la lista), se mostrará un mensaje de error indicando que no se encontró el archivo.
-   **Caso de cancelación:** Si el usuario cancela el cuadro de diálogo de guardado, no se realizará ninguna acción y no se mostrará ningún mensaje.

### Copiar un Archivo desde el Sistema Local a FiUnamFS

-   **Acción:** Presiona el botón **"Copiar a FiUnamFS"** y selecciona un archivo desde tu sistema local.
-   **Resultado esperado:** El archivo se copiará al sistema de archivos FiUnamFS y aparecerá un mensaje de éxito en la interfaz.
-   **Caso de error:**
    -   Si no hay suficiente espacio en FiUnamFS para el archivo, se mostrará un mensaje de error indicando que no hay espacio disponible.
    -   Si no se encuentra un espacio libre en el directorio para almacenar la entrada del archivo, se mostrará un mensaje de error indicando que el directorio está lleno.
-   **Caso de cancelación:** Si el usuario cancela la selección del archivo, no se realizará ninguna acción.

### Eliminar un Archivo de FiUnamFS

-   **Acción:** Selecciona un archivo de la lista y presiona el botón **"Eliminar Archivo"**.
-   **Resultado esperado:** El archivo se marcará como eliminado y se mostrará un mensaje de éxito.
-   **Caso de error:** Si el archivo seleccionado no se encuentra en FiUnamFS (por ejemplo, si fue eliminado por otra operación), se mostrará un mensaje de error indicando que el archivo no fue encontrado.

----------

## 8. Errores y Mensajes de Estado

-   **Error de archivo inexistente:** Si el archivo `fiunamfs.img` no está presente en el directorio de trabajo, se mostrará un mensaje de error y se cancelarán todas las operaciones.
-   **Archivo dañado o formato incorrecto:** Si el archivo `fiunamfs.img` tiene un formato que no coincide con la estructura esperada de FiUnamFS, se mostrará un mensaje de error y se detendrán las operaciones.

----------

## 9. Instrucciones de Instalación y Ejecución

1.  **Descarga** el archivo `fiunamfs.img` y colócalo en el mismo directorio que el código.
    
2.  Asegúrate de tener **Python 3.6+** instalado.
    
3.  Ejecuta el programa con: