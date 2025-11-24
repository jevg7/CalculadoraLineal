# core/systems.py
from __future__ import annotations
from typing import List, Literal, TypedDict, Any
from copy import deepcopy

Matrix = List[List[float]]
SolutionType = Literal["unique", "infinite", "none"]


class SystemSolution(TypedDict):
    type: SolutionType
    solution: List[float] | None
    steps: List[str]


def _format_matrix(m: Matrix, decimals: int = 2) -> str:
    lines = []
    for row in m:
        line = "[ " + " ".join(f"{v:8.{decimals}f}" for v in row) + " ]"
        lines.append(line)
    return "\n".join(lines)


def solve_linear_system(augmented: Matrix) -> SystemSolution:
    """
    Toma una matriz aumentada (n x (n+1)) y devuelve tipo de solución y pasos.
    """
    steps: list[str] = []
    a = deepcopy(augmented)
    n = len(a)
    m = len(a[0]) if n > 0 else 0

    steps.append("Matriz aumentada inicial:")
    steps.append(_format_matrix(a))

    current_row = 0
    for col in range(m - 1):
        if current_row >= n:
            break

        # Buscar pivote
        pivot_row = max(range(current_row, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot_row][col]) < 1e-10:
            continue

        # Intercambio de filas
        if pivot_row != current_row:
            a[current_row], a[pivot_row] = a[pivot_row], a[current_row]
            steps.append(f"F{current_row + 1} ↔ F{pivot_row + 1}")
            steps.append(_format_matrix(a))

        # Normalizar fila pivote
        pivot = a[current_row][col]
        if abs(pivot - 1) > 1e-10:
            for j in range(col, m):
                a[current_row][j] /= pivot
            steps.append(f"F{current_row + 1} = F{current_row + 1} / {pivot:.4g}")
            steps.append(_format_matrix(a))

        # Eliminar en otras filas
        for r in range(n):
            if r == current_row:
                continue
            factor = a[r][col]
            if abs(factor) < 1e-10:
                continue
            for j in range(col, m):
                a[r][j] -= factor * a[current_row][j]
            steps.append(
                f"F{r + 1} = F{r + 1} - ({factor:.4g}) × F{current_row + 1}"
            )
            steps.append(_format_matrix(a))

        current_row += 1

    steps.append("Forma escalonada reducida alcanzada.")

    # Tipo de solución
    # 1) Verificar contradicciones
    for i in range(n):
        lhs_all_zero = all(abs(v) < 1e-10 for v in a[i][: m - 1])
        rhs = a[i][m - 1]
        if lhs_all_zero and abs(rhs) > 1e-10:
            steps.append(
                f"Contradicción en fila {i + 1}: 0 = {rhs:.4g} ⇒ sistema incompatible."
            )
            return {"type": "none", "solution": None, "steps": steps}

    # 2) Contar variables libres
    leading_ones = set()
    for i in range(n):
        for j in range(m - 1):
            if abs(a[i][j] - 1) < 1e-10:
                if all(abs(a[i][k]) < 1e-10 for k in range(j)):
                    leading_ones.add(j)
                    break

    free_vars = (m - 1) - len(leading_ones)
    if free_vars > 0:
        steps.append(
            f"Sistema con {free_vars} variable(s) libre(s) ⇒ infinitas soluciones."
        )
        return {"type": "infinite", "solution": None, "steps": steps}

    # 3) Solución única
    solution = [0.0] * (m - 1)
    for i in range(n):
        for j in range(m - 1):
            if abs(a[i][j] - 1) < 1e-10 and all(abs(a[i][k]) < 1e-10 for k in range(j)):
                solution[j] = a[i][m - 1]
                break

    steps.append("Solución única encontrada:")
    for i, val in enumerate(solution):
        steps.append(f"x{i + 1} = {val:.4g}")

    return {"type": "unique", "solution": solution, "steps": steps}
