#!/usr/bin/python3
import time
import colorama
from random import random, choice
import threading

num_gatos = 30
num_ratones = 30
num_platos = 4

# ... Recuerdan.... ¿A los lectores y los escritores?
#                   ¿Cómo resolvían su conflicto?
#
# ¿Cómo puedo controlar el acceso a un _cuarto_ manteniendo _exclusión
# categórica_?
sem_cuarto_raton = threading.Semaphore(1)
sem_cuarto_gato = threading.Semaphore(1)
mut_contador = threading.Semaphore(1)
mut_puerta = threading.Semaphore(1)
cuenta = {}
difuntos = {}

class Domestico():
    def __init__(self, yo):
        self.num = yo
        self.vivo = True
        self.__reporta__('Iniciando')
        with mut_contador:
            if not self.tipo in cuenta.keys():
                cuenta[self.tipo] = 0

        while self.vivo:
            self.__reporta__('🛌  A dormir un poco... 💤')
            time.sleep(random())
            self.__reporta__('¡Desperté hambriento!')

            # Para evitar bloqueos mutuos, únicamente un animal doméstico puede
            # "evaluar la puerta" de entrada a la vez.
            with mut_puerta:

                # Patrón (doble-)apagador: "cruzo" el apagador contrario como un
                # torniquete, verificando que no haya ninguno del tipo opuesto
                # dentro.
                self.apagador_contrario.acquire()
                self.apagador_contrario.release()

                # Patrón (doble-)apagador: Si soy el primero de mi categoría,
                # adquiero el apagador.
                with mut_contador:
                    if cuenta[self.tipo] == 0:
                        self.__reporta__('Soy el primer %s' % self.tipo)
                        self.mi_apagador.acquire()
                    cuenta[self.tipo] += 1

            for tipo in cuenta.keys():
                self.__reporta__('Hay %d %s' % (cuenta[tipo], tipo))

            self.__verifica_otros__()

            mi_plato = choice(platos)
            self.__come__(mi_plato)

            # Patrón (doble-)apagador: Si soy el último de mi categoría, libero
            # el apagador.
            with mut_contador:
                cuenta[self.tipo] -= 1
                if cuenta[self.tipo] == 0:
                    self.__reporta__('🚪 Soy el último %s.' %
                                     self.tipo)
                    self.mi_apagador.release()

        if not self.tipo in difuntos.keys():
            difuntos[self.tipo] = 0
        difuntos[self.tipo] += 1

    def __reporta__(self, msg):
        print(self.mi_color +
              '%s%s%d: %s' % (self.tipo, ' ' * self.num, self.num, msg) +
              colorama.Fore.RESET + colorama.Back.RESET)

    def __come__(self, plato):
        self.__reporta__('Frente a los platos...')
        plato.acquire()
        # Comiendo
        self.__reporta__('¡Comamos! ñom ñom ñom...🍲🍲🍲')
        time.sleep(random())
        plato.release()

class Gato(Domestico):
    def __init__(self,yo):
        self.tipo = '😺'
        self.mi_color = colorama.Back.YELLOW + colorama.Fore.BLUE
        self.mi_apagador = sem_cuarto_gato
        self.apagador_contrario = sem_cuarto_raton

        super().__init__(yo)

    def __verifica_otros__(self):
        otros_tipos = cuenta.keys() - self.tipo
        for tipo in otros_tipos:
            if cuenta[tipo] > 0:
                self.__reporta__('¡UGH, UN %s! Me lo tengo que comer 🤮' % tipo)

class Raton(Domestico):
    def __init__(self,yo):
        self.tipo = '🐭'
        self.mi_color = colorama.Back.LIGHTBLACK_EX + colorama.Fore.MAGENTA
        self.mi_apagador = sem_cuarto_raton
        self.apagador_contrario = sem_cuarto_gato

        super().__init__(yo)

    def __verifica_otros__(self):
        otros_tipos = cuenta.keys() - self.tipo
        for tipo in otros_tipos:
            if cuenta[tipo] > 0:
                self.__reporta__('¡OH NO, UN %s! Me comió 💀' % tipo)
                self.vivo = False

platos = [threading.Semaphore(1) for i in range(num_platos)]
gatos = [threading.Thread(target=Gato, args=[i]).start() for i in range(num_gatos)]
ratones = [threading.Thread(target=Raton, args=[i]).start() for i in range(num_ratones)]


def rep_presentes():
    return ', '.join(['%s: %d' % (i, cuenta[i]) for i in cuenta.keys()])

def rep_difuntos():
    return ', '.join(['%s: %d' % (i, difuntos[i]) for i in difuntos.keys()])

while True:
    print(colorama.Back.RED +
          'ADENTRO: %s DIFUNTOS: %s' % (rep_presentes(), rep_difuntos()) +
          colorama.Back.RESET)
    time.sleep(1)
