from typing import Literal
from .common import Matrix, StepResult, format_matrix


def determinant_2x2(m: Matrix) -> float:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def determinant_3x3_sarrus(m: Matrix) -> float:
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    pos = a * e * i + b * f * g + c * d * h
    neg = c * e * g + a * f * h + b * d * i
    return pos - neg


def determinant_general(m: Matrix) -> float:
    n = len(m)
    if n == 0:
        return 0.0
    a = [row[:] for row in m]
    det = 1.0
    sign = 1.0
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[pivot][i]) < 1e-12:
            return 0.0
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            sign *= -1.0
        det *= a[i][i]
        pv = a[i][i]
        for r in range(i + 1, n):
            factor = a[r][i] / pv
            for c in range(i, n):
                a[r][c] -= factor * a[i][c]
    return det * sign


def determinant_with_steps(
    m: Matrix,
    method: Literal["cofactors", "sarrus", "cramer"] = "cofactors",
) -> StepResult:
    steps: list[str] = []
    if not m or len(m) != len(m[0]):
        return StepResult(steps=["La matriz debe ser cuadrada"], error="not_square")

    n = len(m)
    steps.append("CÁLCULO DE DETERMINANTE")
    steps.append("Matriz A:")
    steps.append(format_matrix(m))
    steps.append("")

    if n == 1:
        det = m[0][0]
    elif n == 2:
        det = determinant_2x2(m)
        steps.append("Usando fórmula 2×2: det(A) = ad - bc")
    elif n == 3 and method in ("sarrus", "cramer"):
        det = determinant_3x3_sarrus(m)
        steps.append("Usando regla de Sarrus (3×3)")
    else:
        # expansión por cofactores sobre la primera fila
        def cofactor_det(a: Matrix) -> float:
            k = len(a)
            if k == 1:
                return a[0][0]
            if k == 2:
                return determinant_2x2(a)
            total = 0.0
            for j in range(k):
                minor = [row[:j] + row[j + 1 :] for row in a[1:]]
                total += ((-1) ** j) * a[0][j] * cofactor_det(minor)
            return total

        det = cofactor_det(m)
        steps.append("Usando expansión por cofactores (1ª fila)")

    steps.append(f"det(A) = {det}")
    return StepResult(steps=steps, determinant=det)
