from typing import Literal, List
from .common import Matrix, StepResult, format_matrix

def _det_2x2_steps(m: Matrix, steps: List[str]) -> float:
    a, b = m[0][0], m[0][1]
    c, d = m[1][0], m[1][1]
    res = a * d - b * c
    steps.append(f"  > Operación 2x2: ({a} * {d}) - ({b} * {c})")
    steps.append(f"  > Resultado parcial: {a*d} - {b*c} = {res}")
    return res

def _det_3x3_sarrus_steps(m: Matrix, steps: List[str]) -> float:
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    dp1, dp2, dp3 = a*e*i, b*f*g, c*d*h
    sum_pos = dp1 + dp2 + dp3
    ds1, ds2, ds3 = g*e*c, h*f*a, i*d*b
    sum_neg = ds1 + ds2 + ds3
    det = sum_pos - sum_neg
    steps.append("  > Diagonales Principales:")
    steps.append(f"    ({a}*{e}*{i}) + ({b}*{f}*{g}) + ({c}*{d}*{h})")
    steps.append(f"    = {dp1} + {dp2} + {dp3} = {sum_pos}")
    steps.append("  > Diagonales Secundarias:")
    steps.append(f"    ({g}*{e}*{c}) + ({h}*{f}*{a}) + ({i}*{d}*{b})")
    steps.append(f"    = {ds1} + {ds2} + {ds3} = {sum_neg}")
    steps.append(f"  > Total: {sum_pos} - {sum_neg} = {det}")
    return det

def _get_minor(m: Matrix, i: int, j: int) -> Matrix:
    return [row[:j] + row[j+1:] for row in (m[:i] + m[i+1:])]

def _det_cofactors_recursive(m: Matrix, steps: List[str], depth: int = 0) -> float:
    n = len(m)
    indent = "  " * depth
    if n == 1:
        return m[0][0]
    if n == 2:
        val = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        if depth < 2:
            steps.append(f"{indent}Calculando det 2x2: ({m[0][0]}*{m[1][1]}) - ({m[0][1]}*{m[1][0]}) = {val}")
        return val
    det = 0.0
    row_expr = []
    steps.append(f"{indent}Expandiendo por fila 0 de matriz {n}x{n}...")
    for c in range(n):
        element = m[0][c]
        if element == 0:
            continue
        sign = 1 if c % 2 == 0 else -1
        sign_str = "+" if sign == 1 else "-"
        minor = _get_minor(m, 0, c)
        minor_det = _det_cofactors_recursive(minor, steps, depth + 1)
        term = sign * element * minor_det
        det += term
        row_expr.append(f"{sign_str}({element} * {minor_det})")
    steps.append(f"{indent}Sumatoria fila: {' '.join(row_expr)} = {det}")
    return det

def _cramer_det(m: Matrix, steps: List[str]) -> float:
    rows = len(m)
    cols = len(m[0])
    matrix_a = []
    
    if cols == rows + 1:
        steps.append("Matriz Aumentada detectada. Extrayendo matriz de coeficientes (A)...")
        matrix_a = [row[:-1] for row in m]
    elif cols == rows:
        steps.append("Matriz Cuadrada detectada. Usando como matriz de coeficientes (A)...")
        matrix_a = [row[:] for row in m]
    else:
        steps.append(f"ERROR: Dimensiones inválidas ({rows}x{cols}) para Cramer.")
        return 0.0
        
    steps.append(format_matrix(matrix_a))
    steps.append("Calculando Determinante del Sistema (Δ):")
    
    det_sys = 0.0
    if len(matrix_a) == 3:
        det_sys = _det_3x3_sarrus_steps(matrix_a, steps)
    elif len(matrix_a) == 2:
        det_sys = _det_2x2_steps(matrix_a, steps)
    else:
        det_sys = _det_cofactors_recursive(matrix_a, steps)
        
    steps.append(f"-> Δ (Delta Sistema) = {det_sys}")
    return det_sys

def determinant_with_steps(
    m: Matrix,
    method: Literal["cofactors", "sarrus", "cramer"] = "cofactors",
) -> StepResult:
    steps: list[str] = []
    if not m:
        return StepResult(steps=["Matriz vacía"], error="empty")
    
    steps.append(f"CÁLCULO DE DETERMINANTE (Método: {method.upper()})")
    steps.append("-" * 40)

    det = 0.0
    
    if method == "cramer":
        det = _cramer_det(m, steps)
    else:
        rows = len(m)
        cols = len(m[0])
        
        if rows != cols:
            return StepResult(steps=["La matriz debe ser cuadrada para este método."], error="not_square")
            
        steps.append("Matriz A:")
        steps.append(format_matrix(m))
        
        if rows == 1:
            det = m[0][0]
            steps.append(f"Matriz 1x1: {det}")
        elif rows == 2:
            det = _det_2x2_steps(m, steps)
        elif rows == 3 and method == "sarrus":
            det = _det_3x3_sarrus_steps(m, steps)
        else:
            det = _det_cofactors_recursive(m, steps)

    steps.append("-" * 40)
    steps.append(f"RESULTADO FINAL: det = {det}")
    return StepResult(steps=steps, determinant=det)