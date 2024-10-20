import threading
import time
import random
juguetes = 0
mutex_juguetes = threading.Semaphore(1)
SantaVC = threading.Condition()
MutexElfos = threading.Lock()
RenosVC = threading.Condition()
RenosListos=0
ElfosEnProblemas = 0
ElfosVC = threading.Condition()
ElfosVCSO = threading.Condition()
SantaLibre = True
class Elfo():
    def __init__ (self,num):
        self.num = num
        while True:
            self.__chambea__()

    def __reporta__(self, msg):
            print('Elfo %s%d: %s \n' % (' ' * self.num, self.num, msg))

    def __problema__(self):
        self.__reporta__('Tengo un  problema')
        
        
    def __chambea__(self):
        if(random.choice([True, False])):
            self.__problema__()
            global ElfosEnProblemas
            with ElfosVC:
                ElfosEnProblemas+=1
                print("Hay %d elfos en problemas\n" %ElfosEnProblemas)
                if(ElfosEnProblemas==3):
                    with SantaVC:
                        if(SantaLibre!=True):
                            with ElfosVCSO:
                                ElfosVCSO.wait()
                        print("Demasiados elfos |%d| en problemas" % ElfosEnProblemas, "Llamando a Santa!\n")
                        SantaVC.notify_all()
                ElfosVC.wait()
        
        with mutex_juguetes:
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
        time.sleep(random.random())
        self.__chambea__()
    
    
    def __chambea__(self):
        global RenosListos
        with RenosVC:
            RenosListos+=1
            print(f"Reno %d listo. Total de renos listos: {RenosListos} \n" %self.num)
            if(RenosListos==9):
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
        with MutexElfos:
            ElfosEnProblemas=0

    def __FelizNavidad__(self):
        self.__reporta__('JoJoJoJo Feliz Navidad!')
        global RenosListos
        with RenosVC:
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
                time.sleep(2)
                with RenosVC:
                    RenosVC.notify_all()
            else:
                with ElfosVC:
                    ElfosVC.notify_all()      
                self.__OcupadoConElfos__()
                    

SantaH = threading.Thread(target=Santa)
SantaH.start()               
Renos = [threading.Thread(target=Reno, args=[i]).start() for i in range(9)]
Elfos = [threading.Thread(target=Elfo, args=[i]).start() for i in range(11)]
