import threading
import time
import random
juguetes = 0
mutex_juguetes = threading.Semaphore(1)

ElfosEnProblemas = 0
MutexElfos = threading.Lock()
ElfosP = threading.Condition(MutexElfos)
ELfosEsperando= threading.Condition(MutexElfos)
RenosListos = 0
MutexRenos = threading.Lock()
RenosCompletos = threading.Condition(MutexRenos)
RenosALaEspera = threading.Condition(MutexRenos)
SantaMutex = threading.Lock()
SantaCV =  threading.Condition(SantaMutex)
start_barrier = threading.Barrier(20) 
SantaLibre = True
class Elfo(threading.Thread):
    def __init__ (self,num):
        self.num = num
        super().__init__()
    def run(self):
        start_barrier.wait()
        while True:
            self.__chambea__()

    def __reporta__(self, msg):
            print('Elfo %s%d: %s \n' % (' ' * self.num, self.num, msg))

    def __problema__(self):
        self.__reporta__('Tengo un  problema')
        
        
    def __chambea__(self):
        time.sleep(2)
        if(random.choice([True, False])):
            self.__problema__()
            with MutexElfos:
                global ElfosEnProblemas
                ElfosEnProblemas +=1
                print('Somos %d elfos en problemas \n' % ElfosEnProblemas)
                if(ElfosEnProblemas >=3):
                    self.__reporta__('Suficientes esperando, llamando a Santa!')
                    with SantaMutex:
                        global SantaLibre
                        if(SantaLibre!=True):
                            ELfosEsperando.wait()
                        SantaCV.notify_all()
                else:
                    ElfosP.wait()  
        with mutex_juguetes:
            global juguetes
            juguetes +=1
            juguete = juguetes
        self.__reporta__('Termine el juguete, ahora hay %d juguetes. *' % juguete)

class Reno(threading.Thread):    
    def __init__(self, num):
        self.num = num
        super().__init__()
        
            
    def __reporta__(self, msg):
            print('Reno %s%d: %s \n' % (' ' * self.num, self.num, msg))
    
    def run(self):
        start_barrier.wait()
        while True:
            self.__vacaciona__()
            
    def __vacaciona__(self):
        self.__reporta__('De vacaciones...')
        time.sleep(random.random() / 1)
        self.__chambea__()
    
    
    def __chambea__(self):
        with MutexRenos:
            global RenosListos
            RenosListos+=1
            print(f"Reno listo. Total de renos listos: {RenosListos}")
            if(RenosListos==9):
                if(SantaLibre==False):
                    RenosCompletos.wait()
                with SantaMutex:
                    SantaCV.notify_all()
                    time.sleep(2)
            else:
                RenosALaEspera.wait()
        
        
        
class Santa():
    def __init__(self):
        start_barrier.wait()
        while True:
            self.__duerme__()
            self.__Despertando__()
                            
    def __reporta__(self, msg):
            print('Santa %s%d: %s \n' % (' ' * 1, 0, msg))
            
    def __duerme__ (self):
        self.__reporta__("Estoy Durmiendo zzz...")

    def __OcupadoConElfos__(self):
        self.__reporta__('Ocupado con los elfos')
    
    def __FelizNavidad__(self):
        self.__reporta__('JoJoJoJo Feliz Navidad!')
    def __Despertando__(self):
        global RenosListos
        global ElfosEnProblemas
        global SantaLibre
        with SantaMutex:
            SantaCV.wait()  # Santa espera ser notificado
            if RenosListos >= 9:
                SantaLibre = False
                with RenosALaEspera:
                    self.__FelizNavidad__()
                    RenosListos = 0
                    RenosALaEspera.notify_all()  # Despertar a los renos
            if ElfosEnProblemas >= 3:
                SantaLibre = False
                self.__OcupadoConElfos__()
                with MutexElfos:
                    ElfosEnProblemas = 0
                    ElfosP.notify_all()  # Despertar a los elfos
            SantaLibre = True
                
                
                
                
SantaH = threading.Thread(target=Santa)
SantaH.start()

ElfosH = [Elfo(i) for i in range(1, 11)]
RenosH = [Reno(i) for i in range(1, 10)]

for hilo in ElfosH:
    hilo.start()
for hilo in RenosH:
    hilo.start()



# Unir todos los hilos
SantaH.join()
for hilo in ElfosH + RenosH:
    hilo.join()


