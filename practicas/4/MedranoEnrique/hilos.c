/*
Programa para practica 4 de Sistemas Operativos
Este programa solo revisa los hilos disponibles de tu equipo
Utilizando la paquetería de OpenMP, ejecutada con WLS desde Windows

Medrano Solano Enrique

*/

//Se incluyen librerías tanto para estadarización como para directiva OpenMP
#include <stdio.h>
#include "omp.h"

//Inicio del programa
int main()
{

    printf("\n############");
    printf("Hilos de procesamiento con OpenMP");
    printf("\n############\n");

    int noProc = omp_get_num_procs();
    printf("\nNumero de procesadores encontrados: %d\n", noProc);

    int noHilos = 10;
    omp_set_num_threads(noHilos);

    printf("\nHilos actuales: %d\n", omp_get_num_threads());

    printf("\nAntes de la directiva parallel\n\n");

    #pragma omp parallel
    {
        int idHilo = omp_get_thread_num();
        printf("Hilo %d de %d hilo(s)\n", idHilo, omp_get_num_threads());
    }

    printf("\nDespues de directiva parallel\n");

    printf("\nHilos actuales: %d\n\n", omp_get_num_threads());
    return 0;
}