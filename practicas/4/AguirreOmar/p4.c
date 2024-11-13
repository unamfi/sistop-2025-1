#include <stdio.h>
#include <pthread.h>

void* hello(void* arg) {
    printf("Mensaje del hilo!\n");
    return NULL;
}

int main() {
    pthread_t thread;
    pthread_create(&thread, NULL, hello, NULL);
    pthread_join(thread, NULL);
    return 0;
}
