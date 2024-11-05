#include <stdio.h>
#include <dirent.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
  struct dirent *archivo;
  DIR *dir;
  struct stat metadata;

  dir = opendir(".");
  if (! dir) {
    perror("Error abriendo el directorio actual. ¿Será que no tenemos permisos?");
    return 1;
  }

  /*
   * readdir() va entregando un dirent (entrada de directorio) cada vez que
   * es llamado. Un dirent incluye el nombre del archivo en cuestión, llamando
   * a su atributo d_name.
   */
  while ((archivo = readdir(dir)) != 0) {
    /*
     * La llamada lstat() recibe un apuntador a "metadata", la estructura donde
     * guardará los resultados. Para consultar la información que lleva, revisa
     * "man 2 stat".
     */
    if (lstat(archivo->d_name, &metadata) == -1) {
      perror("lstat");
      return 1;
    }
    /* Para nuestro ejemplo, mostramos: número de i-nodo, nombre de archivo y
     * tamaño del archivo.
     *
     * ¡Ojo! Observa que los directorios también tienen tamaño. ¿Qué indicará?
     */
    printf("%d→ %s (%d)\n", metadata.st_ino, archivo->d_name, metadata.st_size);
  }
  printf("\n");
  closedir(dir);
}
