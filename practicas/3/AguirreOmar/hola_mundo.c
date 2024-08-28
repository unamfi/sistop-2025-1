#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Hola, Mundo!\\n");
    } else {
        printf("Hola, %s!\\n", argv[1]);
    }
    return 0;
}
