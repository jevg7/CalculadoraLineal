# core/numerical.py
from __future__ import annotations
from typing import List, Dict, Any


def decompose_base10(num_str: str) -> List[str]:
    num = num_str.strip()
    if not num.isdigit():
        return ["Error: Ingrese solo dígitos numéricos."]

    steps: List[str] = []
    digits = list(reversed(num))
    decomposition: List[str] = []
    values: List[int] = []

    steps.append(f"Descomposición de {num} en base 10:")
    steps.append("")

    for pos, digit in enumerate(digits):
        value = int(digit) * (10 ** pos)
        decomposition.append(f"{digit}×10^{pos}")
        values.append(value)
        steps.append(
            f"Posición {pos}: {digit} × 10^{pos} = {digit} × {10**pos} = {value}"
        )

    steps.append("")
    steps.append(f"Expresión completa: {num} = " + " + ".join(reversed(decomposition)))
    steps.append("")
    rev_values = list(reversed(values))
    steps.append(
        f"Verificación: {' + '.join(str(v) for v in rev_values)} = {sum(values)}"
    )

    return steps


def decompose_base2(bin_str: str) -> List[str]:
    num = bin_str.strip()
    if not all(c in "01" for c in num) or len(num) == 0:
        return ["Error: Ingrese solo dígitos binarios (0 y 1)."]

    steps: List[str] = []
    digits = list(reversed(num))
    decomposition: List[str] = []
    values: List[int] = []

    steps.append(f"Descomposición de {num} en base 2:")
    steps.append("")

    for pos, digit in enumerate(digits):
        value = int(digit) * (2 ** pos)
        decomposition.append(f"{digit}·2^{pos}")
        values.append(value)
        steps.append(
            f"Posición {pos}: {digit} · 2^{pos} = {digit} × {2**pos} = {value}"
        )

    steps.append("")
    steps.append(f"Expresión completa: {num} = " + " + ".join(reversed(decomposition)))
    steps.append("")
    dec_val = sum(values)
    rev_values = list(reversed(values))
    steps.append(
        f"Valor en decimal: {' + '.join(str(v) for v in rev_values)} = {dec_val}"
    )
    steps.append("")
    steps.append(f"Por lo tanto, ({num})₂ = ({dec_val})₁₀")
    return steps


def floating_point_demo() -> Dict[str, Any]:
    a = 0.1
    b = 0.2
    s = a + b
    expected = 0.3

    explanation = (
        "La computadora no puede representar exactamente 0.1, 0.2 y 0.3 en binario.\n\n"
        "Al sumar 0.1 + 0.2, se suman aproximaciones, dando "
        f"{s!r}, que es muy cercano pero no exactamente 0.3.\n\n"
        "Por eso 0.1 + 0.2 === 0.3 es False.\n"
        "Buena práctica: comparar con tolerancia: abs(a - b) < epsilon."
    )

    return {
        "a": a,
        "b": b,
        "sum": s,
        "expected": expected,
        "areEqual": (s == expected),
        "sumString": repr(s),
        "explanation": explanation,
    }
