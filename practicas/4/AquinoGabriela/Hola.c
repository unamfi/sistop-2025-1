#include <stdio.h>

int main()
{
	int n1, n2, producto, suma;
	
    printf("Holaaa, soy Aquino Gabriela\n");
    printf("Bienvenido a mi practica 4 de Sistemas Operativos :)");
    
    printf("\n Introduzca un primer numero: ");
    scanf("%d",&n1);
    printf("\n Introduzca un segundo numero: ");
    scanf("%d",&n2);
    
    suma= n1+n2;
    producto= n1*n2;
    
    printf( "\n   La suma es: %d", suma );
    printf( "\n\n   La multiplicaci%cn es: %d", 162, producto );

    getch(); /* Pausa */

    return 0;
}