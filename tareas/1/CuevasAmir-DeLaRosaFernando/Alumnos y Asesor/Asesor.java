import java.util.concurrent.Semaphore;
import java.util.Random;

class Asesor {
    // Semáforo para controlar cuando el profesor duerme/despierta.
    private Semaphore semProfesor = new Semaphore(0);
    // Semáforo para las sillas, permite hasta x alumnos esperando.
    private Semaphore semSillas;
    // Semáforo para permitir que solo un alumno pregunte a la vez.
    private Semaphore semTurno = new Semaphore(1);
    // Número de sillas disponibles en el cubículo.
    private int sillasDisponibles;
    
    public Asesor(int sillas) {
        this.sillasDisponibles = sillas;
        semSillas = new Semaphore(sillas);
    }
    
    // Método del profesor para atender a los alumnos.
    public void atender() {
        new Thread(() -> {
            try {
                while (true) {
                    // Espera a que haya al menos un alumno para atender
                    System.out.println("Asesor: Dormido, esperando estudiantes...");
                    semProfesor.acquire();
                    System.out.println("Asesor: Despierto, listo para atender...");
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
    
    // Método que simula a un alumno con preguntas.
    public void alumno(int id, int numPreguntas) {
        new Thread(() -> {
            try {
                // El alumno intenta sentarse, si no hay sillas libres, se va
                if (semSillas.tryAcquire()) {
                    System.out.println("Alumno " + id + ": *toc toc*, me voy a sentar, esperando mi turno.");
                    
                    // Despierta al profesor si es necesario
                    semProfesor.release();
                    
                    // Cada alumno hace entre 1 y numPreguntas
                    for (int i = 1; i <= numPreguntas; i++) {
                        semTurno.acquire(); // Solo un alumno puede preguntar a la vez
                        System.out.println("Alumno " + id + ": Pregunta " + i);
                        Thread.sleep(500); // Simular tiempo de respuesta del profesor
                        System.out.println("Asesor: Respuesta a alumno " + id + ", pregunta " + i);
                        semTurno.release();
                        // Espera un poco antes de hacer la próxima pregunta
                        Thread.sleep(new Random().nextInt(1000));
                    }
                    
                    System.out.println("Alumno " + id + ": Terminó sus preguntas, deja la silla.");
                    // Libera una silla para otro alumno
                    semSillas.release();
                } else {
                    System.out.println("Alumno " + id + ": No hay sillas libres, me voy.");
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
}
