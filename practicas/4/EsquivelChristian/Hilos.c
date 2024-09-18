#include <stdio.h>
#include <pthread.h>

void *saludo_hilo(){
printf("Hola mundo desde un hilo\n");
}

int main(){
    pthread_t hilo;
    int resultado;

    resultado = pthread_create(&hilo,NULL,saludo_hilo,NULL);

    if(resultado != 0){
        perror("Error al crear el hilo");
        return 1;
    }

    pthread_join(hilo,NULL);
    return 0;
}


