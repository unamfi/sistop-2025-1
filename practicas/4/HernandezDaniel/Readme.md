# ¿Qué es mi programa?
Es un programa en Java que utiliza hilos (Lo que hemos estado viendo ultimamente), en este caso el programa es un generador de eventos que simula los Juegos del Hambre; donde cada participante es representado por un hilo de forma que los eventos sucedan de la forma más simultantea posible.
# ¿Cómo se compila el programa?
El programa utiliza para crear la GUI un paquete de Java que ya no se incluye en las versiones más recientes, llamado [JavaFX](https://openjfx.io/) por lo que es necesario descargar este paquete para ejecutarlo y compilarlo.

Se utiliza un .bat para poder ejecutar el programa de modo que el usuario pueda ejecutarlo comodamente, este .bat funciona para Windows y solo teniendo el JavaFX en la siguiente direccion: "C:\Java\javafx-sdk-21.0.1\lib".


De tal forma que el .bat ejecuta el siguiente comando:
```
@echo off
java --module-path "C:\Java\javafx-sdk-21.0.1\lib" --add-modules javafx.controls,javafx.fxml -jar YourApp.jar
pause
```
Para compilarlo (En el CMD de windows por lo menos) se utiliza el siguiente comando:
```
javac -d bin --module-path C:\Java\javafx-sdk-21.0.1\lib --add-modules javafx.controls,javafx.fxml,javafx.media src/*.java src/Cuenta/*.java src/JuegosDelHambre/*.java
```
De tal modo que se le dice al compilador que compile (vaya la redundancia) los paquetes mencionados y los ponga en la carpeta bin.

Y bueno con esto espero aclarar algunas dudas (si es que las hubo) porque me parece que es un programa complicado pero era lo más relacionado que tenia con lo visto recientemente.

PD: Este programa es de mi autoria en conjunto con dos compañeros y amigos mios; y fue entregado como un proyecto para la materia de Programacion Orientada a Objetos.