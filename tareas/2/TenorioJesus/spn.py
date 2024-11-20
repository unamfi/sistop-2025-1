from MergeSort import bubble_sort
from Promedio import promedios

def spn(procesos):

    A = []

    esquema_visual = ""

    procesos = bubble_sort(procesos)

    for proceso in procesos:

        A.append(proceso.t_requerido)

    t_final = 0

    while any(proceso.t_requerido > 0 for proceso in procesos):

        for proceso in procesos:

            if proceso.t_llegada <= t_final:

                while(proceso.t_requerido != 0):

                    t_final = t_final + 1

                    esquema_visual = esquema_visual + proceso.name

                    proceso.t_requerido = proceso.t_requerido -1

                proceso.T = t_final - proceso.t_llegada

        t_final = t_final+1
            
    for i in range(len(procesos)):

        procesos[i].t_requerido = A[i]

        procesos[i].E = procesos[i].T - procesos[i].t_requerido

        procesos[i].P = procesos[i].T / procesos[i].t_requerido

    return promedios(procesos),esquema_visual