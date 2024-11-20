import java.util.*;

public class AdministradorProcesos {
    public static void main(String[] args) {
        // Carga inicial de procesos
        Map<String, int[]> administradorProcesos = new HashMap<>(); //Se hace uso de un Map para almacenar los procesos 
        administradorProcesos.put("A", new int[]{0, 3, 0, 0, 0, 0, 0, 0, 0}); 
        administradorProcesos.put("B", new int[]{1, 5, 0, 0, 0, 0, 0, 0, 0});
        administradorProcesos.put("C", new int[]{3, 2, 0, 0, 0, 0, 0, 0, 0});
        administradorProcesos.put("D", new int[]{9, 5, 0, 0, 0, 0, 0, 0, 0});
        administradorProcesos.put("E", new int[]{12, 5, 0, 0, 0, 0, 0, 0, 0});
        //Cada algoritmo se ejecutará con una copia del mapa inicial 
        System.out.println("Ronda 1:");
        System.out.println("Se esta llevando a cabo FCFS: ");
        FCFS(new HashMap<>(administradorProcesos));

        System.out.println("\n\nSe esta llevando a cabo RR1: ");
        RR(new HashMap<>(administradorProcesos), 1);

        System.out.println("\n\nSe esta llevando a cabo RR4: ");
        RR(new HashMap<>(administradorProcesos), 4);

        System.out.println("\n\nSe esta llevando a cabo SPN: ");
        SPN(new HashMap<>(administradorProcesos));

        System.out.println("\n\nSe esta llevando a cabo FB: ");
        Map<String, int[]> pruebaFB = new HashMap<>(administradorProcesos);
        pruebaFB.forEach((k, v) -> pruebaFB.get(k)[8] = 0); // Añadiendo el campo "n" en todos los procesos
        FB(pruebaFB, 1, 5);

        // Para cada nueva ronda de simulacion del administrador de procesos, se crean procesoso con valores aleatorios 
        Random random = new Random();
        int contador = 0;
        while (contador < 5) {
            System.out.println("\n\n..................................................");
            System.out.println("Ronda " + (contador + 2) + ":");

            Map<String, int[]> cargaAleatoria = new HashMap<>();
            cargaAleatoria.put("A", new int[]{random.nextInt(11), random.nextInt(10) + 1, 0, 0, 0, 0, 0, 0, 0});
            cargaAleatoria.put("B", new int[]{random.nextInt(11), random.nextInt(10) + 1, 0, 0, 0, 0, 0, 0, 0});
            cargaAleatoria.put("C", new int[]{random.nextInt(11), random.nextInt(10) + 1, 0, 0, 0, 0, 0, 0, 0});
            cargaAleatoria.put("D", new int[]{random.nextInt(11), random.nextInt(10) + 1, 0, 0, 0, 0, 0, 0, 0});
            cargaAleatoria.put("E", new int[]{random.nextInt(11), random.nextInt(10) + 1, 0, 0, 0, 0, 0, 0, 0});

            int max = cargaAleatoria.values().stream().mapToInt(p -> p[0]).max().orElse(0);//Hace el calculo del tiempo de llegada más grande 'max' y el tiempo total 'tiempoTotal'
            int tiempoTotal = tiempoTotal(cargaAleatoria);
            if (max > tiempoTotal) continue;//Si un procesos tiene un tiempo de llegada mayor al total la ronda se descarta y se continua

            contador++;
            cargaAleatoria.forEach((k, v) -> System.out.printf("%s: %d, t = %d; ", k, v[0], v[1]));
            System.out.println();

            Map<String, int[]> cargaAleatoriaFB = new HashMap<>(cargaAleatoria);
            cargaAleatoriaFB.forEach((k, v) -> v[8] = 0); //Se lleva a cabo la misma ejecucion que en la carga inicial, pero con datos nuevos 

            System.out.println("Se esta llevando a cabo FCFS: ");
            FCFS(new HashMap<>(cargaAleatoria));

            System.out.println("\n\nSe esta llevando a cabo RR1: ");
            RR(new HashMap<>(cargaAleatoria), 1);

            System.out.println("\n\nSe esta llevando a cabo RR4: ");
            RR(new HashMap<>(cargaAleatoria), 4);

            System.out.println("\n\nSe esta llevando a cabo SPN: ");
            SPN(new HashMap<>(cargaAleatoria));

            System.out.println("\n\nSe esta llevando a cabo FB: ");
            FB(cargaAleatoriaFB, 1, 5);
        }
    }
    //Implementacion del algoritmo FCFS (First-Come-First-Served)
    public static void FCFS(Map<String, int[]> carga) {
        //Se crea una mapa para almacenar los resultados promedio:
        //T(tiempo de respuesta promedio), E(tiempo de espera promedio), P(proporcion de penalizacion promedio)
        Map<String, Double> resultados = new HashMap<>();
        resultados.put("T", 0.0);
        resultados.put("E", 0.0);
        resultados.put("P", 0.0);


        Queue<String> cola = new LinkedList<>(); //Cola de procesos a ejecutar, impementada como FIFO;
        StringBuilder resultadoGrafico = new StringBuilder();//Para el gráfico de ejecución del algoritmo

        int tTotal = tiempoTotal(carga); //Se obtiene el tiempo total necesario para completar los procesos 
        carga.forEach((key, value) -> { //Se inicia la cola con procesos que tienen tiempo de llegada 0
            if (value[0] == 0) { 
                cola.add(key);
                value[2] = value[1];
            }
        });
        //Simulacion del reloj del sistema
        int clock = 0; //tiempo actual en la simulacion
        while (clock < tTotal) {
            if (!cola.isEmpty()) {
                String proceso = cola.peek();//Se obtiene el proceso al frente de la cola 
                carga.get(proceso)[2]--;//Reduce el tiempo restante de ejecución del proceso actual

                resultadoGrafico.append(proceso);//Agrega el proceso actual al gráfico de ejecución
                if (carga.get(proceso)[2] == 0) {//CUnao el proceso ha concluido su ejecución
                    int[] datos = carga.get(proceso);
                    //Calculos de las métricas del proceso 
                    datos[4] = clock + 1; //Tiempo de finalizacion 
                    datos[5] = datos[4] - datos[0];//Tiempo de respuesta (finalizacion-llegada)
                    datos[6] = datos[5] - datos[1];//Tiempo de espera (respuesta-duracion)
                    datos[7] = (int) ((double) datos[5] / datos[1]);//Proporcion de penalizacion(respuesta/duración)
                    cola.poll();//Se elimina el proceso de la sola 
                }
            } else {
                tTotal++;
            }
            //Revisa si algún proceso llega en el siguiente instante de tiempo y lo agrega a la cola 
            int finalClock = clock;
            carga.forEach((key, value) -> {
                if (value[0] == finalClock + 1) {
                    cola.add(key);
                    value[2] = value[1];//Se inciializa el tiempo restante de ejecucion 
                }
            });

            clock++;//Incremento en el tiempo de simulación 
        }
        //Calculo de los resultados promedios de los procesos
        carga.forEach((key, value) -> {
            resultados.put("T", resultados.get("T") + value[5]);//Suma del tiempo de respuesta 
            resultados.put("E", resultados.get("E") + value[6]);//Suma del tiempo de espera
            resultados.put("P", resultados.get("P") + value[7]);//Suma de la proporcion de penalizacion 
        });
        //Se calcula el promedio de cada métrica dividiendo entre el número de procesos
        int numProcesos = carga.size();
        resultados.forEach((key, value) -> resultados.put(key, value / numProcesos));

        System.out.printf("FCFS: T = %.2f, E = %.2f, P = %.2f\n", resultados.get("T"), resultados.get("E"), resultados.get("P"));
        System.out.println(resultadoGrafico);
    }
    //Implementacion del algoritmo RR (Round Robin) con quantum especifico
    public static void RR(Map<String, int[]> carga, int quantum) {
        //Copia de la carga par aevitar modificaciones de los datos originales 
    Map<String, int[]> copiaCarga = new HashMap<>();
    for (Map.Entry<String, int[]> entry : carga.entrySet()) {
        copiaCarga.put(entry.getKey(), entry.getValue().clone());//Clona cada proceso 
    }

    List<String> cola = new LinkedList<>();//Se hace uso de una lista para manejar los procesos en la cola de ejecucion 
    String resultadoGrafico = "";
    int clock = 0; //tiempo actual 
    int contaClock = 0;//tiempo que un proceso lleva ejecutandose dentro del quantum 

    for (Map.Entry<String, int[]> entry : copiaCarga.entrySet()) {//Inicializacion de la cola con procesos que llegan en el tiempo 0
        if (entry.getValue()[0] == 0) {//si el tiempo de llegada es 0
            cola.add(entry.getKey());//Agrega el proceso a la cola 
            entry.getValue()[2] = entry.getValue()[1];//Inicializa el tiempo restante con la duracion total del proceso 
        }
    }

    int tTotal = tiempoTotal(copiaCarga);//Se calcula el tiempo total necesario para completar los procesos 

    while (clock < tTotal) {//Reloj del sistema 
        if (!cola.isEmpty()) {
            String procesoActual = cola.get(0);
            copiaCarga.get(procesoActual)[2]--;
            resultadoGrafico += procesoActual;
            contaClock++;

            if (copiaCarga.get(procesoActual)[2] == 0) {
                int[] valores = copiaCarga.get(procesoActual);
                //Calculo de las métricas del proceso terminado, como en la implementacion anterior
                valores[4] = clock + 1;
                valores[5] = valores[4] - valores[0];
                valores[6] = valores[5] - valores[1];
                valores[7] = (int) ((double) valores[5] / valores[1]);
                cola.remove(0);//se elimina el proceso de la cola 
                contaClock = 0;//reinicia el contador del quantum 
            } else if (contaClock == quantum) {
                cola.add(cola.remove(0));
                contaClock = 0;
            }
        } else {
            tTotal++;
        }

        for (Map.Entry<String, int[]> entry : carga.entrySet()) {
            if (entry.getValue()[0] == clock + 1) {
                cola.add(entry.getKey());
                entry.getValue()[2] = entry.getValue()[1];
            }
        }

        clock++;
    }
    //Calculo de los resultados promedio de los procesos 
    double tPromedio = 0, ePromedio = 0, pPromedio = 0;
    for (int[] valores : copiaCarga.values()) {
        tPromedio += valores[5];
        ePromedio += valores[6];
        pPromedio += valores[7];
    }
    //calcula el promedio de cada métrica dividiendo entre el numero de procesos
    int totalProcesos = carga.size();
    tPromedio /= totalProcesos;
    ePromedio /= totalProcesos;
    pPromedio /= totalProcesos;

    System.out.printf("RR%d: T = %.2f, E = %.2f, P = %.2f\n", quantum, tPromedio, ePromedio, pPromedio);
    System.out.println(resultadoGrafico);
    }
    //Implementacion del algoritmo SPN (Shorter Process Next)
    public static void SPN(Map<String, int[]> carga) {
    Map<String, int[]> copiaCarga = new HashMap<>();
    for (Map.Entry<String, int[]> entry : carga.entrySet()) {
        copiaCarga.put(entry.getKey(), entry.getValue().clone());
    }

    List<String> cola = new LinkedList<>();
    String resultadoGrafico = "";
    int clock = 0;

    for (Map.Entry<String, int[]> entry : carga.entrySet()) {
        if (entry.getValue()[0] == 0) {
            cola.add(entry.getKey());
            entry.getValue()[2] = entry.getValue()[1];
        }
    }
    //Se ordenan los procesos en la cola según su duracion (menor a mayor)
    cola.sort((a, b) -> Integer.compare(copiaCarga.get(a)[1], copiaCarga.get(b)[1]));

    int tTotal = tiempoTotal(copiaCarga);

    while (clock < tTotal) {//reloj del sistema 
        if (!cola.isEmpty()) {//si hay procesos en la cola 
            String procesoActual = cola.get(0);//se obtiene el procesos con la menor duracion 
            copiaCarga.get(procesoActual)[2]--;//se reduce el tiempo restante del proceso actual 
            resultadoGrafico += procesoActual;//Se agrega el proceso al gráfico de ejecucion 

            if (copiaCarga.get(procesoActual)[2] == 0) {
                int[] valores = copiaCarga.get(procesoActual);
                //Calculos de las métricas del proceso como las implementaciones pasadas 
                valores[4] = clock + 1;
                valores[5] = valores[4] - valores[0];
                valores[6] = valores[5] - valores[1];
                valores[7] = (int) ((double) valores[5] / valores[1]);
                cola.remove(0);
            }
        } else {
            tTotal++;
        }

        for (Map.Entry<String, int[]> entry : carga.entrySet()) {
            if (entry.getValue()[0] == clock + 1) {
                cola.add(entry.getKey());
                entry.getValue()[2] = entry.getValue()[1];
                //Se reordena la cola para priorizar los procesos con menor duración 
                cola.sort((a, b) -> Integer.compare(copiaCarga.get(a)[1], copiaCarga.get(b)[1]));
            }
        }

        clock++;
    }
    //Calculo de los resultados promedios de los procesos 
    double tPromedio = 0, ePromedio = 0, pPromedio = 0;
    for (int[] valores : copiaCarga.values()) {
        tPromedio += valores[5];
        ePromedio += valores[6];
        pPromedio += valores[7];
    }
    //Calculo del promedio de cada métrica 
    int totalProcesos = carga.size();
    tPromedio /= totalProcesos;
    ePromedio /= totalProcesos;
    pPromedio /= totalProcesos;

    System.out.printf("SPN: T = %.2f, E = %.2f, P = %.2f\n", tPromedio, ePromedio, pPromedio);
    System.out.println(resultadoGrafico);
    }
    //  Implementacion del algoritmo FB (Feedback Scheduling)
    public static void FB(Map<String, int[]> carga, int n, int numColas) {
    Map<String, int[]> copiaCarga = new HashMap<>();
    for (Map.Entry<String, int[]> entry : carga.entrySet()) {
        copiaCarga.put(entry.getKey(), entry.getValue().clone());
        copiaCarga.get(entry.getKey())[8] = n; //Se incia el 'cuenta-ticks' para el proceso 
    }
        //Se inicializan las colas de prioridad con ayuda de una lista 
    List<List<String>> colas = new ArrayList<>();
    for (int i = 0; i < numColas; i++) {
        colas.add(new LinkedList<>()); //Cada cola representa un nivel de prioridad 
    }

    String resultadoGrafico = "";
    int clock = 0;
    int tTotal = tiempoTotal(copiaCarga);
    //Se agregan los procesos que ya están disponibles en el instante 0 a la cola de mayor prioridad (cola 0)
    for (Map.Entry<String, int[]> entry : copiaCarga.entrySet()) {
        if (entry.getValue()[0] == 0) {//Si el tiempo de llegada del proceso es 0 
            colas.get(0).add(entry.getKey());//Agrega el proceso a la cola de mayor prioridad 
            entry.getValue()[2] = entry.getValue()[1];//se inicializa el tiempo restante del proceso 
        }
    }

    while (clock < tTotal) {//Bucle while que se ejecuta mientras el reloj no supera el tiempo total estimado 
        for (int i = 0; i < colas.size(); i++) {//Se recorren las colas en orden de prioridad 
            if (!colas.get(i).isEmpty()) {//si la cola actual no esta vacía 
                String procesoActual = colas.get(i).get(0);//se toma el primer proceso de la cola 
                copiaCarga.get(procesoActual)[2]--;//se reduce el tiempo restante del proceso 
                copiaCarga.get(procesoActual)[8]--;//se reduce el 'cuenta-ticks' de la cola actual 
                resultadoGrafico += procesoActual;//Se registra el proceso 
                //Si el proceso termina 
                if (copiaCarga.get(procesoActual)[2] == 0) {
                    int[] valores = copiaCarga.get(procesoActual);
                    valores[4] = clock + 1;//se marca el tiempo de finalizacion 
                    valores[5] = valores[4] - valores[0];//Se calcula el tiempo de respuesta 
                    valores[6] = valores[5] - valores[1];//Se calcula el tiempo de espera 
                    valores[7] = (int) ((double) valores[5] / valores[1]);//se calcula la proporcion de penalizacion 
                    colas.get(i).remove(0);//se elimina el proceso de la cola actual 

                } 
                //Si el proceso agora su 'cuenta-ticks' y debe ser bajado de prioridad 
                else if (copiaCarga.get(procesoActual)[8] == 0) {
                    if (i < colas.size() - 1) { //si no se encuentra en la cola de menor prioridad 
                        copiaCarga.get(procesoActual)[8] = n;//se reinicia el 'cuenta-ticks'
                        colas.get(i + 1).add(colas.get(i).remove(0));//se mueve el proceso a la siguiente cola 
                    } else {//en caso de que ya este en la cola de menor prioridad 
                        colas.get(i).add(colas.get(i).remove(0));//se coloca al final de la cola 
                        copiaCarga.get(procesoActual)[8] = n;//se reinicia el 'cuenta-ticks'
                    }
                }

                break;
            }

            if (i == colas.size() - 1) {//si se llego a la última cola y esta vacia, se incrementa el tiempo total 
                tTotal++;
            }
        }

        for (Map.Entry<String, int[]> entry : carga.entrySet()) {//Se agregan nuevos procesoso que llegan al reloj actual a la cola de mayor prioridad 
            if (entry.getValue()[0] == clock + 1) {//En caso de que el tiempo de llegada coincida con el prócimo tick 
                colas.get(0).add(entry.getKey());//Se agrega el proceso a la cola de mayor prioridad 
                entry.getValue()[2] = entry.getValue()[1];//se inicializa el tiempo restante del proceso 
            }
        }

        clock++;
    }
    //Se calcula el promedio de las métricas del algoritmo 
    double tPromedio = 0, ePromedio = 0, pPromedio = 0;
    //Se reocrren los valores de la carga procesada para acumular los resultados 
    for (int[] valores : copiaCarga.values()) {
        tPromedio += valores[5];//se suman los tiempos de respuesta de todos los procesos
        ePromedio += valores[6];//se suman los tiempos de espera de todos los procesos 
        pPromedio += valores[7];//se suman las proporciones de penalizacion de todos los procesos
    }
    //Se calculan los promedios dividiendo entre el numero total de procesos 
    int totalProcesos = carga.size();
    tPromedio /= totalProcesos;//promedio del tiempo de respuesta 
    ePromedio /= totalProcesos;//promedio del tiempo de espera
    pPromedio /= totalProcesos;//promedio de la proporcion de penalizacion 

    System.out.printf("FB: T = %.2f, E = %.2f, P = %.2f\n", tPromedio, ePromedio, pPromedio);
    System.out.println(resultadoGrafico);
    }

    public static int tiempoTotal(Map<String, int[]> carga) {
    int tiempo = 0;
    for (int[] valores : carga.values()) {
        tiempo += valores[1];
    }
    return tiempo;
    }
}