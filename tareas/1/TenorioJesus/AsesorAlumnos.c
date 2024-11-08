#include<stdio.h>
#include<unistd.h>
#include<omp.h>

int main(){

    int x,i = 0;

    printf("\nIngrese la cantidad de alumnos que iran con Gunnar: \t");
    scanf("%d",&x);

    int semaforo = 3;
    int semaforo2 = 3;

    #pragma omp parallel num_threads(x)
    {
        #pragma omp single
        printf("\n Hay alumnos con Dudas, Gunnar despierta");

        int atendido = 1;

        while(atendido){

            if(semaforo>0)
            {
                semaforo--;
                #pragma omp flush(semaforo)
                atendido = 0; 
            }
        }

        sleep(2);

        #pragma omp critical
        {
            semaforo2--;
            printf("\nGunnar esta atendiendo la Duda del alumno %d", omp_get_thread_num()+1);
            printf("\nYa casi acaba....");
            printf("\nTermindado El alumno se retira\n\n");
            if(semaforo2==0)
            {
                semaforo2 = 3;
                semaforo = 3;
                #pragma omp flush(semaforo)
                #pragma omp flush(semaforo2)
                printf("---Ronda terminada, Ahora van a pasar otros 3 alumnos----\n ");
            }
        }

        #pragma omp barrier  
        #pragma omp single
        printf("\nAl parecer ya no hay mas alumnos, Gunnar procede a dormir");

    }

    return 0;
}