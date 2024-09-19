import java.util.Scanner; 
public class Calculadora {
	public static void main(String[] args){
		System.out.println("Este programa realiza operaciones basicas con dos numeros dados por el usuario ");
		Scanner scanner = new Scanner(System.in);

		System.out.print("Introduce el primer numero de la operacion: ");
		double num1 = scanner.nextDouble();

		System.out.print("Introduce el segundo numero de la operacion: ");
		double num2 = scanner.nextDouble();


		System.out.print("Elige la operación a realizar: +, -, *, / : ");
		char operacion = scanner.next().charAt(0);

		double resultado = 0; 

		switch (operacion){

			case '+':
				resultado = num1 + num2;
				break; 
			case '-':
				resultado = num1 - num2;
				break; 
			case '*':
				resultado = num1 + num2;
				break; 
			case '/':
				if(num2 != 0){
					resultado = num1/num2;
				} else{
					System.out.println ("No es posible dividir entre 0");
					return; 
				}
				break;
			default:
				System.out.println("Operación no válida");
				return;
		}

		System.out.println("El resultado es : " + resultado);
		scanner.close();


	}
}