import threading
import random
import time
from colorama import init, Fore, Style

"""
Este programa simula un cruce de río entre dos grupos: hackers y serfs.
La balsa tiene capacidad para 4 personas, y las personas de ambos grupos deben
colaborar para cruzar el río sin conflictos. Si se suben más de 2 personas de un grupo
y al menos una persona del otro grupo, se genera un conflicto y no se puede zarpar.
En caso de conflicto, se simula un proceso de negociación para decidir una nueva
combinación de personas para cruzar. El programa utiliza concurrencia para simular
la llegada aleatoria de hackers y serfs, y emplea semáforos y mutex para la sincronización.
"""

# Inicializa colorama para colores en la consola
init(autoreset=True)

# Clase base Persona
class Persona(threading.Thread):
    def __init__(self, balsa):
        super().__init__()
        self.balsa = balsa

    def run(self):
        while True:
            self.balsa.subir(self)

    def representar(self):
        """Método que será implementado por las clases hijas para mostrar el tipo de persona."""
        raise NotImplementedError("Este método debe ser implementado en las subclases.")

# Clase Hacker que hereda de Persona
class Hacker(Persona):
    def __init__(self, balsa):
        super().__init__(balsa)
        self.tipo = 'hacker'

    def representar(self):
        """Devuelve el emoji y representación visual de un hacker."""
        return '💻'

# Clase Serf que hereda de Persona
class Serf(Persona):
    def __init__(self, balsa):
        super().__init__(balsa)
        self.tipo = 'serf'

    def representar(self):
        """Devuelve el emoji y representación visual de un serf."""
        return '💼'

# Clase Balsa que maneja la lógica de sincronización y zarpe
class Balsa:
    def __init__(self):
        # Mutex y semáforo para sincronización
        self.mutex = threading.Lock()
        self.semaforo = threading.Semaphore(4)
        self.hackers = 0
        self.serfs = 0
        self.balsa_list = []

    def subir(self, persona):
        self.semaforo.acquire()  # Limita a 4 personas en la balsa
        
        with self.mutex:
            self.balsa_list.append(persona)
            self.mostrar_estado(persona)

            # Actualiza los contadores según el tipo de persona usando polimorfismo
            if isinstance(persona, Hacker):
                self.hackers += 1
            elif isinstance(persona, Serf):
                self.serfs += 1
            
            time.sleep(0.7)  # Espera antes de permitir que suba la siguiente persona
            
            # Verifica si la balsa está lista para zarpar
            if len(self.balsa_list) == 4:
                self.zarpar()
        
        self.semaforo.release()

    def mostrar_estado(self, persona):
        """Muestra el estado actual de quién se subió a la balsa."""
        balsa_visual = [p.representar() for p in self.balsa_list]
        print(f"\n{Fore.CYAN}🔹 Un {persona.tipo.capitalize()} {persona.representar()} se sube a la balsa: [{' '.join(balsa_visual)}]")

    def zarpar(self):
        print(f"\n{Fore.GREEN}🚣  La balsa está lista para zarpar...🚣")

        # Verifica si hay conflicto entre hackers y serfs
        if (self.hackers > 2 and self.serfs > 0) or (self.serfs > 2 and self.hackers > 0):
            print(f"{Fore.RED}⚠️  No se pudo zarpar porque se están peleando. ⚠️")
            self.simular_acuerdo()  # Inicia proceso de acuerdo en caso de conflicto
            return

        # Si no hay conflicto, la balsa zarpa y todos desembarcan
        print(f"{Fore.GREEN}La balsa zarpa con {self.hackers} hackers y {self.serfs} serfs.")
        time.sleep(1)  # Simula el cruce del río
        print(f"{Fore.GREEN}La balsa ha llegado al otro lado. Todos desembarcan. ✅\n")
        print(" ═════════════════════════════════════════")
        
        # Reinicia los contadores
        self.balsa_list.clear()
        self.hackers = 0
        self.serfs = 0

    def simular_acuerdo(self):
        print(f"\n{Fore.YELLOW}🤝 Los bandos están haciendo acuerdos 🤝 ")
        time.sleep(1.5)  # Simula el tiempo de discusión

        # Elige aleatoriamente la combinación para zarpar en caso de conflicto
        decision = random.choice(["4 hackers", "2 hackers y 2 serfs", "4 serfs"])
        if decision == "4 hackers":
            self.hackers = 4
            self.serfs = 0
            print(f"{Fore.GREEN}🎉 ¡Acuerdo! Zarparán 4 hackers. 🎉")
        elif decision == "2 hackers y 2 serfs":
            self.hackers = 2
            self.serfs = 2
            print(f"{Fore.GREEN}🎉 ¡Acuerdo! Zarparán 2 hackers y 2 serfs. 🎉")
        else:
            self.hackers = 0
            self.serfs = 4
            print(f"{Fore.GREEN}🎉 ¡Acuerdo! Zarparán 4 serfs. 🎉")

        # Simula el zarpe con la combinación acordada
        print(f"\n{Fore.GREEN}🚣 La balsa zarpa con {self.hackers} hackers y {self.serfs} serfs. 🚣  ")
        time.sleep(1)  # Simula el cruce
        print(f"{Fore.GREEN}La balsa ha llegado al otro lado. Todos desembarcan. ✅\n")
        print(" ═════════════════════════════════════════")

        # Reinicia los contadores después del cruce
        self.balsa_list.clear()
        self.hackers = 0
        self.serfs = 0

# Función para crear personas de forma aleatoria
def crear_personas(total_hackers, total_serfs, balsa):
    total_personas = total_hackers + total_serfs

    while total_personas > 0:
        # Selecciona aleatoriamente el tipo de persona
        tipo_persona = 'hacker' if random.random() < (total_hackers / total_personas) else 'serf'
        persona = Hacker(balsa) if tipo_persona == 'hacker' else Serf(balsa)
        persona.start()
        
        # Variabilidad en el tiempo de llegada entre hackers y serfs
        if tipo_persona == 'hacker':
            time.sleep(random.uniform(0.5, 1.5))  # Hackers llegan entre 0.5 y 1.5 segundos
            total_hackers -= 1
        else:
            time.sleep(random.uniform(0.2, 1.0))  # Serfs llegan entre 0.2 y 1.0 segundos
            total_serfs -= 1
        
        total_personas = total_hackers + total_serfs

# Función principal
def main():
    balsa = Balsa()
    
    total_hackers = 15
    total_serfs = 15
    
    crear_personas(total_hackers, total_serfs, balsa)

    # Mantiene el programa en ejecución, en caso de presionar CTRL + C se detendrá el programa
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}🚀 Terminando el cruce del río... 🚀")

if __name__ == "__main__":
    print(f"{Fore.GREEN}🚀 Bienvenido al cruce del río para desarrolladores. 🚀")
    main()





