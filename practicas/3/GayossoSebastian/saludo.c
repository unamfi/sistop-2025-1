#include <stdio.h>

int main() {
    char nombre[50];

    printf("Hello, World!\n");
    printf("Introduce tu nombre: ");
    fgets(nombre, sizeof(nombre), stdin);

    printf("Hola mundo y hola, %s", nombre);

    return 0;
}