import java.io.IOException;
import java.util.ArrayList;

import JuegosDelHambre.JuegosDelHamre;
import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
 
public class App extends Application {
    @Override
    public void start(Stage primaryStage) {
    
  Parent root;
try {
    root = FXMLLoader.load(getClass().getResource("MainScene.fxml"));
      Scene scene = new Scene(root);  
    primaryStage.setTitle("Juegos del Hambre");
        primaryStage.setScene(scene);
        primaryStage.show();
} catch (IOException e) {
    e.printStackTrace();
}


}

 public static void main(String[] args) {
        launch(args);
    }
}