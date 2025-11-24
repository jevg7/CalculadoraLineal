# core/vectors.py
from __future__ import annotations
from typing import List, TypedDict

Vector = List[float]
Matrix = List[List[float]]


class IndependenceResult(TypedDict):
    type: str   # "independence"
    isIndependent: bool
    details: List[str]


class BasisResult(TypedDict):
    type: str   # "base"
    isBasis: bool
    details: List[str]


def _format_matrix(matrix: Matrix) -> str:
    return "\n".join(
        "[ " + " ".join(f"{v:8.2f}" for v in row) + " ]"
        for row in matrix
    )


def _gaussian_elimination(matrix: Matrix) -> Matrix:
    m = len(matrix)
    n = len(matrix[0]) if m else 0
    A = [row[:] for row in matrix]
    current_row = 0

    for col in range(n):
        if current_row >= m:
            break

        # Buscar pivote
        pivot_row = max(range(current_row, m), key=lambda r: abs(A[r][col]))
        if abs(A[pivot_row][col]) < 1e-10:
            continue

        # Intercambiar
        if pivot_row != current_row:
            A[current_row], A[pivot_row] = A[pivot_row], A[current_row]

        # Normalizar
        pivot = A[current_row][col]
        for j in range(n):
            A[current_row][j] /= pivot

        # Eliminar hacia abajo
        for r in range(current_row + 1, m):
            factor = A[r][col]
            for j in range(n):
                A[r][j] -= factor * A[current_row][j]

        current_row += 1

    return A


def check_independence(vectors: List[Vector], dimension: int) -> IndependenceResult:
    details: List[str] = []

    if not vectors:
        return {
            "type": "independence",
            "isIndependent": False,
            "details": ["No hay vectores para analizar."]
        }

    details.append(f"Verificando independencia lineal de {len(vectors)} vectores en ℝ^{dimension}")

    # Vectores como columnas
    matrix: Matrix = [
        [vectors[col][row] for col in range(len(vectors))]
        for row in range(dimension)
    ]
    details.append("Matriz con vectores como columnas:")
    details.append(_format_matrix(matrix))

    reduced = _gaussian_elimination(matrix)
    details.append("Forma escalonada:")
    details.append(_format_matrix(reduced))

    pivots = 0
    for i in range(len(reduced)):
        for j in range(len(reduced[0])):
            if abs(reduced[i][j]) > 1e-10:
                if all(abs(reduced[i][k]) < 1e-10 for k in range(j)):
                    pivots += 1
                    break

    details.append(f"Número de pivotes: {pivots}")
    details.append(f"Número de vectores: {len(vectors)}")

    independent = pivots == len(vectors)
    if independent:
        details.append("✓ Los vectores son linealmente independientes.")
    else:
        details.append("✗ Los vectores son linealmente dependientes.")

    return {
        "type": "independence",
        "isIndependent": independent,
        "details": details,
    }


def check_basis(vectors: List[Vector], dimension: int) -> BasisResult:
    details: List[str] = []
    details.append(f"Verificando si los {len(vectors)} vectores forman una base de ℝ^{dimension}")

    if len(vectors) != dimension:
        details.append(
            f"✗ El conjunto tiene {len(vectors)} vectores, pero se requieren {dimension}."
        )
        return {"type": "base", "isBasis": False, "details": details}

    details.append("✓ El número de vectores es igual a la dimensión.")

    # Misma matriz de arriba
    matrix: Matrix = [
        [vectors[col][row] for col in range(len(vectors))]
        for row in range(dimension)
    ]

    reduced = _gaussian_elimination(matrix)
    pivots = 0
    for i in range(len(reduced)):
        for j in range(len(reduced[0])):
            if abs(reduced[i][j]) > 1e-10:
                if all(abs(reduced[i][k]) < 1e-10 for k in range(j)):
                    pivots += 1
                    break

    independent = pivots == len(vectors)
    if independent:
        details.append("✓ Los vectores son linealmente independientes.")
        details.append("✓ El conjunto forma una base.")
    else:
        details.append("✗ Los vectores son linealmente dependientes.")
        details.append("✗ El conjunto NO forma una base.")

    return {"type": "base", "isBasis": independent, "details": details}
