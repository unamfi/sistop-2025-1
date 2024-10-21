- El problema que decidieron resolver
    Los Alumnos y el asesor

- El lenguaje y entorno en que lo desarrollaron.
    Se utilizo Python desde Windows en el editor de textos Visual Studio Code

- ¿Qué tengo que saber / tener / hacer para ejecutar su programa en mi computadora?
    Tenemos entendido que Linux ya cuenta con Python por defecto en su instalación por lo que no seria necesario tener que instalarlo; sin embargo, hay que instalar o actualizar las librerias que ocupamos dentro de nuestro programa, son las siguientes:
        - threading (para el uso de hilos)
        - time (para usar el tiempo y ver como funciona nuestro codigo)
        - random (para poder hacer interactivo nuestro programa y que sea siempre diferente)
        - logging (para imprimir en consola lo que sale de nuestro codigo)

- La estrategia de sincronización (mecanismo / patrón) que emplearon para lograrlo
    Semáforos para limitar el número de alumnos que pueden esperar su turno en las sillas.
    Locks para asegurar que solo un alumno interactúa con el profesor a la vez.