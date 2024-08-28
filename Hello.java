import java.util.Scanner;

public class Hello {
	public static void main(String args[]) {
		Scanner scan = new Scanner(System.in);
		System.out.print("Teclea tu nombre: ");
		String nombre = scan.next();
		System.out.println("Hola " + nombre + " bienvenido a Sistop25-1");
	}
}