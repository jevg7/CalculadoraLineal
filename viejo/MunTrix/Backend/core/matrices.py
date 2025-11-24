from __future__ import annotations
from typing import List, Literal, Dict, Any, Tuple
from copy import deepcopy

Matrix = List[List[float]]
Operation = Literal["add", "subtract", "multiply", "scalar", "transpose", "inverse"]


def add_matrices(m1: Matrix, m2: Matrix) -> Matrix:
    return [[m1[i][j] + m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]


def subtract_matrices(m1: Matrix, m2: Matrix) -> Matrix:
    return [[m1[i][j] - m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]


def multiply_matrices(m1: Matrix, m2: Matrix) -> Matrix:
    rows, cols, inner = len(m1), len(m2[0]), len(m1[0])
    result: Matrix = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            s = 0.0
            for k in range(inner):
                s += m1[i][k] * m2[k][j]
            result[i][j] = s
    return result


def scalar_multiply(m: Matrix, s: float) -> Matrix:
    return [[s * val for val in row] for row in m]


def transpose_matrix(m: Matrix) -> Matrix:
    return [list(col) for col in zip(*m)]


def _minor(m: Matrix, row: int, col: int) -> Matrix:
    return [
        [m[i][j] for j in range(len(m)) if j != col]
        for i in range(len(m)) if i != row
    ]


def determinant(m: Matrix) -> float:
    n = len(m)
    if n == 0:
        return 0.0
    if n == 1:
        return m[0][0]
    if n == 2:
        return m[0][0]*m[1][1] - m[0][1]*m[1][0]

    det = 0.0
    for j in range(n):
        cofactor = ((-1) ** j) * m[0][j]
        det += cofactor * determinant(_minor(m, 0, j))
    return det


def inverse_matrix(m: Matrix) -> Matrix | None:
    # Gauss-Jordan como en tu React
    n = len(m)
    if n == 0 or n != len(m[0]):
        return None

    det = determinant(m)
    if abs(det) < 1e-10:
        return None

    # Matriz aumentada [A | I]
    aug: Matrix = [
        m[i] + [1.0 if i == j else 0.0 for j in range(n)]
        for i in range(n)
    ]
    # Eliminación
    for i in range(n):
        # Pivote
        max_row = max(range(i, n), key=lambda r: abs(aug[r][i]))
        aug[i], aug[max_row] = aug[max_row], aug[i]

        pivot = aug[i][i]
        if abs(pivot) < 1e-12:
            return None

        # Normalizar fila
        for j in range(2*n):
            aug[i][j] /= pivot

        # Eliminar en otras filas
        for r in range(n):
            if r == i:
                continue
            factor = aug[r][i]
            for j in range(2*n):
                aug[r][j] -= factor * aug[i][j]

    # Extraer inversa
    inv = [row[n:] for row in aug]
    return inv


def perform_operation(
    op: Operation,
    first: Matrix | None,
    second: Matrix | None,
    scalar: float | None = None
) -> Tuple[Matrix | None, list[str], str | None]:
    """
    Devuelve (resultado, pasos, error)
    Razonablemente equivalente a calculateOperation en MatrixOperations.tsx
    """
    steps: list[str] = []
    error: str | None = None
    result: Matrix | None = None

    try:
        if op in ("add", "subtract", "multiply") and (first is None or second is None):
            return None, [], "Faltan matrices para la operación."

        if op in ("transpose", "inverse", "scalar") and first is None:
            return None, [], "Debe proporcionar una matriz."

        if op == "add":
            steps.append("Suma de matrices A + B.")
            result = add_matrices(first, second)  # type: ignore[arg-type]
        elif op == "subtract":
            steps.append("Resta de matrices A - B.")
            result = subtract_matrices(first, second)  # type: ignore[arg-type]
        elif op == "multiply":
            steps.append("Multiplicación de matrices A × B.")
            result = multiply_matrices(first, second)  # type: ignore[arg-type]
        elif op == "scalar":
            if scalar is None:
                return None, [], "Falta el valor escalar."
            steps.append(f"Multiplicación escalar: {scalar} × A.")
            result = scalar_multiply(first, scalar)  # type: ignore[arg-type]
        elif op == "transpose":
            steps.append("Transposición de matriz A.")
            result = transpose_matrix(first)  # type: ignore[arg-type]
        elif op == "inverse":
            steps.append("Cálculo de inversa de A mediante Gauss-Jordan.")
            inv = inverse_matrix(first)  # type: ignore[arg-type]
            if inv is None:
                return None, steps, "La matriz es singular o no cuadrada, no tiene inversa."
            result = inv
        else:
            error = "Operación no soportada."
    except Exception:
        error = "Error al realizar la operación."

    return result, steps, error