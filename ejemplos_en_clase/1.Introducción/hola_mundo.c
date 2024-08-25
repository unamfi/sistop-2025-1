#include <stdio.h>
#include <stdlib.h>

/* Este código lo genero sólo para que, a su vez, se genere el código
   correspondiente en ensamblador que también les incluyo, "hola_mundo.s". */
void main() {
  int *num;
  printf("¡Hola mundo!\n\n...Mundo inmundo...\n\n");
  num = malloc(50 * sizeof(int));
  printf("Tengo un arreglo de 50 enteros en la dirección de memoria: %x\n", num);
}
