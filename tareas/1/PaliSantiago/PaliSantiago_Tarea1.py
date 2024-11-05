from colorama import init, Fore, Style
import threading
import time
import random

# Inicializar colorama
init(autoreset=True)

# Variables compartidas
elf_problems = 0
returned_reindeer = 0
mutex = threading.Lock()
santa_event = threading.Condition(mutex)
elf_semaphore = threading.Semaphore(0)

# Número de elfos y renos
NUM_ELVES = 15
NUM_REINDEER = 6

# Variable para terminar el programa
done = False

def log_msg(message, sender="", problem=False):
    """Función para registrar mensajes con colores, separadores y formatear"""
    if not done:
        current_time = time.strftime("%H:%M:%S", time.localtime())
        
        if sender == "elf":
            # Si el elfo tiene problemas, usar color rojo, de lo contrario azul
            color = Fore.RED if problem else Fore.BLUE
            print(f"\n{color}{'='*40}\n[Elfo {current_time}] {message}\n{'='*40}{Style.RESET_ALL}")
        
        elif sender == "reindeer":
            # Diálogos de los renos con separadores y color verde
            print(f"\n{Fore.GREEN}{'*'*40}\n[Reno {current_time}] {message}\n{'*'*40}{Style.RESET_ALL}")
        
        elif sender == "santa":
            # Diálogos de Santa con separadores y color amarillo
            print(f"\n{Fore.YELLOW}{'+'*40}\n[Santa {current_time}] {message}\n{'+'*40}{Style.RESET_ALL}")

# Frases aleatorias para los elfos
work_phrases = [
    "Elfo {id}: A chambear!!.",
    "Elfo {id}: ¡Vamos, equipo, cada regalo cuenta!",
    "Elfo {id}: ¿No podemos acelerar el ritmo?!!",
    "Elfo {id}: ¡Los niños están contando con nosotros, no hay tiempo que perder!",
    "Elfo {id}: ¡Qué emoción! No puedo esperar a ver las sonrisas en Navidad.",
    "Elfo {id}: Cada juguete terminado es un paso más hacia una feliz Navidad."
]

problem_phrases = [
    "Elfo {id}: ¡Ay no! El robot de envolver regalos se descompuso otra vez.... {count} {plural} tienen problemas.",
    "Elfo {id}: ¡Auxilio, se me rompió una herramienta! Hay {count} {plural} con problemas.",
    "Elfo {id}: ¡Socorro! Se nos quemaron las galletas que teníamos para el receso, {count} {plural} estamos en problemas."
]

solved_phrases = [
    "Elfo {id}: Gracias Santa, problema resuelto. ¡De vuelta al trabajo!",
    "Elfo {id}: ¡Eres un verdadero salvador, Santa!, volvamos a la acción.",
    "Elfo {id}: ¡Problema resuelto, seguimos trabajando!"
]

# Función de Santa Claus
def santa():
    global elf_problems, returned_reindeer, done
    while True:
        with santa_event:
            santa_event.wait_for(lambda: elf_problems >= 3 or returned_reindeer == NUM_REINDEER)
            
            if returned_reindeer == NUM_REINDEER:
                log_msg("La operación regalo ha comenzadooo ¡Ho, ho, ho!.", "santa")
                done = True
                returned_reindeer = 0
                santa_event.notify_all()
                for _ in range(elf_problems):
                    elf_semaphore.release()
                break
            
            elif elf_problems >= 3:
                log_msg("¿Elfos en problemas?, Recuerden, la Navidad se trata de trabajar en equipo.", "santa")
                for _ in range(3):
                    elf_semaphore.release()
                elf_problems = 0

# Función de los elfos
def elf(elf_id):
    global elf_problems, done
    while True:
        if done:
            break

        log_msg(random.choice(work_phrases).format(id=elf_id), "elf")
        time.sleep(random.uniform(1, 5))

        if done:
            break

        if random.random() < 0.3:
            with mutex:
                if done:
                    break
                elf_problems += 1
                plural = "elfo" if elf_problems == 1 else "elfos"
                # Cambiar el color a rojo cuando el elfo tiene problemas
                log_msg(random.choice(problem_phrases).format(id=elf_id, count=elf_problems, plural=plural), "elf", problem=True)
                if elf_problems == 3:
                    santa_event.notify_all()
            elf_semaphore.acquire()
            log_msg(random.choice(solved_phrases).format(id=elf_id), "elf")
        else:
            log_msg(f"Elfo {elf_id}: La magia de los juguetes me llama. ¡A seguir trabajando!", "elf")

        if done:
            break

# Función de los renos
def reindeer():
    global returned_reindeer, done
    while True:
        time.sleep(random.uniform(5, 10))
        if done:
            break
        
        with mutex:
            returned_reindeer += 1
            if returned_reindeer == 1:
                log_msg(f". ¡Santa! ¡Tenemos un nuevo reno en la fábrica! ", "reindeer")
            elif returned_reindeer < NUM_REINDEER:
                log_msg(f"¡Santa! ¡Tenemos un nuevo reno en la fábrica!, {returned_reindeer} renos están de vuelta.", "reindeer")
            else:
                log_msg(f"Rodolfo ya llegó!!. Todos los {returned_reindeer} renos están de vuelta y es hora de partir.", "reindeer")
                santa_event.notify_all()

# Crear e iniciar los hilos de Santa, elfos y renos
thread_santa = threading.Thread(target=santa)
threads_elves = [threading.Thread(target=elf, args=(i,)) for i in range(NUM_ELVES)]
threads_reindeer = [threading.Thread(target=reindeer) for _ in range(NUM_REINDEER)]

# Iniciar hilos
thread_santa.start()
for thread in threads_elves:
    thread.start()
for thread in threads_reindeer:
    thread.start()

# Santa termina
thread_santa.join()
for thread in threads_elves:
    thread.join()
for thread in threads_reindeer:
    thread.join()
