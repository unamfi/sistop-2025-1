#Algoritmo obtenido de la red

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i].t_llegada < right_half[j].t_llegada:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1


        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

    return arr

def bubble_sort(arreglo):
    n = len(arreglo)
    for i in range(n - 1):

        for j in range(n - i - 1):

            if arreglo[j].t_requerido > arreglo[j + 1].t_requerido:

                arreglo[j], arreglo[j + 1] = arreglo[j + 1], arreglo[j]
    return arreglo