class CrearMatriz:
    @staticmethod
    def crear_matriz():
        # Creación de la matriz (lista de listas, donde X = tamaño de la lista y Y = cantidad de listas)
        matriz = []

        # Entrada del usuario del número de filas y número de columnas
        resp_numfilas = int(input('Introduzca el número de filas que desea\n-> '))
        resp_numcolumnas = int(input('Introduzca el número de columnas que desea\n-> '))

        # Ciclo for encargado de introducir valores para la matriz
        for i in range(resp_numfilas):
            matriz_x = []
            for j in range(resp_numcolumnas):
                valor_x = int(input(f'Introduzca el valor en la posición ({i+1}, {j+1})\n-> '))
                matriz_x.append(valor_x)
            matriz.append(matriz_x)
        return matriz

class DebugPrograma:
    @staticmethod
    def imprimir_matriz(matriz):
        for i in range(len(matriz)):
            print(matriz[i])