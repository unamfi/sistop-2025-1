* Documentación de la Concurrencia en el Sistema de Archivos FIunamFS

La concurrencia en este programa se utiliza en los métodos `copyfromFS()` y `copytoFS()` de la clase `FSsistop`. Estos métodos manejan la lectura y escritura de archivos en el sistema de archivos FIunamFS de manera concurrente.

** `copyfromFS()`
El método `copyfromFS()` se encarga de copiar un archivo del sistema de archivos FIunamFS a una ruta de destino en el sistema operativo. Utiliza dos hilos para realizar esta operación:

1. *Reader Thread*:
   - Este hilo se encarga de leer los datos del archivo en el sistema de archivos FIunamFS y colocarlos en una cola (`data_queue`).
   - Primero, calcula el tamaño total del archivo y el tamaño de los bloques (clusters) a leer.
   - Luego, abre el archivo FIunamFS y lee los datos en bloques, colocándolos en la cola.
   - Finalmente, coloca un valor `None` en la cola para indicar que la lectura ha finalizado.

2. *Writer Thread*:
   - Este hilo se encarga de tomar los datos de la cola (`data_queue`) y escribirlos en el archivo de destino.
   - Mientras la cola no esté vacía, el hilo toma los datos de la cola y los escribe en el archivo de destino.
   - Una vez que la cola está vacía (indicado por el valor `None`), el hilo finaliza.

Ambos hilos se inician en paralelo y se unen al final, asegurando que la operación de copia se complete correctamente.

** `copytoFS()`
El método `copytoFS()` se encarga de copiar un archivo del sistema operativo al sistema de archivos FIunamFS. Al igual que `copyfromFS()`, utiliza dos hilos para realizar esta operación:

1. *Reader Thread*:
   - Este hilo se encarga de leer los datos del archivo en el sistema operativo y colocarlos en la cola (`data_queue`).
   - Abre el archivo de origen y lee los datos en bloques, colocándolos en la cola.
   - Finalmente, coloca un valor `None` en la cola para indicar que la lectura ha finalizado.

2. *Writer Thread*:
   - Este hilo se encarga de tomar los datos de la cola (`data_queue`) y escribirlos en el archivo FIunamFS.
   - Primero, calcula el cluster de inicio para el archivo y actualiza los metadatos del directorio.
   - Luego, mientras la cola no esté vacía, el hilo toma los datos de la cola y los escribe en el archivo FIunamFS.
   - Una vez que la cola está vacía (indicado por el valor `None`), el hilo finaliza.

Al igual que en `copyfromFS()`, ambos hilos se inician en paralelo y se unen al final, asegurando que la operación de copia se complete correctamente.

Si observamos, la lógica en ambos métodos es relativamente la misma con la diferencia en que se tiene que considerar de donde a donde se va a realizar la operación entre archivos. 
En nuestro caso, son las opciones:
    2.- Copiar Archivos;
    3.- Agregar Archivo.