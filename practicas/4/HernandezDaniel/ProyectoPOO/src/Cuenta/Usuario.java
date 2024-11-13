package Cuenta;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;

import JuegosDelHambre.JuegosDelHamre;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextArea;
import javafx.stage.Stage;
public class Usuario implements Cuenta {
    private String username;
    private String password;
    static int i=0;
    @FXML private Label winner;
    @FXML public TextArea Eventos;
    @FXML private Button Anterior;
    @FXML private Button Siguiente;
    @FXML private Button Mostrar;
    public Usuario(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public Usuario() {
    }
    
    @FXML
    private Label vistausuario;
    public void cerrarEscenaActual() {
        Scene escenaActual = vistausuario.getScene();
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
            FXMLLoader loader = new FXMLLoader(getClass().getResource("UsuarioScene.fxml"));
            Parent root = loader.load();
            Stage UsuarioStage = new Stage();
            UsuarioStage.setTitle("Menu de Usuario");
            UsuarioStage.setScene(new Scene(root));
            UsuarioStage.showAndWait();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
        public void imprimirMensaje(String mensaje) {
        Eventos.appendText(mensaje + "\n");
    }
         public static LinkedList<Usuario> leerUsuariosDesdeArchivo() throws IOException {
        LinkedList<Usuario> usuarios = new LinkedList<>();

        try (BufferedReader br = new BufferedReader(new FileReader("src/Cuenta/users.txt"))) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(" ");
                if (partes.length == 2) {
                    String nombreUsuario = partes[0];
                    String contrasena = partes[1];
                    Usuario usuario = new Usuario(nombreUsuario, contrasena);
                    usuarios.add(usuario);
                } else {
                    System.out.println("Formato incorrecto en línea: " + linea);
                }
            }
        }

        return usuarios;
    }

    public void atras(){
        ArrayList<JuegosDelHamre> juegos = (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
        i--;
        if(i<0){
            i=juegos.size()-1;
        }
        Eventos.setText(juegos.get(i).getEventos());
        winner.setText(juegos.get(i).getGanador());
    }
    public void adelante(){
        ArrayList<JuegosDelHamre> juegos = (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
        i++;
        if(i==juegos.size()){
            i=0;
        }
      
        Eventos.setText(juegos.get(i).getEventos());
        winner.setText(juegos.get(i).getGanador());
    }

        public void show(){
        ArrayList<JuegosDelHamre> juegos = (ArrayList<JuegosDelHamre>) JuegosDelHamre.cargarLista();
        Eventos.setText(juegos.get(0).getEventos());
        winner.setText(juegos.get(0).getGanador());
    }


    /*
   
    public static LinkedList<Usuario> usuariosPredefinidos(){
        List<Usuario> lista = Arrays.asList(
            new Usuario("twyblade", "26a4938ee320f831c3b6c5bae4573c6c18a8949879e9370c7d49f4c869c56a42"),// Paswword: mytsvwerbr
            new Usuario("lerioar", "61de60d7e2449da2e11d4a662a0cc0c3996fc866e6bd8fd9a35dbee2279ab400"),// Paswword: ovejas
            new Usuario("lalolo", "fd26cc45fb122b5bfcdd3180bc0340143c9e435fbe3373d78afb3b699927b8a7"),// Paswword: perrocat
            new Usuario("kargon", "d0a35dab95d09d3d0c954baa626b5d6db18271a62209d84ffb494f537665bad5"),// Paswword: perasmanzanas
            new Usuario("sofi", "130026f20a38ecfb6761f77c1d845d7ac33122c7e821c12a3810588a3e2b6375")// Paswword: opimoeen
		);
		LinkedList<Usuario> newLinkedList = new LinkedList<>();
        for(Usuario i : lista) newLinkedList.add(i);
        return newLinkedList;
    }
    */  
 }