package JuegosDelHambre;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.EOFException;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class JuegosDelHamre implements Serializable {
    String Eventos;
    String Ganador;

    public JuegosDelHamre(String Eventos, String Ganador) {
        this.Eventos = Eventos;
        this.Ganador = Ganador;
    }

    public String getEventos() {
        return this.Eventos;
    }

    public void setEventos(String Eventos) {
        this.Eventos = Eventos;
    }

    public String getGanador() {
        return this.Ganador;
    }

    public void setGanador(String Ganador) {
        this.Ganador = Ganador;
    }
           public static void guardarLista(List<JuegosDelHamre> lista) {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("src/JuegosDelHambre/Juegos.txt"))) {
            oos.writeObject(lista);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

public static List<JuegosDelHamre> cargarLista() {
    List<JuegosDelHamre> lista = new ArrayList<>();
    try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("src/JuegosDelHambre/Juegos.txt"))) {
        Object obj;
        while ((obj = ois.readObject()) != null) {
            if (obj instanceof List) {
                lista = (List<JuegosDelHamre>) obj;
            }
        }
    } catch (EOFException e) {
        // Se alcanzó el final del archivo (EOF), se puede ignorar o manejar según tus necesidades.
    } catch (IOException | ClassNotFoundException e) {
        e.printStackTrace();
    }
    return lista;
}
}