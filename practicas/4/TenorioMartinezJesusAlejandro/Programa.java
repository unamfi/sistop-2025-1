class MiHilo extends Thread{

	private String nombreHilo;

	public MiHilo(String nombre){
		this.nombreHilo = nombre;
	}

	@Override
	public void run(){
		for (int i =0;i<5;i++){
			System.out.println(nombreHilo+"ejecutando: "+i);
			try{
				Thread.sleep(500);
			} catch  (InterruptedException e){
				System.out.println(nombreHilo + "Interrumpido.");
			}
		}
		System.out.println(nombreHilo + "finalizado.");
	}
}

public class Programa{
	public static void main(String[] args){

		MiHilo hilo1 = new MiHilo("Hilo1");
		MiHilo hilo2 = new MiHilo("Hilo2");

		hilo1.start();
		hilo2.start();

		try{
			hilo1.join();
			hilo2.join();
		}catch (InterruptedException e){
			System.out.println("Hilos interrumpidos");
		}
		System.out.println("Hilos y programa Finalizados");
	}
}
