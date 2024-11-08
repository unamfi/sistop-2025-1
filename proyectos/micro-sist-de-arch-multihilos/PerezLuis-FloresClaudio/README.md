# Proyecto sistemas de archivos multi-hilos

## Autores:

- Perez Osorio Luis Eduardo
- Flores Garcia Claudio

## Requerimientos.

- Entorno

El programa se desarrolló utilizando python 3, en particular las versiones 3.10.12 y 3.13.0, se probó su funcionamiento en sistemas los siguientes operativos: windows 11 (10.0.22631), ubuntu 22.04 y mint 22

- Dependencias

Ademas de la version 3.10+ de python, es necesario la descarga de la biblioteca prettytable, que es usada para visualizar el contenido del sistema de archivos, esta puede instalarse con `pip` utilizando el comando:

   `pip install prettytable`

## Uso del programa

El programa se puede ejecutar posicionándose en el directorio que contiene a `main.py` y ejecutando el comando

`python3 main.py` o `python main.py` 

Dependiendo la instalación de python del sistema.

El programa presenta una interfaz de linea de comandos para la interacción con el usuario, al iniciarse el programa solicitara al usuario la ruta del sistema de archivos, las rutas que se proporcionan al programa pueden ser relativas o absolutas.

La ruta indicada debe apuntar a un archivo binario que cumpla con la especificación planteada en el proyecto, de otra manera se mostrara un error y terminara la ejecución del programa.

Una vez se ha proporcionado un sistema de archivos válido se desplegara un menu de usuario con las siguientes opciones:

1. **Listar contenido.**

   Despliega el contenido del directorio, indicando nombre de archivo, tamaño (en bytes), fecha de creacion y ultima modificación.

2. **Copiar archivo de FiunamFS.**

   Permite al usuario copiar un archivo desde el sistema de archivos hacia otra parte de su computadora.

   Esta opción solicitará primero el nombre del archivo a copiar, este se se debe escribir tal cual aparece en la lista de contenidos (opción 1).

   Después se debe proporcionar la ruta en la cual se guardara el archivo copiado, esta puede ser relativa o absoluta, por ejemplo `/home/lalo/archivo.txt` o `archivo.txt` para guardarlo en el directorio actual.

3. **Agregar archivo a FIunamFS.**

   Permite agregar un archivo desde la computadora hacia el sistema de archivos FIunamFS.

   Esta opción solicitará al usuario la ruta del archivo a copiar, igual que para la opcion 2 esta ruta puede ser relativa o absoluta.

   Después se solicitara el nombre con el cual se guardara el archivo, **el nombre deber ser una cadena ASCII de máximo 14 caracteres**.

4. **Eliminar archivo**

   Elimina un archivo de el sistema de archivos FIunamFS. se debe proporcionar el nombre del archivo a eliminar tal cual aparece en la opción 1.
5. **Salir**

   Cierra el programa.

## Estrategia de desarrollo

El sistema de archivos se encuentra en un archivo binario de acuerdo con la especificación del proyecto, al abrir el archivo proporcionado por el usuario se hace la lectura de los primeros 64 bits del archivo, de acuerdo con las especificaciones estos corresponden al superbloque del sistema de archivos.
Aquí verificamos que el archivo proporcionado sea valido y la version correcta comparando los bits 0-8 y 10-14 con sus valores esperados, una vez confirmada la valides del FS se lee y almacena en memoria el tamaño del cluster para su uso posterior.

Una vez se ha verificado la validez del FS se hace la lectura del directorio, se lee cada entrada (de 64 bits), se decodifican los datos binarios a cadenas y números y se almacenan estos datos en un diccionario, cada entrada es un diccionario que as su vez se almacena en una lista, esto se hace para no abrir el archivo del FS cada vez que se necesita ver su contenido sin modificarLO y simplificar el manejo de los archivos.

Los procesos de lectura y escritura al FS se explican en la sección de concurrencia, pero vale la pena explicar la asignación de espacio en el FS usada para la escritura, esta se hace obteniendo el numero de clusters que necesita el archivo (redondeado hacia arriba) y obteniendo del directorio los clusters de inicio y fin de cada entrada, estos se guardan en tuplas y se ordenan de menor a mayor, se calcula la diferencia entre el inicio y fin de archivos adyacentes y se coloca el nuevo archivo en el primer cluster a partir del cual haya suficiente espacio.

Para la eliminación solo se eliminan los contenidos de la entrada del directorio correspondiente, no se eliminan los datos del archivo para agilizar la ejecución del programa.

## Concurrencia en el Sistema de Archivos FIunamFS

La concurrencia en este programa se utiliza en los métodos `copyfromFS()` y `copytoFS()` de la clase `FSsistop`. Estos métodos manejan la lectura y escritura de archivos en el sistema de archivos FIunamFS de manera concurrente usando un modelo de productor-consumidor para hacer la lectura en el sistema host concurrentemente con la escritura en el sistema de archivos.

Para la sincronización entre los procesos de lectura y escritura se utiliza una cola sincronizada utilizando la estructura  `queue` de python.

- `copyfromFS()`
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

- `copytoFS()`
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

La lógica en ambos métodos es relativamente similar con la diferencia en que se tiene que considerar de donde a donde se va a realizar la operación entre archivos.