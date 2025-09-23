class MetodosMatrices:
    @staticmethod
    def crear_matriz():
        # Creación de la matriz (lista de listas, donde resp_numcolumnas = tamaño de la lista y resp_numfilas = cantidad de listas)
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
            valor_independiente = int(input(f'Introduzca el término independiente de la fila {i+1}\n-> '))
            matriz_x.append(valor_independiente)

            matriz.append(matriz_x)
        return matriz

# Clase que contiene las 3 operaciones permitidas;
# Intercambio entre filas, multiplicar la fila por un escalar distinto de cero y sumar el producto de un escalar y una fila con otra fila
class OperacionesMatrices:
    @staticmethod
    def intercambio(matriz):
        resp_intercambio1 = int(input(f'Intercambiar fila\n-> '))
        resp_intercambio2 = int(input(f'Por la fila\n-> '))

        matriz[resp_intercambio1-1], matriz[resp_intercambio2-1] = matriz[resp_intercambio2-1], matriz[resp_intercambio1-1]

        return matriz

    @staticmethod
    def multiplicar_escalar(matriz):
        resp_decision_fila = int(input(f'Multiplicar la fila\n-> '))
        resp_decision_escalar = int(input(f'Por el escalar (=/= 0)\n-> '))

        for i in range(len(matriz[resp_decision_fila-1])):
            matriz[resp_decision_fila-1][i] = resp_decision_escalar * matriz[resp_decision_fila-1][i]

        return matriz

    # No es completamente funcional aún
    @staticmethod
    def sumar_fila_por_escalar(matriz):
        mult_escalar = OperacionesMatrices.multiplicar_escalar(matriz)
        resp_sumar_fila = int(input(f'Y sumar la fila multiplicada a la fila\n-> '))

        for i in range(len(matriz[resp_sumar_fila-1])):
            matriz[resp_sumar_fila-1][i] = mult_escalar[i] + matriz[resp_sumar_fila-1][i]

class DebugPrograma:
    @staticmethod
    def imprimir_matriz(matriz):
        for i in range(len(matriz)):
            print(matriz[i])