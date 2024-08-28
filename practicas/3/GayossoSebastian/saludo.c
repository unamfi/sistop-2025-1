#include <stdio.h>
int main() {
    char nombre[100];
    printf("Hola usuario, dime tu nombre\n");
    scanf("%s" ,&nombre);
    
    printf("Hola, %s y hola mundo!\n", &nombre);
    return 0;
}
