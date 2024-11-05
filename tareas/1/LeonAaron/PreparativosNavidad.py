#LeonPerez AaronRodrigo

import threading
import time
import random

# Variables compartidas
elfos_problema = 0  # Cuenta de elfos con problemas
renos_de_vuelta = 0  # Cuenta de renos que han regresado
mutex = threading.Lock()  # Mutex para proteger variables compartidas
santa_cond = threading.Condition(mutex)  # Condición para despertar a Santa
elfos_sem = threading.Semaphore(0)  # Semáforo para coordinar a los elfos

# Número total de elfos y renos
NUM_ELFOS = 10
NUM_RENOS = 9

# Nombres de los elfos y renos
elf_names = ["Tontín", "Dormilón", "Saltarín", "Travieso", "Bromista", "Brillante", "Chispita", "Rápido", "Goloso", "Alegre"]
reindeer_names = ["Rudolph", "Dasher", "Dancer", "Prancer", "Vixen", "Comet", "Cupid", "Donner", "Blitzen"]

# Dibujo de Santa Claus
santa_ascii = """
   ________
  /        \\
 |  ~    ~  |   zZZ
 |   \\__/   |  
 |__________|
||      ||
||      ||
"""

# Dibujo de Santa Claus sorprendido
santa_surprised_ascii = """
   ________
  /        \\
 |  O   O   |  !!
 |  \\____/  |  
 |__________|
   
   //   \\\\
"""

# Dibujo festivo de Santa Claus
santa_festive_ascii = """


 _   _         _   _         _   _       _ 
| | | | ___   | | | | ___   | | | | ___ | |
| |_| |/ _ \  | |_| |/ _ \  | |_| |/ _ \| |
|  _  | (_) | |  _  | (_) | |  _  | (_) |_|
|_| |_|\___/  |_| |_|\___/  |_| |_|\___/(_)

   ________
  /           \\
 | ^      ^   |  
 |   \\____/   |    --Feliz Navidad!!!
  ___________
    _________________
     |'-========OoO===='-.              
     | ||'-.____'-.'-.____'-.       
     | ||  |      |  |      |        
      '-|  |      |  |      |          
         '-|______|__|______|          
"""

# Dibujo para los elfos y renos
elf_ascii = """
  \\(o_o)/
   |   | 
   / \\  ~ {name}
"""

reindeer_ascii = """
    ~{name}~
   /\\_/\\ 
  ( o o ) 
   (   )  
"""

# Frases divertidas para los elfos trabajando
working_phrases = [
    "¡Vaya, estos seran los mejores regalos de todos!",
    "El taller está más ocupado que nunca.",
    "¡Estoy en mi mejor momento!",
    "Ningún juguete es demasiado complicado para mí.",
    "¡A trabajar con una sonrisa!",
    "Los juguetes no se hacen solos, ¡vamos allá!",
    "Me encanta el olor a juguetes nuevos en la mañana.",
    "¡Esta Navidad va a ser la mejor de todas!",
    "Concentrado y motivado, como siempre.",
    "Cada día soy más eficiente.",
    "Hoy es un día productivo en el taller.",
    "¡Cuidado! ¡El mejor elfo en acción!",
    "Un juguete más y listo para otro.",
    "¡Parece que voy a romper mi récord de hoy!",
    "Nada puede detener mi productividad.",
    "¿Ya es hora del descanso? ¡No, a seguir trabajando!",
    "Voy a hacer que esta Navidad sea inolvidable.",
    "¡Vamos equipo, la Navidad nos necesita!",
    "Mis manos son mágicas para hacer juguetes.",
    "¡Un juguete más terminado, sigo invicto!"
]

# Variable para terminar
terminar = False

# Función para imprimir mensajes con timestamp
def log(message):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}\n")

# Función para el comportamiento de Santa Claus
def santa_claus():
    global elfos_problema, renos_de_vuelta, terminar
    while True:
        with santa_cond:
            # Esperar hasta que haya 3 elfos con problemas o los 9 renos estén de vuelta
            santa_cond.wait_for(lambda: elfos_problema >= 3 or renos_de_vuelta == NUM_RENOS)
            print(santa_surprised_ascii)  # Mostrar dibujo de Santa sorprendido
            if renos_de_vuelta == NUM_RENOS:
                log("Santa Claus: ¡Es hora de repartir los regalos!")
                print(santa_festive_ascii)  # Dibujo alegre de Santa
                terminar = True  # Establecer la variable de "terminar"
                renos_de_vuelta = 0  # Reiniciar la cuenta de renos
                # Notificar a todos los elfos y renos para continuar su trabajo
                santa_cond.notify_all()
                # También liberar el semáforo para que los elfos que estaban esperando puedan terminar
                for _ in range(elfos_problema):  # Liberar el semáforo para los elfos con problemas
                    elfos_sem.release()
                break  # Salir del bucle de Santa
            elif elfos_problema >= 3:
                log("Santa Claus: Ayudo a 3 elfos con problemas y vuelve a dormir")
                # Permitir que los tres elfos continúen
                for _ in range(3):
                    elfos_sem.release()  # Liberar el semáforo para permitir que los elfos sigan trabajando 
                elfos_problema = 0  # Reiniciar el contador de elfos con problemas
                print(santa_ascii)  # Mostrar dibujo de Santa volviendo a dormir

# Función para el comportamiento de los elfos
def elfo(elfo_id):
    global elfos_problema, terminar
    name = elf_names[elfo_id % len(elf_names)]  # Asignar un nombre único a cada elfo
    while True:
        # Frase aleatoria cuando el elfo está trabajando sin problemas
        working_message = random.choice(working_phrases)
        log(f"Elfo {name}: {working_message}") 
        time.sleep(random.uniform(1, 5)) 
        if terminar:
            break  # Salir si Santa ha repartido los regalos (ya son libres!)
        if random.random() < 0.3:  # 30% de probabilidad de tener un problema
            with mutex:
                elfos_problema += 1
                log(f"Elfo {name}: Tengo un problema, esperare a que hayan 3 elfos con problemas para pedir ayuda a Santa, hay {elfos_problema} elfos con problemas")
                print(elf_ascii.format(name=name))  # Mostrar dibujo del elfo
                if elfos_problema == 3:
                    # Despertar a Santa Claus
                    santa_cond.notify_all()
            # Esperar a que Santa resuelva el problema
            elfos_sem.acquire()  # Un elfo con un problema no puede seguir trabajando
        else:
            # Elfo trabajando normal (frase divertida ya impresa arriba)
            pass

        # Revisar si se debe salir después de intentar adquirir el semáforo
        if terminar:
            break

# Función para el comportamiento de los renos
def reno(reno_id):
    global renos_de_vuelta, terminar
    name = reindeer_names[reno_id % len(reindeer_names)]  # Asignar nombre único a cada reno
    while True:
        time.sleep(random.uniform(5, 10))  # El reno regresa después de un tiempo aleatorio
        if terminar:
            break  # Salir si Santa ha repartido los regalos
        with mutex:
            renos_de_vuelta += 1
            log(f"Reno {name}: He regresado de mis vacaciones, actualmente hay {renos_de_vuelta} renos de vuelta")
            print(reindeer_ascii.format(name=name))  # Mostrar dibujo del reno
            if renos_de_vuelta == NUM_RENOS:
                # Despertar a Santa Claus
                santa_cond.notify_all()

# Crear hilos
santa = threading.Thread(target=santa_claus)
elfos = [threading.Thread(target=elfo, args=(i,)) for i in range(NUM_ELFOS)]
renos = [threading.Thread(target=reno, args=(i,)) for i in range(NUM_RENOS)]

# Iniciar hilos
santa.start()
for e in elfos:
    e.start()
for r in renos:
    r.start()

# Esperar a que Santa termine
santa.join()
# Notificar a los elfos y renos que deben terminar
for e in elfos:
    e.join()
for r in renos:
    r.join()
