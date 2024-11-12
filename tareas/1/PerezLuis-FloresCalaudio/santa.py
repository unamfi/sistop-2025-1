import threading
import random
import time
from typing import List

class SantaWorkshop:
    def __init__(self):
        # Semáforos para sincronización básica
        self.santa_sleep = threading.Semaphore(0)
        
        # Semáforos para la coordinación de elfos
        self.elfos_mutex = threading.Lock()
        self.ayuda_elfos = threading.Semaphore(0)
        self.elfos_ayudados = threading.Semaphore(0)
        
        # Semáforos para la coordinación de renos
        self.renos_mutex = threading.Lock()
        self.renos_listos = threading.Semaphore(0)
        self.renos_pueden_irse = threading.Semaphore(0)
        
        # Contadores y estados
        self.elfos_esperando: List[threading.Thread] = []
        self.renos_regresados = 0
        self.entrega_regalos = False

    def elfo_trabajo(self, id: int) -> None:
        """Simula el trabajo de un elfo y el proceso de solicitar ayuda."""
        while not self.entrega_regalos:
            # Trabajo normal del elfo
            time.sleep(random.randint(1, 3))
            
            with self.elfos_mutex:
                if len(self.elfos_esperando) < 3:
                    print(f"🧝 Elfo {id} necesita ayuda")
                    self.elfos_esperando.append(threading.current_thread())
                    
                    if len(self.elfos_esperando) == 3:
                        print("👥 Grupo de 3 elfos formado, despertando a Santa")
                        self.santa_sleep.release()
                    
                    # Esperar fuera del mutex para no bloquear a otros elfos
                    self.elfos_mutex.release()
                    self.ayuda_elfos.acquire()  # Esperar ayuda de Santa
                    self.elfos_ayudados.release()  # Señalar que fue ayudado
                    self.elfos_mutex.acquire()
                    
                    if threading.current_thread() in self.elfos_esperando:
                        self.elfos_esperando.remove(threading.current_thread())
                else:
                    print(f"🧝 Elfo {id} continúa trabajando solo")

    def reno_vuelta(self, id: int) -> None:
        """Simula el regreso de un reno de vacaciones."""
        while not self.entrega_regalos:
            time.sleep(random.randint(10, 20))  # Vacaciones
            
            with self.renos_mutex:
                self.renos_regresados += 1
                print(f"🦌 Reno {id} ha regresado ({self.renos_regresados}/9)")
                
                if self.renos_regresados == 9:
                    print("🦌 Todos los renos han regresado")
                    self.santa_sleep.release()
            
            # Esperar a que Santa prepare el trineo
            self.renos_listos.acquire()
            # Esperar a completar la entrega
            self.renos_pueden_irse.acquire()
            
            with self.renos_mutex:
                self.renos_regresados -= 1

    def santa_claus(self) -> None:
        """Simula las actividades de Santa Claus."""
        while not self.entrega_regalos:
            print("😴 Santa está dormido...")
            self.santa_sleep.acquire()  # Esperar a ser despertado
            
            # Verificar renos primero (prioridad)
            with self.renos_mutex:
                if self.renos_regresados == 9:
                    print("🎅 Santa prepara el trineo")
                    time.sleep(2)
                    
                    # Despertar a todos los renos
                    for _ in range(9):
                        self.renos_listos.release()
                    
                    self.entrega_regalos = True
                    print("🛷 Entregando regalos...")
                    time.sleep(5)  # Tiempo de entrega
                    
                    # Liberar a los renos
                    for _ in range(9):
                        self.renos_pueden_irse.release()
                    
                    print("🎁 Entrega completada")
                    self.entrega_regalos = False
                    continue
            
            # Atender elfos si no hay renos
            with self.elfos_mutex:
                if len(self.elfos_esperando) >= 3:
                    print("🎅 Santa ayudando a los elfos")
                    # Ayudar a los 3 elfos
                    for _ in range(3):
                        self.ayuda_elfos.release()
                    
                    # Esperar a que todos sean ayudados
                    for _ in range(3):
                        self.elfos_ayudados.acquire()
                    
                    print("✨ Santa terminó de ayudar a los elfos")

def main():
    """Función principal que inicializa y ejecuta la simulación."""
    workshop = SantaWorkshop()
    
    # Crear y empezar hilos
    santa_thread = threading.Thread(target=workshop.santa_claus)
    elfo_threads = [
        threading.Thread(target=workshop.elfo_trabajo, args=(i,))
        for i in range(10)
    ]
    reno_threads = [
        threading.Thread(target=workshop.reno_vuelta, args=(i,))
        for i in range(9)
    ]
    
    # Iniciar todos los hilos
    santa_thread.start()
    for t in elfo_threads + reno_threads:
        t.start()
    
    # Esperar a que terminen
    santa_thread.join()
    for t in elfo_threads + reno_threads:
        t.join()

if __name__ == "__main__":
    main()
