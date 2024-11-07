# Sistema de Archivos - Proyecto de Sistemas Operativos

## Autores
- **Ortiz Moreno Ximena**
- **Sánchez Gachuz Jennyfer Estefanía**

## Problema a Resolver
Este proyecto implementa un sistema de archivos simulado en Python. El sistema debe gestionar la creación, modificación, eliminación y listado de archivos dentro de un espacio limitado (similar a un disquete), con soporte para la sincronización entre operaciones concurrentes y estructura de datos adecuada para la gestión de archivos. 

## Estrategia de Sincronización
El sistema de archivos utiliza varios mecanismos de sincronización para garantizar la integridad de los datos en un entorno concurrente:

- **Hilos**: Cada operación principal (creación, eliminación, copia de archivos) se maneja en un hilo independiente, lo que permite que múltiples operaciones se ejecuten concurrentemente.
  
- **Exclusión mutua**: Un objeto `Lock` asegura que solo un hilo pueda acceder o modificar los datos del sistema de archivos al mismo tiempo, evitando condiciones de carrera al manejar archivos compartidos.

- **Variables de condición**: Condiciones específicas se utilizan para coordinar la espera y notificación entre hilos. Esto permite que los hilos notifiquen cambios de estado (como la disponibilidad de espacio libre) y optimiza el uso de los recursos.

## Requisitos del Proyecto
Para desarrollar este sistema de archivos, se emplearon las siguientes técnicas y requisitos:

- **Formato del sistema de archivos**: Se simula un sistema de archivos de 1.44 MB, similar a un disquete. Este sistema se gestiona en un archivo binario de longitud fija, donde se dividen los sectores en clusters para almacenar los datos de los archivos.
- **Representación de archivos**: Cada archivo se representa en un directorio plano que almacena sus atributos, como nombre, tamaño, fecha de creación, fecha de modificación y el cluster de inicio en el almacenamiento.
- **Asignación contigua**: Para optimizar la búsqueda y recuperación de archivos, el sistema emplea una asignación contigua, donde cada archivo ocupa un bloque continuo de clusters en la imagen.

## Ejemplos de Uso

1. **Listar archivos**:  
   Ejecuta la función para listar los archivos en el sistema, lo que muestra el nombre, tamaño y fechas de cada archivo. Esta función muestra los datos almacenados en el directorio de `FiUnamFS`.

2. **Copiar un archivo desde el Sistema Operativo a FiUnamFS**:  
   Selecciona un archivo en el sistema operativo y cópialo a `FiUnamFS`. El archivo debe caber en el sistema simulado y ocupará un espacio contiguo en clusters.

3. **Copiar un archivo desde FiUnamFS al sistema Operativo**:  
   Especifica el nombre del archivo dentro de `FiUnamFS` y selecciona el destino en el sistema operativo para exportar el archivo.

4. **Eliminar un archivo**:  
   Al seleccionar un archivo en `FiUnamFS` y eliminarlo, se marca el archivo como eliminado en el directorio, liberando su espacio en el sistema de archivos.

## Entorno y Dependencias

### Entorno de Desarrollo
- **Lenguaje**: Python 3
- **Entorno de Desarrollo**: El entorno de desarrollo es independiente de la plataforma, por lo que puede ejecutarse en cualquier sistema operativo que tenga instalado Python 3.

  
### Dependencias
Este proyecto no requiere librerías externas, ya que utiliza solo módulos de la biblioteca estándar de Python:

- **threading**: Para manejar la concurrencia y sincronización entre hilos.
- **struct**: Para gestionar datos binarios, necesarios para almacenar enteros y cadenas en el sistema de archivos.
- **os**: Para operaciones de sistema de archivos, como rutas y manejo de archivos en el sistema operativo.
- **time**: Para manejar fechas de creación y modificación en el sistema de archivos.

## Instrucciones para correr el programa

Para ejecutar el programa en su computadora, necesita:

- **Python 3 instalado**: Puede verificar la instalación ejecutando el siguiente comando en su terminal o línea de comandos:
    ```bash
    python --version
    ```
    o
    ```bash
    python3 --version
    ```
    Si Python no está instalado, puede descargarlo e instalarlo desde la [página oficial de Python](https://www.python.org/downloads/).

- **No se requieren librerías externas**: El programa utiliza únicamente módulos estándar de Python, por lo que no es necesario instalar librerías adicionales.

- **Ejecutar el programa**: Abra una terminal o línea de comandos, navegue hasta el directorio donde guardó los archivos del programa, y ejecute uno de los siguientes comandos:
    ```bash
    python interfaz_fiunamfs.py
    ```
    o
    ```bash
    python3 interfaz_fiunamfs.py
    ```

**Nota**: Asegúrese de que los archivos `sistema_fiunamfs.py` e `interfaz_fiunamfs.py` estén en el directorio actual desde el cual está ejecutando el comando.

## Problemas Conocidos

### 1. Problemas con la función de copiar del Sistema Operativo a `FiUnamFS`

La función de **copiar archivos desde el sistema operativo a `FiUnamFS`** presenta un problema donde, al copiar los archivos, las fechas de creación y modificación no se almacenan correctamente en `FiUnamFS`. En algunos casos, las fechas aparecen como `00000000000000` o con valores incorrectos, a pesar de que se intenta escribir la fecha y hora en el formato adecuado (`AAAAMMDDHHMMSS`).

#### Posible Causa

Este problema puede estar relacionado con:
- **Errores en la escritura o lectura de datos en el sistema de archivos**: Es posible que el sistema no esté almacenando los datos correctamente en el formato especificado.
- **Problemas de alineación o offset de los bytes**: La lectura y escritura de los bytes en el archivo pueden estar desplazadas, lo que provoca que los datos de las fechas no se interpreten correctamente en el sistema `FiUnamFS`.
