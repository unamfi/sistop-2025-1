import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.Semaphore; 
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicInteger;

public class SantaClausP{
	private static final int NUM_ELFOS = 12; //Número establecido por el equipo para tener un mejor control sobre el funcionamiento de los elfos en el programa 
	private static final int NUM_RENOS = 9; 
	private static final int GRUPO_ELFOS = 3; //Variable establecida para establecer el numero de elfos que pueden pedir ayuda a Santa Claus 

	//Se hace uso de semaforos para poder controlar los diferentes eventos que se presentan en el problema 

	private Semaphore santaSemaforo = new Semaphore(0);// Utilizado para despertar a Santa según corresponda 
	private Semaphore grupoElfosSemaforo = new Semaphore(0);//Para controlar mejor el grupo de 3 elfos que puede pedir ayuda 
	private Semaphore elfoMutex = new Semaphore(1);//Para el contador de elfos 
	private Semaphore renoMutex= new Semaphore(1);//Para el contador de renos 

	private AtomicInteger elfosEsperando = new AtomicInteger(0); //Para llevar la cuenta de los elfos que estan esperando ayuda 
	private AtomicInteger renosRegresados = new AtomicInteger(0); //Parar llevar la cuenta de los renos que han regresado 
	private Set<Integer> elfosAyudados = new HashSet<>(); //El equipo decidio que los elfos no se repitieran al pedir ayuda, por lo que el uso de este HashSet es para evitar repeticiones 
	private boolean santaFinal = false;
	private boolean mensajeFinal= false; 

	public static void main(String[] args){
		SantaClausP santa = new SantaClausP();
		santa.start();
	}
	//Se crean los hilos para manejar el funcionamiento de los elfos y los renos 
	public void start (){
		for(int i=0; i < NUM_ELFOS; i++){
			new Thread(new Elfos(i, this)).start();
		}
		for(int i=0; i < NUM_RENOS; i++){
			new Thread(new Renos(i, this)).start();
		}
		//Se crea el hilo para el funcionamiento de Santa Claus 
		new Thread(() -> {
			try{ 
				while(true){
					santaSemaforo.acquire();//Para que santa espere a ser despertado una vez que alguna de las condiciones se cumpla

					elfoMutex.acquire();//Mutex para protección de la sección critica
					//Verificación de las condiciones para el final del programa: Si todos los renos han regresado y si no hay más elfos que necesiten ayuda
					if (renosRegresados.get() == NUM_RENOS && elfosEsperando.get() == 0 && !mensajeFinal){
						System.out.println("\u001B[31mSanta : Todos los renos han regresado y ningún elfo necesita ayuda, ¡es hora de repartir los regalos!\u001B[0m");
						mensajeFinal = true ; //Se muestra el mensaje final una vez 
						santaFinal = true ; //Santa despierta definitivamente e inicia su recorrido 
						elfoMutex.release();
						break;
					}

					elfoMutex.release();
					ayudarElfos();//Se ayuda a los elfos cuando hay tres de ellos esperando 
				}
			} catch(InterruptedException e){
				Thread.currentThread().interrupt();
			}
		}).start();

	}

	public void elfosNecesitanAyuda(int elfoId) throws InterruptedException {
		elfoMutex.acquire();
		if(santaFinal){//Se verifica si Santa ya ha iniciado su recorrido 
			elfoMutex.release();
			return;//No debe permitirse que los elfos pidan más ayuda una vez que Santa ha partido 
		}

		if (!elfosAyudados.contains(elfoId)){//Se verifica si el elfo ya ha sido ayudado antes
			if(elfosEsperando.get() < GRUPO_ELFOS){
				elfosEsperando.incrementAndGet();
				elfosAyudados.add(elfoId); //Se "marca" que el elfo ya ha sido ayudado 
				System.out.println("\u001B[34mElfo " + elfoId + " necesita ayuda. ( " + elfosEsperando.get() + " elfos esperando)\u001B[0m");

				if(elfosEsperando.get() == GRUPO_ELFOS){
					System.out.println("\u001B[34mTres elfos necesitan ayuda, despertando a Santa. \u001B[0m");
					santaSemaforo.release(); //Despertando a Santa
				}
			}
		}
		elfoMutex.release();
		grupoElfosSemaforo.acquire();//El elfo espera a que Santa Claus despierte y lo ayude 
	}
	public void renosRegreso(int renoId) throws InterruptedException {
		renoMutex.acquire();//Para proteger el contador de los renos 
		renosRegresados.incrementAndGet();
		System.out.println("\u001B[33mReno " + renoId + " ha regresado del Caribe. ( " + renosRegresados.get() + " renos en el Polo Norte)\u001B[0m");

		if (renosRegresados.get() == NUM_RENOS){
			System.out.println("\u001B[31mTodos los renos han regresado, despertando a Santa para su recorrido final.\u001B[0m");
			santaSemaforo.release();//Se despierta a Santa para dar inicio a su recorrido 

		}
		renoMutex.release();
	}
	private void ayudarElfos() throws InterruptedException {
		System.out.println("\u001B[31mSanta está ayudando a los elfos...\u001B[0m");
		Thread.sleep(1000);//Simular ayuda 
		elfoMutex.acquire();
		elfosEsperando.set(0);
		elfoMutex.release();

		for (int i=0; i < GRUPO_ELFOS; i++){//Los tres elfos ayudados deben continuar 
			grupoElfosSemaforo.release();
		}

		System.out.println("\u001B[31mSanta ha ayudado a los elfos y vuelve a dormir.\u001B[0m");

	}
	//Clases correspondientes para la solucion del problema 
	//Clase para ELFOS 
	static class Elfos implements Runnable {
		private int id; 
		private SantaClausP santa;

		Elfos(int id, SantaClausP santa){
			this.id = id; 
			this.santa = santa; 
		}
		@Override
		public void run(){
			try{
				while(true){
					Thread.sleep(ThreadLocalRandom.current().nextInt(2000, 5000));//Para simular el trabajo de los elfos 
					santa.elfosNecesitanAyuda(id); 
					if(santa.santaFinal){
						break; //Se termina el ciclo cuando Santa inicia su recorrido segun las condiciones 

					}
				}
			}catch (InterruptedException e){
				Thread.currentThread().interrupt();

			}
		}
	}
	//Clase para RENOS 
	static class Renos implements Runnable {
		private int id; 
		private SantaClausP santa; 

		Renos(int id, SantaClausP santa){
			this.id = id; 
			this.santa = santa; 
		}
		@Override
		public void run(){
			try{
				Thread.sleep(ThreadLocalRandom.current().nextInt(5000, 10000));//Para simular las vacaciones de los renos 
				santa.renosRegreso(id);//Los renos regresan al Polo Norte 
			}catch (InterruptedException e ){
				Thread.currentThread().interrupt();
			}
		}
	}
}