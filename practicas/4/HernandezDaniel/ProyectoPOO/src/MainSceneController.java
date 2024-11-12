import java.io.IOException;
import java.util.List;
import java.util.Stack;
import Cuenta.Admin;
import Cuenta.Usuario;
import Cuenta.Utilerias;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;
public class MainSceneController {
    
    @FXML
    private TextField Usuariotf;
    
    @FXML
    private PasswordField Contrasenatf;

    @FXML
    private Pane Menu;

    private Stack<Scene> sceneStack = new Stack<>();
    private void agregarEscena(String fxml) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource(fxml));
            Parent root = loader.load();
            Scene scene = new Scene(root);
            sceneStack.push(scene);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void cerrarEscenaActual() {
        Scene escenaActual = Usuariotf.getScene();
        Stage stage = (Stage) escenaActual.getWindow();
        stage.close();
    }
    private void abrirUltimaEscena() {
        if (!sceneStack.isEmpty()) {
            Scene ultimaEscena = sceneStack.pop();
            Stage stage = (Stage) Usuariotf.getScene().getWindow();
            stage.setScene(ultimaEscena);
            stage.show();
        }
    }
    @FXML
    void iniciarsesion(){
        Stage Iniciodesesion = (Stage) Usuariotf.getScene().getWindow();
        sceneStack.push(Iniciodesesion.getScene());
        String Usuario = Usuariotf.getText();
        String Contrasena = Contrasenatf.getText();
        Admin administrador = Isadmin(Usuario, Utilerias.hashPassword(Contrasena));
        if(administrador != null){
            cerrarEscenaActual();
            administrador.acceder();
            abrirUltimaEscena();
        }else{
            Usuario usuario = IsUser(Usuario, Utilerias.hashPassword(Contrasena));
                if(usuario !=null){
                    cerrarEscenaActual();
                    usuario.acceder();
                    abrirUltimaEscena();
                }else{
                    String Usuarioinexistente = "El usuario no existe";
                    mostrarAlerta("Usuario no encontrado", Usuarioinexistente);
                }
        }
        
        
    }
    Admin Isadmin(String Usuario, String Password){
        try {
        List<Admin> usuarios = Admin.leerUsuariosDesdeArchivo();
        for (Admin u : usuarios) {
            if (u.getUsername().equals(Usuario) && u.getPassword().equals(Password)) {
                return u; // Usuario y contraseña coinciden
            }
        }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    
    Usuario IsUser(String User, String Password){
        try {
        List<Usuario> usuarios = Usuario.leerUsuariosDesdeArchivo();
        for (Usuario u : usuarios) {
            if (u.getUsername().equals(User) && u.getPassword().equals(Password)) {
                return u; // Usuario y contraseña coinciden
            }
        }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    private void mostrarAlerta(String titulo, String mensaje) {
        Alert alert = new Alert(AlertType.INFORMATION);
        alert.setTitle(titulo);
        alert.setHeaderText(null);
        alert.setContentText(mensaje);
        alert.showAndWait();
    }

    private void cambiarEscena(String fxml) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource(fxml));
            Parent root = loader.load();
            Stage stage = (Stage) Usuariotf.getScene().getWindow();
            stage.setScene(new Scene(root));
        } catch (IOException e) {
            e.printStackTrace();
        }



        
    }

}
