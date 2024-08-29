#include <stdio.h>

int main()
{
    char nombre[50];  

    printf("Hola mundo :)");    
    printf("¿Cuál es tu nombre? ");
    scanf("%49s", nombre);  
    printf("Hola %s, ¡bienvenido a mi repositorio! :)\n", nombre);  

    return 0;
}
