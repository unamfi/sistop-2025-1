from montaje import montaje
from mostrararchivos import mostrarArchivos
import threading
import time

"""""
ESTE ES UN EJEMPLO DE SINCRONIZACION, SE GENERAN VARIOS HILOS QUE VAN A ESTAR
SOLICICITANDO EL RECURSO DE FIUNAMFS, EL CUAL SE MANEJA COMO UN RECURSO CRITICO
AL QUE SOLO UN HILO A LA VEZ PUEDE ACCEDER 
"""""

# Semaforo para sincronizar el acceso al recurso compartido
semaforo = threading.Semaphore(1)

# Funcion que simula un usuario ejecutando el comando `ls`
def usuario_ls():
    while True:
        print("\nUsuario solicitando 'ls': Esperando el recurso...")
        with semaforo: #Adquirimos el semaforo
            with open('fiunamfs.img', 'r+b') as disco:
                NameFiles = mostrarArchivos(disco)
            time.sleep(5)  # Simula el tiempo de uso del recurso
        time.sleep(3)  # Pausa antes de que el usuario intente nuevamente

# Función principal
def main():
    print("\nMontando FiUnamFs")
    montaje("fiunamfs.img")

    # Creamos y arrancamos multiples hilos que simulan diferentes usuarios
    hilos = []
    for i in range(5):  # Simularemos 5 usuarios ejecutando `ls` de forma paralela
        hilo = threading.Thread(target=usuario_ls)
        hilos.append(hilo)
        hilo.start()

    # Espera a que los hilos terminen
    for hilo in hilos:
        hilo.join()

if __name__ == "__main__":
    main()
