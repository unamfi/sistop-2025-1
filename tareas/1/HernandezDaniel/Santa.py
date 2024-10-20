import threading
import time
import random
#Los juguetes al ser un contador son variables que solo se puede acceder un hilo a la vez por lo que se tiene su mutex
juguetes = 0
mutex_juguetes = threading.Semaphore(1)

#Santa es un recurso compartido por los Elfos y por lo Renos por lo que usamos una variable de condicion
SantaVC = threading.Condition()

#Como los elfos en problemas son una variable que es accedida por santa y a la vez accedida por santa cuando termina de ayudarles se hacen dos mutex
#Este primer mutex es para que santa pueda "limpiar" la variable pues ayudo a todos los elfos
MutexElfos = threading.Lock()
ElfosEnProblemas = 0
#Este segundo mutex es una variable de condicion para que los elfos accedan a si tienen un problema o no, pero sin bloquearle el acceso a santa
ElfosVC = threading.Condition()
#Esta ultima variable de condicion es necesaria para evitar el bloqueo mutuo, pues si santa esta ocupado y todos los elfos tienen problemas ya no abra elfo que pueda alertar a santa
#Entonces Santa cuando se desocupa le llama la atencion a esta variable de condicion para "decirle" a los elfos, ¡oigan ya estoy dormido!
ElfosVCSO = threading.Condition()
#Esta variable de condicion se ocupa de que se acceda al contador de renos listos de manera adecuada, pero ademas, me permite que los renos que ya regresaron de vacaciones queden a la espera
#de los renos que no han regresado de vacaciones, asi cuando lleguen a los 9 renos, le dicen a santa, ¡Santa es hora de partir! y santa se encarga de devolverlos a vacacionar.
RenosVC = threading.Condition()
RenosListos=0

#Esta variable se usa como condicion para que los elfos no se bloqueen entre ellos y asi se identifique cuando santa esta despierto (False) o dormido (True)
SantaLibre = True
MutexAccesoSanta = threading.Lock()

class Elfo():
    def __init__ (self,num):
        self.num = num
        while True:
            self.__chambea__()

    #Esta funcion la tome del problema de los filosofs y la modifique de forma que reporte que hace cada elfo.
    def __reporta__(self, msg):
            print('Elfo %s%d: %s \n' % (' ' * self.num, self.num, msg))
            
    #Como se dice, reporta si tiene un problema
    def __problema__(self):
        self.__reporta__('Tengo un  problema')
        
    #Funcion donde sucede la magia
    def __chambea__(self):
        if(random.choice([True, False])): #Random Choice porque pues el elfo puede inevitablemente llegar a tener o no un problema
            self.__problema__()
            global ElfosEnProblemas
            with MutexElfos:               #Si hay un problema tomamos el mutex
                ElfosEnProblemas+=1
                print("Hay %d elfos en problemas\n" %ElfosEnProblemas)
                if(ElfosEnProblemas >=3 ):
                    if(SantaLibre):
                        with SantaVC:
                            print("Demasiados elfos |%d| en problemas" % ElfosEnProblemas, "Llamando a Santa!\n")
                            SantaVC.notify_all()
                    else:
                        with ElfosVCSO: #Tomamos el mutex de los que justo agarraron a santa ocupado 
                                ElfosVCSO.wait()
                                with SantaVC:
                                    print("Demasiados elfos |%d| en problemas" % ElfosEnProblemas, "Llamando a Santa!\n")
                                    SantaVC.notify_all()
                    if(SantaLibre== False):
                        with ElfosVC:
                            ElfosVC.wait()
                    else:
                         with ElfosVCSO: #Tomamos el mutex de los que justo agarraron a santa ocupado 
                                ElfosVCSO.wait()
                        

        with mutex_juguetes:
            time.sleep(0.5)
            global juguetes
            juguetes +=1
            juguete = juguetes
        self.__reporta__('Termine el juguete, ahora hay %d juguetes. *' % juguete)

class Reno():    
    def __init__(self, num):
        self.num = num
        while True:
            self.__vacaciona__() 
            
    def __reporta__(self, msg):
            print('Reno %s%d: %s \n' % (' ' * self.num, self.num, msg))
    
            
    def __vacaciona__(self):
        self.__reporta__('De vacaciones...')
        time.sleep(random.uniform(0, 10))
        self.__chambea__()
    
    
    def __chambea__(self):
        global RenosListos
        with RenosVC:
            RenosListos+=1
            print(f"Reno %d listo. Total de renos listos: {RenosListos} \n" %self.num)
            if(RenosListos==9):
                if(SantaLibre):
                    with SantaVC:
                        SantaVC.notify_all()
                    
            RenosVC.wait()
                    
                    
        
        
        
class Santa():
    def __init__(self):
        while True:
            self.__Despertando__()
                            
    def __reporta__(self, msg):
            print('Santa %s%d: %s \n' % (' ' * 1, 0, msg))
            
    def __duerme__ (self):
        self.__reporta__("Estoy Durmiendo zzz...")

    def __OcupadoConElfos__(self):
        self.__reporta__('Ocupado con los elfos')
        global ElfosEnProblemas
        with MutexAccesoSanta:
            ElfosEnProblemas-=3

    def __FelizNavidad__(self):
        global RenosListos
        global juguetes
        with mutex_juguetes:
            juguetes=0
            print('Jueguetes = %d' % juguetes)
        self.__reporta__('JoJoJoJo Feliz Navidad!')
        with MutexAccesoSanta:
            RenosListos=0


        
    def __Despertando__(self):
        global RenosListos
        global SantaLibre 
        with SantaVC:
            self.__duerme__()
            SantaLibre= True
            with ElfosVCSO:
                ElfosVCSO.notify_all()
            SantaVC.wait()
            SantaLibre = False
            if(RenosListos == 9):
                self.__FelizNavidad__()
                with RenosVC:
                    RenosVC.notify_all()
            else:
                with ElfosVC:
                    self.__OcupadoConElfos__()
                    ElfosVC.notify_all()


                    

SantaH = threading.Thread(target=Santa)
SantaH.start()               
Renos = [threading.Thread(target=Reno, args=[i]).start() for i in range(9)]
Elfos = [threading.Thread(target=Elfo, args=[i]).start() for i in range(11)]
