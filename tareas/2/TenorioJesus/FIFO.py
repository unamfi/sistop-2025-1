from MergeSort import merge_sort
from Promedio import promedios

def fifo(procesos):

    esquema_visual = ""

    procesos = merge_sort(procesos)

    t_final = 0

    for proceso in procesos:

        procesando = proceso.t_requerido

        while(procesando != 0):

            t_final = t_final + 1

            esquema_visual = esquema_visual + proceso.name

            procesando = procesando - 1
        
        proceso.T = t_final - proceso.t_llegada

        proceso.E = proceso.T - proceso.t_requerido

        proceso.P = proceso.T / proceso.t_requerido

    return promedios(procesos),esquema_visual