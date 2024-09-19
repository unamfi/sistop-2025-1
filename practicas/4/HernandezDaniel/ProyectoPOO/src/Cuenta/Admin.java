package Cuenta;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.security.AccessController;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;
import javax.sound.sampled.LineEvent;
import javax.sound.sampled.LineListener;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Side;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.MenuItem;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.control.TextInputDialog;
import javafx.scene.layout.Pane;
import javafx.scene.media.AudioClip;
import javafx.stage.Stage;
import JuegosDelHambre.JuegosDelHamre;
import JuegosDelHambre.Participante;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Alert.AlertType;
public class Admin implements Cuenta {
    private String username;
    private String password;
    public  LinkedList<Participante>  participantesSeleccionados = new LinkedList<>();
    public Admin(String username, String password) {
        this.username = username;
        this.password = password;
    }
    @FXML public TextArea Events;
    @FXML private Label vistaadmin;
    @FXML private Button Clear;
    @FXML private Button TributosAleatorios;
    @FXML private Button SeleccionarTributoss;
    @FXML private Button AgregarArchivo;
    @FXML private Button Iniciar;
    @FXML private Button Neblina;
    @FXML private Button Lluvia;
    @FXML private Button obligar;
    @FXML private Button EventoAleatorio;
    @FXML private TextArea TAparticipantes;
    @FXML
    private void mostrarParticipantesSeleccionados() {
        StringBuilder contenido = new StringBuilder("Participantes Seleccionados:\n");
        TAparticipantes.clear();
        int i = 0;
        System.out.println("Numero total : " + participantesSeleccionados.size());
        for (Participante participante : participantesSeleccionados) {
            if (participante != null) {
                i++;
                contenido.append(i).append(": ").append("Nombre: ").append(participante.getNombre())
                        .append(", Vida: ").append(participante.getVida()).append("\n");
            }
        }
        TAparticipantes.setText(contenido.toString());
    }
    public void imprimirMensaje(String mensaje) {
        Events.appendText(mensaje + "\n");
    }


    public Admin() {
    }
    public void cerrarEscenaActual() {
        Scene escenaActual = vistaadmin.getScene();
        Stage stage = (Stage) escenaActual.getWindow();
        stage.close();
    }
    public String getUsername() {
        return this.username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return this.password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
    
    @Override
    public void acceder() {
            try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("AdminScene.fxml"));
            Parent root = loader.load();
            Stage adminStage = new Stage();
            adminStage.setTitle("Ventana del Administrador");
            adminStage.setScene(new Scene(root));
            adminStage.showAndWait();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

     public static LinkedList<Admin> leerUsuariosDesdeArchivo() throws IOException {
        LinkedList<Admin> usuarios = new LinkedList<>();
        try (BufferedReader br = new BufferedReader(new FileReader("src/Cuenta/Adminusers.txt"));        ) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(" ");
                if (partes.length == 2) {
                    String nombreUsuario = partes[0];
                    String contrasena = partes[1];
                    Admin usuario = new Admin(nombreUsuario, contrasena);
                    usuarios.add(usuario);
                } else {
                    System.out.println("Formato incorrecto en línea: " + linea);
                }
            }
        }
        return usuarios;
    }

        private static void escribirEnArchivo(LinkedList<Participante> set) {
            
        try (ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("src/JuegosDelHambre/Tributos.txt"))) {
            outputStream.writeObject(set);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static LinkedList<Participante> leerYGuardarContenido() {
        LinkedList<Participante> lista = null;
        try (ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("src/JuegosDelHambre/Tributos.txt"))) {
             lista = (LinkedList<Participante>) inputStream.readObject();

        } catch (IOException | ClassNotFoundException e) {
            return null;
        }
        return lista;
    }

    @FXML
    public LinkedList<Participante> SeleccionarTributos(){
         LinkedList<Participante> lista = leerYGuardarContenido();
        if(lista == null){
        Utilerias.mostrarAlerta("Participantes insuficientes", "Para seleccionar tributos primero crea 24 tributos.");               
        return null;
        }else if(lista.size() <24){  
            Utilerias.mostrarAlerta("Participantes insuficientes", "Para seleccionar tributos primero crea 24 tributos.");
            return null;
        }
        return lista;
    }
    @FXML
    private void handleAgregarParticipantes() {
        // Crear un TextInputDialog para obtener el nombre del nuevo participante
        TextInputDialog dialog = new TextInputDialog();
        LinkedList<Participante> lista  = leerYGuardarContenido();
        if(lista == null)
        lista = new LinkedList<>();
        dialog.setTitle("Agregar Participante");
        dialog.setHeaderText(null);
        dialog.setContentText("Ingrese el nombre del nuevo participante:");

        // Obtener la respuesta del diálogo
        Optional<String> result = dialog.showAndWait();
    // Declarar la variable fuera del bloque lambda
    String nombreParticipante;
    Participante addp = null;
    // Si se proporciona un nombre, guárdalo en una cadena
    if (result.isPresent()) {
        nombreParticipante = result.get();
        // Puedes hacer lo que quieras con la cadena 'nombreParticipante'
         addp = new Participante(nombreParticipante, 100);
    } else {
        addp = null;
    }
    lista.add(addp);
    escribirEnArchivo(lista);
    }

    @FXML
    private void handleSeleccionarTributos() {
        LinkedList<Participante> tributosSeleccionados = SeleccionarTributos();
        System.out.println("Tamaño de tributosSeleccionados: " + tributosSeleccionados.size());
        if(participantesSeleccionados.size()>=24){
            Utilerias.mostrarAlerta("Sin espacio", "Ya hay 24 tributos");
            return;
        }
        // Crear un menú contextual con elementos del conjunto de participantes
        ContextMenu contextMenu = new ContextMenu();
        for (Participante participante : tributosSeleccionados) {
            if(participante!=null){
            MenuItem menuItem = new MenuItem(participante.getNombre());
            menuItem.setOnAction(event -> agregarParticipanteSeleccionado(participante));
            contextMenu.getItems().add(menuItem);
            }

        }
        // Mostrar el menú contextual cerca del botón
        contextMenu.show(SeleccionarTributoss, Side.BOTTOM, 0, 0);
        

    }
    private void agregarParticipanteSeleccionado(Participante participante) {
        participantesSeleccionados.add(participante);
        System.out.println("Participante seleccionado: " + participante.getNombre());
        mostrarParticipantesSeleccionados();
        // Puedes realizar otras operaciones aquí según tus necesidades
    }

    public void Aleatorio() {
  LinkedList<Participante> lista = SeleccionarTributos();
    lista.removeIf(participante -> participante == null);
        if(lista != null){
        // Clonar la lista original
        LinkedList<Participante> listaClonada = new LinkedList<>(lista);
        // Barajar la lista clonada
        Collections.shuffle(listaClonada);
        // Crear una nueva lista con los primeros 24 elementos de la lista barajada
        LinkedList<Participante> lista2 = new LinkedList<>(listaClonada.subList(0, 24));
        participantesSeleccionados = lista2;
        mostrarParticipantesSeleccionados();
        }

    }

    public void iniciarjuegos(){
        if(participantesSeleccionados.size()<24){
            Utilerias.mostrarAlerta("No hay jugadores suficientes para empezar", "No hay jugadores suficientes para empezar " + participantesSeleccionados.size()+"/24");
            return;
        }
    try {
            File archivoSonido = new File("src/JuegosDelHambre/Empieza.wav");
            AudioInputStream audioStream = AudioSystem.getAudioInputStream(archivoSonido);
            // Abre el clip
            Clip clip = AudioSystem.getClip();
            clip.open(audioStream);
    
            // Agregar un LineListener para controlar eventos
            clip.addLineListener(new LineListener() {
                @Override
                public void update(LineEvent event) {
                    if (event.getType() == LineEvent.Type.STOP) {
                        clip.close();
                    }
                }
            });
            // Reproduce el sonido
            clip.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
        TributosAleatorios.setVisible(false);
        Iniciar.setVisible(false);
        SeleccionarTributoss.setVisible(false);
        AgregarArchivo.setVisible(false);
        Clear.setVisible(false);
        Neblina.setVisible(true);
        Lluvia.setVisible(true);
        EventoAleatorio.setVisible(true);
        obligar.setVisible(true);
    }


    public void juegosdelhambre(){
            Participante.participantes = participantesSeleccionados;
        for (Participante participante : participantesSeleccionados) {
       
            if (participante != null) {
                participante.admin = this;
                Thread thread = new Thread(participante);
                // Iniciar el hilo
                thread.start();
            }
        }
        participantesSeleccionados = Participante.participantes;
        TAparticipantes.clear();
        mostrarParticipantesSeleccionados();
        Participante winner = howManyAlive();
        if(winner!=null){
            Utilerias.mostrarAlerta("GANADOR",winner.getNombre() + " ha ganado los juegos");
            JuegosDelHamre juego = new JuegosDelHamre(Events.getText(), winner.getNombre());       
            ArrayList<JuegosDelHamre> lista =   (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
            lista.add(juego);
            JuegosDelHamre.guardarLista(lista);
                Neblina.setVisible(false);
                Lluvia.setVisible(false);
                
                EventoAleatorio.setVisible(false);
                 obligar.setVisible(false);
        }

    }

    public void activarneblincatoxica(){
               Participante.participantes = participantesSeleccionados;
             Participante p = new Participante("Test", 0);
            p.admin = this;
        p.event(Participante.participantes, false, 6);
        participantesSeleccionados = Participante.participantes;
        TAparticipantes.clear();
        mostrarParticipantesSeleccionados();
        Participante winner = howManyAlive();
        if(winner!=null){
            Utilerias.mostrarAlerta("GANADOR",winner.getNombre() + " ha ganado los juegos");
            JuegosDelHamre juego = new JuegosDelHamre(Events.getText(), winner.getNombre());       
            ArrayList<JuegosDelHamre> lista =   (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
            lista.add(juego);
            JuegosDelHamre.guardarLista(lista);
                Neblina.setVisible(false);
                Lluvia.setVisible(false);
                EventoAleatorio.setVisible(false);;
                obligar.setVisible(false);
        }
    }

        public void activarlluviaacida(){
               Participante.participantes = participantesSeleccionados;
             Participante p = new Participante("Test", 0);
                        p.admin = this;
        p.event(Participante.participantes, false, 5);
        participantesSeleccionados = Participante.participantes;
        TAparticipantes.clear();
        mostrarParticipantesSeleccionados();
        Participante winner = howManyAlive();
        if(winner!=null){
            Utilerias.mostrarAlerta("GANADOR",winner.getNombre() + " ha ganado los juegos");
            JuegosDelHamre juego = new JuegosDelHamre(Events.getText(), winner.getNombre());       
            ArrayList<JuegosDelHamre> lista =   (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
            lista.add(juego);
            JuegosDelHamre.guardarLista(lista);
                 Neblina.setVisible(false);
                Lluvia.setVisible(false);
                EventoAleatorio.setVisible(false);;
                obligar.setVisible(false);
        }
    }
    public void obligar(){
        Participante.participantes = participantesSeleccionados;
                // Crear un menú contextual con elementos del conjunto de participantes
        ContextMenu contextMenu = new ContextMenu();
        for (Participante participante : Participante.participantes) {
            if(participante!=null && participante.verificate()){
            participante.admin = this;
            MenuItem menuItem = new MenuItem(participante.getNombre());
            menuItem.setOnAction(event -> participante.event(participantesSeleccionados, false, 4));
            contextMenu.getItems().add(menuItem);
            }

        }
        // Mostrar el menú contextual cerca del botón
        contextMenu.show(SeleccionarTributoss, Side.BOTTOM, 0, 0);
         participantesSeleccionados = Participante.participantes;
        TAparticipantes.clear();
        mostrarParticipantesSeleccionados();
        Participante winner = howManyAlive();
        if(winner!=null){
            Utilerias.mostrarAlerta("GANADOR",winner.getNombre() + " ha ganado los juegos");
            JuegosDelHamre juego = new JuegosDelHamre(Events.getText(), winner.getNombre());       
            ArrayList<JuegosDelHamre> lista =   (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
            lista.add(juego);
            JuegosDelHamre.guardarLista(lista);
                 Neblina.setVisible(false);
                Lluvia.setVisible(false);
                EventoAleatorio.setVisible(false);;
                obligar.setVisible(false);
        }
        
    }
    public Participante howManyAlive() {
        int count = 0;
        Participante aliveParticipant = null;
    
        for (Participante participante : participantesSeleccionados) {
            if(participante!=null)
            if (participante.getVida() > 0) {
                count++;
                aliveParticipant = participante;
            }
        }
    
        // Si solo hay un participante con vida 100, devolver ese participante, de lo contrario, devolver null
        return (count == 1) ? aliveParticipant : null;
    }

    public void clear(){
        participantesSeleccionados.clear();
        TAparticipantes.clear();
    }







    /* 
    public static LinkedList<Usuario> usuariosPredefinidos(){
        List<Usuario> lista = Arrays.asList(
            new Usuario("sebjimort", "d806c65a1d870df0495040640ebf2ad3627f628c44cb02170be5c13722873cce"),// Password: mainjax
            new Usuario("danieloct", "668252554336f961032c233686448b24eea52620be071dc9d4afcb5c72240c5b"),// Pasword: yasuoplayer
            new Usuario("isaac", "8fc9c94f022d84cf039b70ae22bc104792906a105462e9765dd6d86aa345d4b0"),// Password: perro
            new Usuario("raulo", "a4e7c6ae4013276deabc1be4f9c65a6dc382f317e0cb81497aba26915cde5b66"),// Password: contrasenia
            new Usuario("remi", "f3e8fb4bf3f9c12e1939c1d999b4ad29c4a64cfcb5e78f84d39a3e74f9dd5908")// Password: piope
        );
		LinkedList<Usuario> newLinkedList = new LinkedList<>();
        for(Usuario i : lista) newLinkedList.add(i);
        return newLinkedList;
    }
    */
}
