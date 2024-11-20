from MergeSort import merge_sort
from Promedio import promedios

def rr(procesos):

    A =[]

    esquema_visual = " "

    procesos = merge_sort(procesos)

    for proceso in procesos:

        A.append(proceso.t_requerido)

    t_final = 0

    while any(proceso.t_requerido > 0 for proceso in procesos):

        for proceso in procesos:

            quantum = 4

            if proceso.t_requerido == 0 or proceso.t_llegada > t_final:

                continue

            else:

                while(quantum > 0):
                
                    t_final = t_final + 1

                    proceso.t_requerido = proceso.t_requerido - 1

                    quantum = quantum - 1

                    esquema_visual = esquema_visual + proceso.name

                    if proceso.t_requerido == 0:

                        proceso.T = t_final - proceso.t_llegada
        
        t_final = t_final + 1

    for i in range(len(procesos)):

        procesos[i].t_requerido = A[i]

        procesos[i].E = procesos[i].T - procesos[i].t_requerido

        procesos[i].P = procesos[i].T / procesos[i].t_requerido

    return promedios(procesos),esquema_visual