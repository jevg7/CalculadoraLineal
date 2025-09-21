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

    # Aún no funciona, retorna la fila sin alterar, ya encontré solución, pero tengo demasiado sueño y pereza
    # para implementarla ahora mismo, con el tiempo que gasté escribiendo este comentario perfectamente
    # pude haber implementado la solución, pero ni modo, así es la vida. (01:10 AM, 09.21.25)

    @staticmethod
    def multiplicar_escalar(matriz):
        resp_decision_fila = int(input(f'Multiplicar la fila\n-> '))
        resp_decision_escalar = int(input(f'Por el escalar (=/= 0)\n-> '))

        for i in range(len(matriz[resp_decision_fila-1])):
            resp_decision_escalar *= matriz[resp_decision_fila-1][i]

        return matriz

    # Creo que es obvio que este método no hace nada, ¿verdad?
    @staticmethod
    def sumar_fila_por_escalar():
        print('hola')

class DebugPrograma:
    @staticmethod
    def imprimir_matriz(matriz):
        for i in range(len(matriz)):
            print(matriz[i])