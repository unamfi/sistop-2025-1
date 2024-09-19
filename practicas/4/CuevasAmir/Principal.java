import java.util.Random; // For Atleta class
import java.time.LocalDateTime; // For Atleta class

public class Principal { // Solo esta clase es pública porque coincide con el nombre del archivo
    public static void main(String[] args) {
        System.out.println("\n\n INICIANDO CARRERA\n\n");

        Equipo equipoAzul = new Equipo("Azul");
        Equipo equipoRojo = new Equipo("Rojo");

        equipoAzul.iniciarEquipo();
        equipoAzul.start();
        equipoRojo.iniciarEquipo();
        equipoRojo.start();
    }
}

class Equipo extends Thread { // Clase no pública
    private String nombre;
    private Thread[] atletas = new Thread[4];

    public Equipo(String nombre) {
        this.nombre = nombre;

        for (int i = 0; i < 4; i++) {
            atletas[i] = new Thread(new Atleta(), nombre + " " + i);
        }
    }

    public void iniciarEquipo() {
        System.out.println("Comienza la carrera para " + nombre);
    }

    public void imprimeFinalizada() {
        System.out.println("Carrera TERMINADA por el equipo " + nombre);
    }

    public void run() {
        for (int i = 0; i < atletas.length; i++) {
            atletas[i].start();
            try {
                atletas[i].join(); // Espera a que cada atleta termine antes de iniciar el siguiente
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        imprimeFinalizada();
    }
}

class Atleta extends Thread { // Clase no pública
    public void run() {
        Random r = new Random();
        System.out.println("El atleta " + Thread.currentThread().getName() + " inició a correr. [" + LocalDateTime.now() + "]");

        try {
            Thread.sleep(r.nextInt(3000) + 500); // Simula diferentes tiempos para cada atleta
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        System.out.println("El atleta " + Thread.currentThread().getName() + " terminó sus 100[m] [" + LocalDateTime.now() + "]");
    }
}
