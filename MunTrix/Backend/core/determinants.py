# core/determinants.py
from __future__ import annotations
from typing import List, Literal, TypedDict
from .matrices import determinant as det_cofactors

Matrix = List[List[float]]
Method = Literal["cofactors", "sarrus", "lu"]


class DetResult(TypedDict):
    determinant: float
    steps: List[str]


def determinant_sarrus(m: Matrix, steps: List[str]) -> float:
    n = len(m)
    if n != 3 or len(m[0]) != 3:
        raise ValueError("Sarrus solo para matrices 3x3.")

    steps.append("Método de Sarrus para matriz 3×3.")
    steps.append("Matriz original:")
    steps.append(
        "\n".join(
            "[ " + " ".join(f"{v:8.2f}" for v in row) + " ]"
            for row in m
        )
    )

    d1 = m[0][0]*m[1][1]*m[2][2]
    d2 = m[0][1]*m[1][2]*m[2][0]
    d3 = m[0][2]*m[1][0]*m[2][1]

    d4 = m[0][2]*m[1][1]*m[2][0]
    d5 = m[0][0]*m[1][2]*m[2][1]
    d6 = m[0][1]*m[1][0]*m[2][2]

    steps.append(f"d1 = {d1:.4g}, d2 = {d2:.4g}, d3 = {d3:.4g}")
    steps.append(f"d4 = {d4:.4g}, d5 = {d5:.4g}, d6 = {d6:.4g}")

    det = (d1 + d2 + d3) - (d4 + d5 + d6)
    steps.append(f"det = (d1 + d2 + d3) - (d4 + d5 + d6) = {det:.4g}")
    return det


def determinant_cofactors(m: Matrix, method: Method) -> DetResult:
    steps: List[str] = []
    if len(m) == 0 or len(m) != len(m[0]):
        raise ValueError("La matriz debe ser cuadrada.")

    if method == "cofactors":
        steps.append("Determinante por expansión de cofactores.")
        d = det_cofactors(m)
    elif method == "sarrus":
        d = determinant_sarrus(m, steps)
    elif method == "lu":
        steps.append("Método LU (simplificado usando cofactores por ahora).")
        d = det_cofactors(m)
    else:
        raise ValueError("Método de determinante no soportado.")

    steps.append(f"Determinante final: {d:.4g}")
    return {"determinant": d, "steps": steps}
