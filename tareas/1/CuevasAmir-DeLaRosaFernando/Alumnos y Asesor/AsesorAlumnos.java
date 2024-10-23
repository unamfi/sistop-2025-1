import java.util.concurrent.*;
import java.util.Random;
import java.util.ArrayList;
import java.util.List;

class AsesorAlumnos {
    static Semaphore sillas; // Controla el acceso a las sillas
    static Semaphore profesor; // Para despertar al profesor
    static Semaphore mutex; // Controla el acceso exclusivo al profesor
    static Semaphore estudiantesEnSala; // Controla el número total de estudiantes en la sala
    static int numSillas = 3; // Número de sillas disponibles
    static Semaphore estudiantesEsperando; // Contar cuántos estudiantes están esperando
    static boolean profesorDespierto = false; // Controlar si el profesor está despierto
    static List<Integer> estudiantesEnSilla = new ArrayList<>(); // Lista de estudiantes sentados
    static Random rand = new Random();
    
    // Colores para los alumnos
    static final String[] colores = {
        "\u001B[31m", // Rojo
        "\u001B[32m", // Verde
        "\u001B[33m", // Amarillo
        "\u001B[34m", // Azul
        "\u001B[35m", // Magenta
        "\u001B[36m", // Cian
        "\u001B[37m", // Blanco
        "\u001B[90m", // Gris
        "\u001B[91m", // Rojo Brillante
        "\u001B[92m", // Verde Brillante
    };

    public static void main(String[] args) {
        sillas = new Semaphore(numSillas); // Limitar las sillas
        profesor = new Semaphore(0); // El profesor duerme al principio
        mutex = new Semaphore(1); // Para que solo un alumno acceda al profesor a la vez
        estudiantesEsperando = new Semaphore(0); // Contar los estudiantes esperando
        estudiantesEnSala = new Semaphore(10); // Máximo 10 estudiantes en la sala

        // Hilo del profesor
        new Thread(() -> {
            try {
                while (true) {
                    // Si no hay estudiantes esperando, el profesor duerme
                    if (estudiantesEsperando.availablePermits() == 0) {
                        System.out.println("Asesor: Dormido, esperando estudiantes...");
                        profesorDespierto = false; // El profesor vuelve a estar dormido
                        profesor.acquire(); // Esperar hasta que lo despierten
                    }

                    // Si hay estudiantes esperando, el profesor atiende
                    mutex.acquire(); // Obtener acceso exclusivo al profesor
                    if (!profesorDespierto) {
                        System.out.println("Asesor: Despierto, listo para atender...");
                        profesorDespierto = true; // El profesor ya está despierto
                    }
                    mutex.release();
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();

        // Crear múltiples alumnos
        for (int i = 1; i <= 10; i++) {
            final int alumnoId = i;
            final String color = colores[i % colores.length]; // Asigna color a cada alumno
            new Thread(() -> {
                try {
                    // Intentar entrar a la sala (máximo 10 estudiantes)
                    if (estudiantesEnSala.tryAcquire()) {
                        // Intentar sentarse en una silla
                        if (sillas.tryAcquire()) {
                            System.out.println(color + "Alumno " + alumnoId + ": *toc toc*, me voy a sentar, espero mi turno." + "\u001B[0m");
                            estudiantesEnSilla.add(alumnoId); // El alumno toma una silla
                            estudiantesEsperando.release(); // Aumentar el número de estudiantes esperando

                            // Si el profesor está dormido, solo un alumno lo despierta
                            mutex.acquire();
                            if (!profesorDespierto) {
                                profesor.release(); // Despertar al profesor solo si está dormido
                            }
                            mutex.release();

                            // Cada alumno puede hacer un máximo de 3 preguntas
                            for (int j = 1; j <= 3; j++) {
                                // Acceso exclusivo al profesor para hacer la pregunta
                                mutex.acquire(); 
                                System.out.println(color + "Alumno " + alumnoId + ": Pregunta " + j + "\u001B[0m");
                                //System.out.println("Profesor: Alumno " + alumnoId + " mi respuesta a tu pregunta " + j + " es *bla bla*");
                                // Aseguramos que el mensaje "Despierto, listo para atender..." se imprima antes de la respuesta
                                if (!profesorDespierto) {
                                    System.out.println("Asesor: Despierto, listo para atender...");
                                    profesorDespierto = true; // El profesor ya está despierto
                                }

                                Thread.sleep(rand.nextInt(1000)); // Simular el tiempo de pregunta
                                System.out.println("Asesor: Respuesta a alumno " + alumnoId + ", pregunta " + j);
                                mutex.release(); // Liberar acceso al profesor

                                // Esperar a que otro alumno haga su pregunta
                                Thread.sleep(rand.nextInt(1000)); 
                            }

                            // Alumno termina sus preguntas
                            sillas.release(); // Liberar la silla
                            estudiantesEsperando.acquire(); // Disminuir el número de estudiantes esperando
                            estudiantesEnSilla.remove((Integer) alumnoId); // El alumno deja la silla
                            System.out.println(color + "Alumno " + alumnoId + ": Terminó sus preguntas, deja la silla." + "\u001B[0m");
                        } else {
                            System.out.println(color + "Alumno " + alumnoId + ": No hay sillas libres, me voy." + "\u001B[0m");
                            estudiantesEnSala.release(); // Liberar espacio en la sala
                        }
                    } else {
                        System.out.println(color + "Alumno " + alumnoId + ": La sala está llena, me voy." + "\u001B[0m");
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }).start();

            try {
                Thread.sleep(rand.nextInt(1000)); // Simular llegada de alumnos en diferentes momentos
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
