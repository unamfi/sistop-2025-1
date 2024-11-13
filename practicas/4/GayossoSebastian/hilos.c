#include <stdio.h>

void tarea1() {
    for (int i = 0; i < 5; i++) {
        printf("Ejecutando tarea 1, iteración %d\n", i);
    }
}

void tarea2() {
    for (int i = 0; i < 5; i++) {
        printf("Ejecutando tarea 2, iteración %d\n", i);
    }
}

int main() {
    printf("Iniciando la tarea 1\n");
    tarea1();

    printf("Iniciando la tarea 2\n");
    tarea2();

    printf("Todas las tareas han terminado.\n");
    return 0;
}
