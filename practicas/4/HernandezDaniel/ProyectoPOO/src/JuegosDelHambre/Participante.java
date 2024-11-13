package JuegosDelHambre;
import java.util.Random;
import java.util.Set;

import Cuenta.Admin;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.TextArea;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;

public class Participante implements Tributo, Runnable, Serializable {
    public Admin admin;
    private String nombre;
    private int vida;
    public static Event event = null;
    public static LinkedList<Participante> participantes;
    public Participante(String nombre, int vida) {
        this.nombre = nombre;
        this.vida = vida;
    }


    public String getNombre() {
        return this.nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public int getVida() {
        return this.vida;
    }

    public void setVida(int vida) {
        this.vida = vida;
    }



    @Override
    public void event(LinkedList <Participante> participantes, boolean random, int eventid) {
        int idEvent;
        Random rand = new Random();
        if(random ==true)
            idEvent = rand.nextInt(6) + 1;
        else
            idEvent = eventid;
        switch (idEvent) {
            case 1:
                Platform.runLater(() -> {
                admin.imprimirMensaje(this.getNombre() + " encontro Suministros + 20HP");});
                System.out.println(this.getNombre() + " encontro Suministros");
                this.vida+=20;
                break;
            case 2:
               Platform.runLater(() -> {
                admin.imprimirMensaje(this.getNombre() + " recibio una donacion + 50 HP");});
                System.out.println(this.getNombre() + " recibio una donacion + 50 HP");
                this.vida+=50;
                break;
            case 3:
                Platform.runLater(() -> {
                admin.imprimirMensaje(this.getNombre() + " encontro agua apta para el consumo + 10HP");});
                System.out.println(this.getNombre() + " encontro agua apta para el consumo + 10HP");
                this.vida+=10;
                break;
            case 6:
                if(participantes!=null)
                synchronized (participantes) {
                    for (Participante affected : participantes) {
                        int effect;
                        event = new Event("Neblina toxica", 20);
                        if(affected != null)
                        if (affected.getVida() >0 ) {
                            effect = rand.nextInt(3) + 1;
                            switch (effect) {
                                case 1:
                                    Platform.runLater(() -> {
                                    admin.imprimirMensaje(affected.getNombre() + " Sufrio " + event.damage * 0.1 + " Por neblina toxica");});
                                    affected.setVida(affected.getVida() - (int) (event.damage * 0.1));
                                    break;
                                case 2:
                                    Platform.runLater(() -> {
                                    admin.imprimirMensaje(affected.getNombre() + " Sufrio " + event.damage * 0.5 + " Por neblina toxica");});
                                    affected.setVida(affected.getVida() - (int) (event.damage * 0.5));
                                    break;
                                case 3:
                                    Platform.runLater(() -> {
                                    admin.imprimirMensaje(affected.getNombre() + " Sufrio " + event.damage + " Por neblina toxica");});
                                    affected.setVida(affected.getVida() - event.damage);
                                    break;
                            }
                        }
                    }
                }
                break;
            case 5:
            if(participantes!=null)
            synchronized (participantes) {
                for (Participante affected : participantes) {
                    int effect;
                    event = new Event("Lluvia acida", 10);
                    if(affected != null)
                    if (affected.getVida() > 0) {
                        effect = rand.nextInt(3) + 1;
                        switch (effect) {
                            case 1:
                                    Platform.runLater(() -> {
                                    admin.imprimirMensaje(affected.getNombre() + " Sufrio " + event.damage * 0.1 + " Por lluvia acida");});
                                affected.setVida(affected.getVida() - (int) (event.damage * 0.1));
                                break;
                            case 2:
                                    Platform.runLater(() -> {
                                    admin.imprimirMensaje(affected.getNombre() + " Sufrio " + event.damage * 0.5 + " Por lluvia acida");});
                                affected.setVida(affected.getVida() - (int) (event.damage * 0.5));
                                break;
                            case 3:
                             Platform.runLater(() -> {
                            admin.imprimirMensaje(affected.getNombre() + " Sufrio " + event.damage + " Por lluvia acida");});
                                affected.setVida(affected.getVida() - event.damage);
                                break;
                        }
                    }
                }
            }
                break;
            case 4:
                if (participantes != null) {
                    synchronized (participantes) {
                        int v;
                        while (true) {
                            v = rand.nextInt(participantes.size());
                    
                            Participante affected = participantes.get(v);
            
                            // Verificar si el participante está vivo
                            if(affected!=null)
                            if (affected.getVida() > 0) {
                                // Realizar la operación sobre el participante seleccionado
                                this.kill(affected);
                                break;
                            }
                        }
                    }
                }
                break;
        }
    }

    @Override
    public void stats() {
        System.out.println("Nombre: "+ nombre);
        System.out.println("Vida: " + vida);
    }

    @Override
    public boolean verificate(){
        if (this.getVida() <= 0)
            return false;
        else
            return true;
    }

    @Override
    public void kill(Participante participante) {
        participante.setVida(0);
        if(participante == this){
            Platform.runLater(() -> {
                admin.imprimirMensaje(this.getNombre() + " tomo el camino facil");});
            System.out.println(this.getNombre() + "tomo el camino facil");
        }else
            Platform.runLater(() -> {
                admin.imprimirMensaje(this.getNombre() + " mato a " + participante.getNombre());});
            System.out.println(this.getNombre() + " mato a " + participante.getNombre());
    }

    @Override
    public void run() {
        if(verificate())
        this.event(participantes , true, 0);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Participante that = (Participante) obj;
        return nombre.equals(that.nombre);
    }




}
