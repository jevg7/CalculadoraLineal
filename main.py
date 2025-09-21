from funciones.func_matriz import MetodosMatrices, DebugPrograma, OperacionesMatrices

crear_matriz = MetodosMatrices.crear_matriz()
imprimir_matriz = DebugPrograma.imprimir_matriz(crear_matriz)
multiplicar_escalar = OperacionesMatrices.multiplicar_escalar(crear_matriz)
imprimir_matriz2 = DebugPrograma.imprimir_matriz(multiplicar_escalar)