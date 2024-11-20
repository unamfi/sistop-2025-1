# Sobre los algoritmos
Se pueden ajustar los datos de rondas que se quieran hacer con los mismos procesos, se puede ajustar la cantidad de procesos, lo maximo que pueden durar y lo maximo que pueden tardar en llegar.
Para el Round Robin se puede ajustar los Quantums, para FB se pueden ajustar los quantums para ambas colas. Por su naturaleza SPN y FCFS tienen una funcion especifica para su representacion visual, mientras que para RR y FB se hace sobre la marcha, es decir, conforme llegan los procesos en el algoritmo.
# Sobre la implementacion
La implementacion trabaja de tal forma que si un proceso llega al final del proceso que se estaba ejecutando, se tomara como si llegara "despues", si llega en mitad del proceso, es decir, si el proceso acaba en 4 y llego en 3 se respeta su posicion.
# Sobre los datos
Se registraron los siguientes datos:
# Comparación de Algoritmos de Planificación

| **Caso** | **Algoritmo** | **T (Tiempo Total)** | **E (Tiempo de Espera)** | **P (Penalización)** | **Secuencia de Procesos** |
|----------|---------------|----------------------|--------------------------|--------------------------------------|---------------------------|
| **1**    | **FCFS**      | 7.80                 | 4.40                     | 2.35                                 | P0P0P2P2P2P2P2P3P3P4P4P4P4P1P1P1P1 |
|          | **RR**        | 9.80                 | 6.40                     | 2.71                                 | P0P0P2P3P4P2P1P3P4P2P1P4P2P1 |
|          | **SPN**       | 6.80                 | 3.40                     | 1.75                                 | P0P0P3P3P4P4P4P4P1P1P1P1P2P2P2P2P2 |
|          | **FB**        | 10.00                | 6.60                     | 2.82                                 | P0P0P2P3P4P1P2P2P3P4P4P1P1P2P2P4P1 |
| **2**    | **FCFS**      | 5.20                 | 2.60                     | 2.32                                 | P1P1P1P2P0P3P3P3P3P3P4P4P4 |
|          | **RR**        | 5.40                 | 2.80                     | 2.17                                 | P1P1P2P1P0P3P4P3P4P3P4P3P3 |
|          | **SPN**       | 4.80                 | 2.20                     | 2.11                                 | P1P1P1P2P0P4P4P4P3P3P3P3P3 |
|          | **FB**        | 5.40                 | 2.80                     | 1.77                                 | P1P2P0P3P4P1P1P3P3P4P4P3P3 |
| **3**    | **FCFS**      | 5.40                 | 3.00                     | 2.52                                 | P1P1P2P4P4P3P3P3P3P3P0P0 |
|          | **RR**        | 5.60                 | 3.20                     | 2.40                                 | P1P2P4P1P3P4P0P3P0P3P3P3 |
|          | **SPN**       | 4.60                 | 2.20                     | 1.80                                 | P2P1P1P4P4P0P0P3P3P3P3P3 |
|          | **FB**        | 6.40                 | 4.00                     | 2.80                                 | P1P2P4P3P0P1P4P3P3P0P3P3 |
| **4**    | **FCFS**      | 7.20                 | 4.00                     | 3.15                                 | P4P4P4P4P0P0P0P0P1P2P2P2P2P2P3P3 |
|          | **RR**        | 7.40                 | 4.20                     | 2.53                                 | P4P4P4P4P0P1P2P0P3P2P0P3P2P0P2P2 |
|          | **SPN**       | 5.60                 | 2.40                     | 1.68                                 | P4P4P4P4P1P3P3P0P0P0P0P2P2P2P2P2 |
|          | **FB**        | 8.20                 | 5.00                     | 2.63                                 | P4P4P4P0P1P2P3P4P0P0P2P2P3P0P2P2 |
| **5**    | **FCFS**      | 6.00                 | 3.60                     | 3.48                                 | P1P1P2P2P2P2P2P3P0P4P4P4 |
|          | **RR**        | 5.80                 | 3.40                     | 2.51                                 | P1P2P1P2P3P0P4P2P4P2P4P2 |
|          | **SPN**       | 4.00                 | 1.60                     | 1.35                                 | P1P1P3P0P4P4P4P2P2P2P2P2 |
|          | **FB**        | 5.40                 | 3.00                     | 1.95                                 | P1P2P3P0P4P1P2P2P4P4P2P2 |

