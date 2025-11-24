import math
from typing import Dict, Callable
from .common import StepResult


def decompose_base10(num_str: str) -> StepResult:
    num_str = num_str.strip()
    if not num_str.isdigit():
        return StepResult(steps=["Error: ingrese solo dígitos (base 10)"], error="invalid")
    steps: list[str] = []
    digits = list(reversed(num_str))
    decomposition = []
    values = []
    for pos, d in enumerate(digits):
        value = int(d) * (10 ** pos)
        decomposition.append(f"{d}×10^{pos}")
        values.append(value)
        steps.append(f"Posición {pos}: {d}×10^{pos} = {value}")
    steps.append("")
    steps.append(f"{num_str} = " + " + ".join(reversed(decomposition)))
    steps.append(" = " + " + ".join(map(str, reversed(values))) + f" = {sum(values)}")
    return StepResult(steps=steps)


def decompose_base2(num_str: str) -> StepResult:
    num_str = num_str.strip()
    if not num_str or any(c not in "01" for c in num_str):
        return StepResult(steps=["Error: ingrese solo 0 y 1"], error="invalid")
    steps: list[str] = []
    digits = list(reversed(num_str))
    values = []
    for pos, d in enumerate(digits):
        value = int(d) * (2 ** pos)
        values.append(value)
        steps.append(f"Posición {pos}: {d}·2^{pos} = {value}")
    decimal_value = sum(values)
    steps.append("")
    steps.append(f"{num_str}₂ = {decimal_value}₁₀")
    return StepResult(steps=steps, vector=[decimal_value])


def demonstrate_roundoff(value: float, n: int) -> StepResult:
    if n < 1 or n > 100:
        return StepResult(steps=["n debe estar entre 1 y 100"], error="invalid_n")
    steps: list[str] = []
    s = 0.0
    for i in range(1, n + 1):
        s += value
        expected = i * value
        err = abs(s - expected)
        steps.append(f"Iteración {i}: suma={s}, esperado={expected}, error={err:e}")
    return StepResult(steps=steps)


def demonstrate_truncation(x: float, max_terms: int) -> StepResult:
    if max_terms < 1 or max_terms > 50:
        return StepResult(steps=["términos fuera de rango"], error="invalid_terms")
    steps: list[str] = []
    exact = math.exp(x)
    approx = 0.0
    fact = 1.0
    for n in range(0, max_terms + 1):
        if n > 0:
            fact *= n
        term = (x ** n) / fact
        approx += term
        err = abs(exact - approx)
        rel = err / exact * 100
        steps.append(
            f"n={n}: término={term:.10f}, aprox={approx:.10f}, "
            f"error={err:e}, error_rel={rel:.6f}%"
        )
    return StepResult(steps=steps)


def demonstrate_propagation(a: float, b: float) -> StepResult:
    steps: list[str] = []
    s1 = a + b
    s2 = a - (a - b)
    steps.append(f"a + b = {s1}")
    steps.append(f"a - (a - b) = {s2} (debería ~ {b})")
    if b != 0:
        s3 = (a / b) * b
        steps.append(f"(a / b) · b = {s3} (debería ~ {a})")
    return StepResult(steps=steps)


def _eval_function(expr: str, x: float) -> float:
    allowed: Dict[str, Callable[..., float]] = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
    }
    env = {"x": x, **allowed, "__builtins__": {}}
    expr = expr.replace("^", "**")
    return eval(expr, env)  # en producción usar parser seguro


def solve_bisection(expr: str, a: float, b: float, tol: float, max_iter: int) -> StepResult:
    steps: list[str] = []
    fa = _eval_function(expr, a)
    fb = _eval_function(expr, b)
    steps.append(f"f(x) = {expr}")
    steps.append(f"[a,b] = [{a},{b}], f(a)={fa}, f(b)={fb}")
    if fa * fb > 0:
        steps.append("f(a) y f(b) tienen el mismo signo → no se garantiza raíz")
        return StepResult(steps=steps, error="same_sign")
    for k in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = _eval_function(expr, c)
        steps.append(f"Iteración {k}: c={c}, f(c)={fc}")
        if abs(fc) < tol or (b - a) / 2.0 < tol:
            steps.append("Condición de paro alcanzada")
            return StepResult(steps=steps, vector=[c])
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    steps.append("Máx. iteraciones alcanzado")
    return StepResult(steps=steps, vector=[(a + b) / 2.0])

def solve_false_position(expr: str, a: float, b: float, tol: float, max_iter: int) -> StepResult:
    steps: list[str] = []

    fa = _eval_function(expr, a)
    fb = _eval_function(expr, b)

    steps.append('════════════════════════════════════════════')
    steps.append('   MÉTODO DE REGLA FALSA (FALSE POSITION)')
    steps.append('════════════════════════════════════════════')
    steps.append('')
    steps.append(f'Función: f(x) = {expr}')
    steps.append(f'Intervalo: [{a}, {b}]')
    steps.append(f'Tolerancia: {tol}')
    steps.append(f'Iteraciones máximas: {max_iter}')
    steps.append('')
    steps.append(f'f({a}) = {fa:.6f}')
    steps.append(f'f({b}) = {fb:.6f}')
    steps.append('')

    if fa * fb > 0:
        steps.append('ERROR: f(a) y f(b) deben tener signos opuestos')
        steps.append('No se puede garantizar una raíz en este intervalo.')
        return StepResult(steps=steps, error="same_sign")

    steps.append('Condición verificada: f(a) × f(b) < 0 ✓')
    steps.append('Existe al menos una raíz en el intervalo.')
    steps.append('')
    steps.append('Fórmula de interpolación lineal:')
    steps.append('c = b - f(b) × (b - a) / (f(b) - f(a))')
    steps.append('')
    steps.append('─────────────────────────────────────────────')
    steps.append('')

    a_val = a
    b_val = b
    c_prev = a_val
    c = a_val
    fc = fa
    iteration = 0

    while iteration < max_iter:
        fa = _eval_function(expr, a_val)
        fb = _eval_function(expr, b_val)

        # Fórmula de regla falsa
        c = b_val - (fb * (b_val - a_val)) / (fb - fa)
        fc = _eval_function(expr, c)

        error = abs(c - c_prev) if iteration > 0 else abs(b_val - a_val)

        steps.append(f'Iteración {iteration + 1}:')
        steps.append(f'  a = {a_val:.6f}, f(a) = {fa:.6f}')
        steps.append(f'  b = {b_val:.6f}, f(b) = {fb:.6f}')
        steps.append(f'  c = {c:.6f}')
        steps.append(f'  f(c) = {fc:.6f}')
        steps.append(f'  Error = {error:.6f}')

        if abs(fc) < tol or error < tol:
            steps.append('  ✓ Convergencia alcanzada!')
            steps.append('')
            break

        if fa * fc < 0:
            b_val = c
            steps.append(f'  Nueva búsqueda: [{a_val:.6f}, {c:.6f}]')
        else:
            a_val = c
            steps.append(f'  Nueva búsqueda: [{c:.6f}, {b_val:.6f}]')
        steps.append('')

        c_prev = c
        iteration += 1

    steps.append('═════════════════════════════════════════════')
    steps.append(f'  RAÍZ ENCONTRADA: x ≈ {c:.8f}')
    steps.append(f'  f({c:.8f}) = {fc:.10f}')
    steps.append(f'  Iteraciones: {iteration + 1}')
    steps.append('═════════════════════════════════════════════')
    steps.append('')
    steps.append('Ventaja sobre bisección:')
    steps.append('La regla falsa usa interpolación lineal, lo que')
    steps.append('generalmente converge más rápido que bisección.')

    return StepResult(steps=steps, vector=[c])