#include <stdio.h>

void procesoHijo(int numero) {
    if (numero == 1) {
        printf("Soy el primer proceso hijo\n");
    } else if (numero == 2) {
        printf("Soy el segundo proceso hijo\n");
    } else {
        printf("Soy un proceso hijo adicional\n");
    }
}

void procesoPadre() {
    printf("Soy el proceso padre\n");
    procesoHijo(1); // Llamada al primer hijo
    procesoHijo(2); // Llamada al segundo hijo
}

int main() {
    procesoPadre();
    return 0;
}