#include <stdio.h>
#include <stdlib.h>
#include <time.h>


int main() {
    int numero, adivinanza, intentos = 0;

    srand(time(0)); //Se inicializa el generador de numeros
    
    numero = rand() % 21; //Se genera un numero aleatorio entre 0-20

    printf("Trata de adivinar el número aleatorio que se generó entre 0 y 20.\n");

    do {
        printf("Adivina el número: ");
        scanf("%d", &adivinanza);
        intentos++;

        if(adivinanza < numero) {
            printf("El número es mayor.\n");
        } else if(adivinanza > numero) {
            printf("El número es menor.\n");
        } else {
            printf("¡Felicidades! Adivinaste el número en %d intentos.\n", intentos);
        }
    } while(adivinanza != numero);

    return 0;
}


