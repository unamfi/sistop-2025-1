package JuegosDelHambre;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Set;
public interface Tributo{
    void event(LinkedList<Participante> participantes, boolean random, int event);
    void stats();
    boolean verificate();
    void kill(Participante participante);
}
