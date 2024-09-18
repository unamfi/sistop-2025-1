#include <stdio.h>
#include <pthread.h>

// Función que ejecutará el hilo
void* print_message(void* arg) {
    char* message = (char*)arg;
    printf("%s\n", message);
    return NULL;
}

int main() {
    pthread_t thread1, thread2;

    pthread_create(&thread1, NULL, print_message, "Hola desde el hilo 1");
    pthread_create(&thread2, NULL, print_message, "Hola desde el hilo 2");

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("Hilos completados.\n");

    return 0;
}
