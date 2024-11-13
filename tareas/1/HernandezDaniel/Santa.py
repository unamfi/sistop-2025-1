import threading #Biblioteca de Hilos 
import time #Biblioteca de "simulador de trabajo haha"
import random #Biblioteca de aleatorieadad
import tkinter as tk #Bibliotecas de GUI
from tkinter import ttk #Bibliotecas de GUI
from PIL import Image, ImageTk #Bibliotecas de GUI 



######################  TIEMPOS DE TRABAJO ######################
#Tiempo que se tarda un elfo en crear un juguete
JugueteTime = 0.1
#Tiempo que se tarda Santa en Terminar la navidad
Navidad = 3
#Tiempo que tardaen en vacacionar los renos (intervalo purque puede ser que cada quien se tarde de foarma aleatoria cierto tiempo)
Vaciones = (0, 10)
#Tiempo que se lleva santa ayudando a los elfos
Ayudando = 1



#Los juguetes al ser un contador son variables que solo se puede acceder un hilo a la vez por lo que se tiene su mutex
juguetes = 0
mutex_juguetes = threading.Semaphore(1)
#Santa es un recurso compartido por los Elfos y por lo Renos por lo que usamos una variable de condicion
SantaVC = threading.Condition()
#Como los elfos en problemas son una variable que es accedida por santa y a la vez accedida por santa cuando termina de ayudarles se hacen dos mutex

MutexElfos = threading.Lock()#Este primer mutex es para que santa pueda "limpiar" la variable pues ayudo a todos los elfos
MutexElfos2 = threading.Lock() # Mutex Para que solo un hilo verifique que ya hay 3 en espera (1 elfo avisa q ya somos 3)
ElfosEnProblemas = 0 #Contador de elfos que hay en problemas

#Este variable de condicion es para que queden a la espera a que haya 3 elfos en problemas
MutexElfosVC = threading.Lock()
ElfosVC = threading.Condition(MutexElfosVC)


MutexRenos = threading.Lock() #Este mutex sirve para que los renos puedan acceder una por hilo a la cantidad de renos listos y validar si ya hay 9 renos listos

MutexRenosVC = threading.Lock() #Esta variable de condicion sirve para que los renos que regresaron de vacaciones queden a la espera de los demas
RenosVC = threading.Condition(MutexRenosVC)

RenosListos=0#Contador de cuantos renos listos hay


#Estos mutex sirven unicamente para que santa acceda a ciertas variables sin intervenir con los demas hilos 
MutexAccesoSanta = threading.Lock() #Como cuando se reinicia el contador de juguetes
MutexSantaDisp = threading.Lock() #O cuando se necesita saber si hay por lo menos 3 elfos a la espera

#La clase que establece el comportamiento del Elfo
class Elfo():
    def __init__ (self,num):
        self.num = num
        while True:
            self.__chambea__()
    
    #Funcion tomada del problema de los filosofos que reporta el estado del elfo
    def __reporta__(self, msg):
            print('Elfo %s%d: %s \n' % (' ' * 1, self.num, msg))
            
    #Reporta que tiene un problema
    def __problema__(self):
        self.__reporta__('Tengo un  problema')
                   
  #Funcion donde sucede la magia
    def __chambea__(self):
        if(random.choice([True, False, False, False, False, False, False, False])): #Random Choice porque pues el elfo puede inevitablemente llegar a tener o no un problema
            global ElfosEnProblemas 
            self.__problema__() #Aqui el elfo solo reporta que tiene un problema
            MutexElfos.acquire()  #Si hay un problema tomamos el mutex
            ElfosEnProblemas+=1 #Modificamos la variable (con el mutex se logra que solo un hilo acceda, sin perder datos)
            print("Hay %d elfos en problemas\n" %ElfosEnProblemas) 
            elfo_counter_label.config(text=str(ElfosEnProblemas)) #Actualizamos la GUI
            MutexElfos.release() #Liberamos el mutex para que puedan seguir habiendo elfos identificandose "Con problemas"
            MutexElfos2.acquire() #Tomamos el mutex para que solo un elfo avise que si ya hay 3 en problemas o que se quede a la espera
            if(ElfosEnProblemas >=3 ):
                print("Demasiados elfos |%d| en problemas" % ElfosEnProblemas, "Llamando a Santa!\n") 
                with SantaVC: #Toman el mutex de santa que estaba a la espera
                    SantaVC.notify_all() #lo despiertan
            MutexElfos2.release() #Dejan que otro hilo haga la comprobacion, aqui pueden haber varios hilos que intenten avisar a santa 
                                  #Como es normal si ya hay 3 elfos los que siguen intentaran avisar y acoplar un grupo, pero santa los liberara unicamente de 3 en 3
                                  #Si hubiera usado solo un mutex, digamos que inice en MutexElfos y se libere en MutexElfos2.realese() haria que obligatoriamente haya de
                                  #3 en 3 elfos reporten, pero pausaria la actualizacion de elfos en problemas, es decir, que mientras hay 3 elfos en problemas, aunque haya más
                                  #Los elfos no podrian decirlo hasta que pase el siguiente grupo, y aqui varios avisan a santa pero se mantienen actualizados y Santa los toma de 3 en 3 aun asi
                                  #Tambien se podria solucionar pasando el mensaje de impresion al bloque with SantaVC, pero pasaria lo mismo porque el bloque, bloquearia el acceso
                                  #A elfos en problemas
            with ElfosVC:
                ElfosVC.wait() #Se pone a dormir el hilo hasta que santa lo termine de ayudar (esta fuera del if porque sucede par aambos, el que pidio ayuda espera la ayuda)
                                #y el que estaba esperando la ayuda previamente                  
        global JugueteTime  #Tiempo de creacion de juguetes  
        time.sleep(JugueteTime)
        with mutex_juguetes: #Mutex para que no se pierdan datos al acceder al aumentar los jugeuetes
            global juguetes
            juguetes +=1
            juguetes_counter_label.config(text=str(juguetes))  #Actualizacion de GUI
            self.__reporta__('Termine el juguete, ahora hay %d juguetes. *' % juguetes)
            
#La Clase que determina el comportamiento del reno
class Reno():    
    def __init__(self, num):
        self.num = num
        while True:
            self.__vacaciona__() 
    #Reno reporta su estado, Ahora que lo veo creo que podria hacer una funcion para todos los que usan reporta, pero en la GUI se aprecia mucho mejor
    #Igual lo dejo por si quiere verlo en la consola de comandos     
    def __reporta__(self, msg):
            print('Reno %s%d: %s \n' % (' ' * 1, self.num, msg))
    
    #Aqui es donde el Reno vacaciona por un intervalo de tiempo        
    def __vacaciona__(self):
        global Vaciones
        self.__reporta__('De vacaciones...')
        time.sleep(random.uniform(*Vaciones))
        self.__chambea__() #y luego dice ok ya fue mucho, hora de chambiar
    
                
    def __chambea__(self):
        MutexRenos.acquire() #Tomamos el mutex para que solo un reno pueda decir ya estoy listo a la vez sin perder datos
        global RenosListos
        RenosListos+=1
        print(f"Reno %d listo. Total de renos listos: {RenosListos} \n" %self.num)
        reno_counter_label.config(text=str(RenosListos))   #Actualizacion de la GUI para el contador de renos
        if(RenosListos==9): #y que ademas pueda decir ok ya somos 9 
            with SantaVC:
                SantaVC.notify_all()
        MutexRenos.release() # O de lo contrario liberar el mutex 
        with RenosVC:        #y ponerse a esperar a los demas
            RenosVC.wait()
                    
                    
                 
        
#La clase que determina el comportamiento de JoJOJO FELIZ NAVIDAD!
class Santa():
    def __init__(self):
        while True:
            self.__Despertando__() #aqui lo puse como despertando, pero realmente es como un inicio, pues la primera accion que hace al ejecutar esta funcion es dormir
    
    #Santa reporta que esta haciendo                    
    def __reporta__(self, msg):
            print('Santa %s%d: %s \n' % (' ' * 1, 0, msg))
    #Santa reporta que duerme
    def __duerme__ (self):
        self.__reporta__("Estoy Durmiendo zzz...")
        santa_label.config(image=santa_sleeping_photo) #Actualizacion de la GUI, muestra imagen de santa durmiendo
        SantaVC.wait() #Santa se pone a la espera del Notify que lo despierte
        
    #La funcion donde Santa ayuda a los elfos
    def __OcupadoConElfos__(self):
        global Ayudando
        self.__reporta__('Ocupado con los elfos') #Reporta que los esta ayudando
        time.sleep(Ayudando)#simula el tiempo de ayuda
        with ElfosVC: #Toma la variable de condicion
            global ElfosEnProblemas #Toma la cantidad de elfos en problemas
            ElfosEnProblemas-=3 #Actualiza que ya ayudo a 3 elfos
            elfo_counter_label.config(text=str(ElfosEnProblemas)) #Actualiza el contador de elfos que necesitan ayuda en la GUI
            ElfosVC.notify(3) #Despierta los 3 hilos (Los 3 elfos que libero)
    
    #Santa desea la feliz navidad cuando volvieron los 9 renos
    def __FelizNavidad__(self):
        global RenosListos #Toma la cantidad de renos que esten listos
        global Navidad      #Cuanto toma la navidad en tiempo
        with MutexAccesoSanta: #Toma este mutex para reiniciar el contador de juguetes sin perdida de datos pues los elfos siguen chambiando aun en navidad
            global juguetes
            juguetes=0  
            juguetes_counter_label.config(text=str(juguetes))  #Actualiza el contador de jueguetes en la GUI
        with RenosVC: #Toma la variable de condicion en donde los renos tan dormidos
            self.__reporta__('JoJoJoJo Feliz Navidad!') #Feliz Navidad!
            RenosListos=0 #Hay 0 renos listos de nuevo
            reno_counter_label.config(text=str(RenosListos)) #Actualiza el contador en la GUI
            time.sleep(Navidad)  #Simula la navidad
            RenosVC.notify_all() #Renos vuelven al Caribe
        
    def __Despertando__(self): #Funcion de inicio de santa
        global RenosListos #Toma los renos que esten listos
        with SantaVC: #Toma la variable de condicion
            self.__duerme__() #Y se duerme a la espera de que alguien lo despierte
            #Cuando sucede un notify se despierta y evalua su entorno?
            if(RenosListos == 9): #Ah con que fueron ustedes Renos
                santa_label.config(image=santa_renos_photo)
                self.__FelizNavidad__()
        #Si fueron entonces aprovecha que esta despierto y dice, a ver elfos ocupan ayuda?
        MutexSantaDisp.acquire()
        global ElfosEnProblemas
        ElfosEnProblemascache = ElfosEnProblemas
        MutexSantaDisp.release()
        if(ElfosEnProblemascache>=3): # si son 3 es porque los elfos ocupan ayuda, se hace fuera del bloque SantaVC por la razon prinicpal de que, si los renos siempre estan listos
                                      #Entonces no los elfos sufririan de inanicion, fuera del bloque se garantiza que una vez pasados los renos, santa aprovecha y ayuda a los elfos
                                      #Pues sin juguetes no hay navidad
                                      #Tambien se hace asi porque si los renos no fueron quien alertaron a santa entonces automaticamente dice Ah fueron los elfos, no us eun elif pq
                                      #Si entra al SantaVC la variable "Elfos en problemas" se bloquearia hasta que santa termine de ayudar a los elfos y pues, los elfos en problemas
                                      #no se actualizarian correctamente.
                                      #Aqui tengo un poco de duda en si esto es trampa pq pues tengo que revisar el estado de cuantos elfos hay en problemas
                                      #Pero pues el planteamiento me parece indicar que siempre tengo que estar al pendiente de cuantos elfos hay en problemas y cuantos renos hay listos.
            santa_label.config(image=santa_awake_photo) # Actualizacion de la GUI
            self.__OcupadoConElfos__() #Se ocupa de los elfos en problemas

            
                    


# Función para iniciar los hilos de Santa, Renos y Elfos, lo hice con una funcion para que inicien junto la GUI
def start_threads():
    SantaH = threading.Thread(target=Santa)
    SantaH.start()

    Renos = [threading.Thread(target=Reno, args=[i]).start() for i in range(9)]
    Elfos = [threading.Thread(target=Elfo, args=[i]).start() for i in range(11)]
root = tk.Tk()

################################## Funcionamiento de la GUI omitir si es necesario #################################################################################
root.title("Taller de Santa")

# Cargar imágenes usando PIL
reno_img = Image.open("reno.png")
elfo_img = Image.open("elfo.png")
saco_img = Image.open("saco.png")
santa_sleeping_img = Image.open("santa_sleeping.png")
santa_awake_img = Image.open("santa_awake.png")


# Redimensionar las imágenes usando Image.Resampling.LANCZOS
reno_img = reno_img.resize((100, 100), Image.Resampling.LANCZOS)
elfo_img = elfo_img.resize((100, 100), Image.Resampling.LANCZOS)
saco_img = saco_img.resize((100, 100), Image.Resampling.LANCZOS)
santa_sleeping_img = santa_sleeping_img.resize((150, 150), Image.Resampling.LANCZOS)
santa_awake_img = santa_awake_img.resize((150, 150), Image.Resampling.LANCZOS)


# Convertir imágenes a PhotoImage para Tkinter
reno_photo = ImageTk.PhotoImage(reno_img)
elfo_photo = ImageTk.PhotoImage(elfo_img)
saco_photo = ImageTk.PhotoImage(saco_img)
santa_sleeping_photo = ImageTk.PhotoImage(santa_sleeping_img)
santa_awake_photo = ImageTk.PhotoImage(santa_awake_img)

# Crear frames para organizar la interfaz
frame_reno = ttk.Frame(root, padding="10")
frame_reno.grid(row=0, column=0)

frame_elfo = ttk.Frame(root, padding="10")
frame_elfo.grid(row=0, column=1)

frame_saco = ttk.Frame(root, padding="10")
frame_saco.grid(row=0, column=2)

frame_santa = ttk.Frame(root, padding="10")
frame_santa.grid(row=1, column=1)

# Añadir imagen y contador del reno
reno_label = ttk.Label(frame_reno, image=reno_photo)
reno_label.grid(row=0, column=0)

reno_counter_label = ttk.Label(frame_reno, text=str(RenosListos), font=("Arial", 24))
reno_counter_label.grid(row=0, column=1)

# Añadir imagen y contador del elfo
elfo_label = ttk.Label(frame_elfo, image=elfo_photo)
elfo_label.grid(row=0, column=0)

elfo_counter_label = ttk.Label(frame_elfo, text=str(ElfosEnProblemas), font=("Arial", 24))
elfo_counter_label.grid(row=0, column=1)

# Añadir imagen y contador del saco de juguetes
saco_label = ttk.Label(frame_saco, image=saco_photo)
saco_label.grid(row=0, column=0)

juguetes_counter_label = ttk.Label(frame_saco, text=str(juguetes), font=("Arial", 24))
juguetes_counter_label.grid(row=0, column=1)

# Añadir imagen de Santa (comienza despierto)
santa_label = ttk.Label(frame_santa, image= santa_sleeping_photo)
santa_label.grid(row=0, column=0)
# Cargar la imagen de Santa en sus renos
santa_renos_img = Image.open("santa_renos.png")
santa_renos_img = santa_renos_img.resize((100, 100))
santa_renos_photo = ImageTk.PhotoImage(santa_renos_img)

# Ejecutar la función que arranca los hilos en paralelo después de que inicie la interfaz
root.after(0, start_threads)

# Iniciar el loop de la ventana
root.mainloop()

