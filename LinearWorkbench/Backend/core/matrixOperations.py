from typing import List
from .common import Matrix, StepResult, format_matrix
from .determinants import _det_cofactors_recursive

def add_matrices_with_steps(a: Matrix, b: Matrix) -> StepResult:
    if not a or not b or len(a) != len(b) or len(a[0]) != len(b[0]):
        return StepResult(
            steps=["Dimensiones incompatibles para suma"], error="dimension_mismatch"
        )
    steps: list[str] = []
    steps.append("SUMA DE MATRICES: C = A + B")
    steps.append("Matriz A:")
    steps.append(format_matrix(a))
    steps.append("")
    steps.append("Matriz B:")
    steps.append(format_matrix(b))
    steps.append("")
    result: Matrix = []
    for i, row in enumerate(a):
        result_row: List[float] = []
        for j, val in enumerate(row):
            s = val + b[i][j]
            steps.append(f"C[{i+1},{j+1}] = {val} + {b[i][j]} = {s}")
            result_row.append(s)
        result.append(result_row)
    steps.append("")
    steps.append("Resultado C = A + B:")
    steps.append(format_matrix(result))
    return StepResult(steps=steps, matrix=result)


def subtract_matrices_with_steps(a: Matrix, b: Matrix) -> StepResult:
    if not a or not b or len(a) != len(b) or len(a[0]) != len(b[0]):
        return StepResult(
            steps=["Dimensiones incompatibles para resta"], error="dimension_mismatch"
        )
    steps: list[str] = []
    steps.append("RESTA DE MATRICES: C = A - B")
    result: Matrix = []
    for i, row in enumerate(a):
        result_row: List[float] = []
        for j, val in enumerate(row):
            r = val - b[i][j]
            steps.append(f"C[{i+1},{j+1}] = {val} - {b[i][j]} = {r}")
            result_row.append(r)
        result.append(result_row)
    steps.append("")
    steps.append("Resultado C = A - B:")
    steps.append(format_matrix(result))
    return StepResult(steps=steps, matrix=result)


def multiply_matrices_with_steps(a: Matrix, b: Matrix) -> StepResult:
    if not a or not b or len(a[0]) != len(b):
        return StepResult(
            steps=["Dimensiones incompatibles para producto"], error="dimension_mismatch"
        )
    steps: list[str] = []
    n_rows, n_inner, n_cols = len(a), len(a[0]), len(b[0])
    steps.append("PRODUCTO DE MATRICES: C = A × B")
    steps.append(f"Dimensiones: ({n_rows}×{n_inner})·({len(b)}×{n_cols})")
    steps.append("")
    result: Matrix = [[0.0] * n_cols for _ in range(n_rows)]
    for i in range(n_rows):
        for j in range(n_cols):
            total = 0.0
            terms = []
            for k in range(n_inner):
                prod = a[i][k] * b[k][j]
                terms.append(f"({a[i][k]}×{b[k][j]})")
                total += prod
            steps.append(f"C[{i+1},{j+1}] = " + " + ".join(terms) + f" = {total}")
            result[i][j] = total
        steps.append("")
    steps.append("Resultado C = A × B:")
    steps.append(format_matrix(result))
    return StepResult(steps=steps, matrix=result)


def scalar_multiply_with_steps(m: Matrix, k: float) -> StepResult:
    if not m:
        return StepResult(steps=["Matriz vacía"], error="empty_matrix")
    steps: list[str] = []
    steps.append(f"MULTIPLICACIÓN POR ESCALAR: k = {k}")
    result: Matrix = []
    for i, row in enumerate(m):
        result_row: list[float] = []
        for j, val in enumerate(row):
            r = k * val
            steps.append(f"C[{i+1},{j+1}] = {k}×{val} = {r}")
            result_row.append(r)
        result.append(result_row)
    steps.append("")
    steps.append("Resultado C = k × A:")
    steps.append(format_matrix(result))
    return StepResult(steps=steps, matrix=result)


def transpose_with_steps(m: Matrix) -> StepResult:
    if not m:
        return StepResult(steps=["Matriz vacía"], error="empty_matrix")
    rows, cols = len(m), len(m[0])
    steps: list[str] = []
    steps.append("TRANSPOSICIÓN: C = Aᵀ")
    result: Matrix = [[m[i][j] for i in range(rows)] for j in range(cols)]
    steps.append(format_matrix(result))
    return StepResult(steps=steps, matrix=result)


def inverse_with_steps(m: Matrix) -> StepResult:
    if not m or len(m) != len(m[0]):
        return StepResult(
            steps=["La matriz debe ser cuadrada para invertirla"], error="not_square"
        )
    n = len(m)
    steps: list[str] = []
    det = _det_cofactors_recursive(m)
    steps.append("INVERSA DE MATRIZ mediante Gauss-Jordan")
    steps.append(f"det(A) = {det}")
    if abs(det) < 1e-12:
        steps.append("det(A) ≈ 0 → la matriz no es invertible")
        return StepResult(steps=steps, error="singular")

    # matriz aumentada [A | I]
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            return StepResult(steps=steps + ["Pivote nulo"], error="singular")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        for j in range(2 * n):
            aug[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            for j in range(2 * n):
                aug[r][j] -= factor * aug[col][j]
    inv = [row[n:] for row in aug]
    steps.append("A⁻¹:")
    steps.append(format_matrix(inv))
    return StepResult(steps=steps, matrix=inv)
