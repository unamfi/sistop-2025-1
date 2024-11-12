#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void* tarea(void* arg) {
    char* nombre_hilo = (char*)arg;
    int i = 0;
    for (i = 0; i < 5; i++) {
        printf("Hilo %s: %d\n", nombre_hilo, i);
        sleep(1); // Simula una tarea que toma tiempo
    }
    pthread_exit(NULL);
}

int main() {
    pthread_t hilo1, hilo2;
    
    if (pthread_create(&hilo1, NULL, tarea, "Hilo 1")) {
        fprintf(stderr, "Error creando hilo 1\n");
        return 1;
    }

    if (pthread_create(&hilo2, NULL, tarea, "Hilo 2")) {
        fprintf(stderr, "Error creando hilo 2\n");
        return 1;
    }

    pthread_join(hilo1, NULL);
    pthread_join(hilo2, NULL);

    printf("Ambos hilos han terminado.\n");
    return 0;
}
