import math
import sympy as sp
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
    
    steps.append('════════════════════════════════════════════')
    steps.append('       MÉTODO DE BISECCIÓN (DETALLADO)')
    steps.append('════════════════════════════════════════════')
    steps.append(f'Función: f(x) = {expr}')
    steps.append(f'Intervalo inicial: [{a}, {b}]')
    steps.append(f'f({a}) = {fa:.6f}')
    steps.append(f'f({b}) = {fb:.6f}')
    steps.append('')

    if fa * fb > 0:
        steps.append('ERROR: f(a) y f(b) tienen el mismo signo.')
        steps.append('No se cumple el teorema de Bolzano.')
        return StepResult(steps=steps, error="same_sign")
    
    steps.append('Chequeo de signo: f(a) * f(b) < 0 -> OK')
    steps.append('----------------------------------------')

    for k in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = _eval_function(expr, c)
        error = (b - a) / 2.0
        
        steps.append(f"Iteración {k}:")
        steps.append(f"  a={a:.6f}, b={b:.6f}")
        steps.append(f"  Punto medio (c) = ({a:.4f} + {b:.4f}) / 2 = {c:.6f}")
        steps.append(f"  f(c) = {fc:.8f}")
        steps.append(f"  Error est. = {error:.8f}")

        if abs(fc) < tol or error < tol:
            steps.append("")
            steps.append("  ✓ Condición de parada alcanzada (tolerancia)")
            steps.append('════════════════════════════════════════════')
            steps.append(f"  RAÍZ APROX: {c:.8f}")
            return StepResult(steps=steps, vector=[c])

        if fa * fc < 0:
            steps.append("  Signos opuestos entre a y c -> Nuevo intervalo [a, c]")
            b = c
            fb = fc # 
        else:
            steps.append("  Signos opuestos entre c y b -> Nuevo intervalo [c, b]")
            a = c
            fa = fc 
        steps.append("")

    steps.append("AVISO: Máximo de iteraciones alcanzado.")
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
        return StepResult(steps=steps, error="same_sign")

    a_val, b_val = a, b
    c = a_val
    iteration = 0
    c_prev = a_val

    while iteration < max_iter:
        fa = _eval_function(expr, a_val)
        fb = _eval_function(expr, b_val)
        
        # Evitar división por cero si fa == fb (raro pero posible)
        if abs(fb - fa) < 1e-15:
            steps.append("Error: Denominador cercano a cero en interpolación.")
            break

        c = b_val - (fb * (b_val - a_val)) / (fb - fa)
        fc = _eval_function(expr, c)
        error = abs(c - c_prev) if iteration > 0 else abs(b_val - a_val)

        steps.append(f'Iteración {iteration + 1}:')
        steps.append(f'  Intervalo: [{a_val:.5f}, {b_val:.5f}]')
        steps.append(f'  c = {b_val:.5f} - ({fb:.4f}*({b_val:.4f}-{a_val:.4f}))/({fb:.4f}-{fa:.4f})')
        steps.append(f'  c = {c:.6f}, f(c) = {fc:.8f}')
        steps.append(f'  Error = {error:.8f}')

        if abs(fc) < tol or error < tol:
            steps.append('  ✓ Convergencia alcanzada!')
            break

        if fa * fc < 0:
            b_val = c
        else:
            a_val = c
        
        steps.append("")
        c_prev = c
        iteration += 1

    steps.append('═════════════════════════════════════════════')
    steps.append(f'  RAÍZ ENCONTRADA: x ≈ {c:.8f}')
    return StepResult(steps=steps, vector=[c])


def solve_newton_raphson(expr: str, x0: float, tol: float, max_iter: int) -> StepResult:

    steps: list[str] = []
    
    #Configuración de SymPy
    try:
        x_sym = sp.symbols('x')
        
        # Convertir el string a expresión simbólica (ej: "x^2 - 4" -> x**2 - 4)
        # sympify es inteligente y entiende 'sin', 'cos', 'exp', etc.
        f_expr = sp.sympify(expr.replace('^', '**'))
        
        # Calcular la derivada simbólica
        df_expr = sp.diff(f_expr, x_sym)
        
        # Convertir a funciones rápidas de Python para evaluar números
        f_func = sp.lambdify(x_sym, f_expr, modules=['math'])
        df_func = sp.lambdify(x_sym, df_expr, modules=['math'])
        
    except Exception as e:
        return StepResult(steps=[f"Error al calcular la derivada: {e}"], error="parse_error")

    
    steps.append('════════════════════════════════════════════')
    steps.append('    MÉTODO DE NEWTON-RAPHSON (CON SYMPY)')
    steps.append('════════════════════════════════════════════')
    steps.append(f'Función original: f(x) = {expr}')
    steps.append(f'Derivada calculada: f\'(x) = {df_expr}') 
    steps.append(f'Semilla inicial: x0 = {x0}')
    steps.append('')
    steps.append('Fórmula iterativa:')
    steps.append('x(i+1) = x(i) - f(x(i)) / f\'(x(i))')
    steps.append('----------------------------------------')

    x_curr = x0
    
    # 3. Ciclo iterativo
    for i in range(1, max_iter + 1):
        try:
            # Evaluamos usando las funciones compiladas por SymPy
            fx = f_func(x_curr)
            dfx = df_func(x_curr)
        except Exception as e:
            steps.append(f"Error matemático al evaluar (dominio inválido): {str(e)}")
            return StepResult(steps=steps, error="math_error")

        steps.append(f"Iteración {i}:")
        steps.append(f"  x_actual = {x_curr:.8f}")
        steps.append(f"  f(x)     = {fx:.8f}")
        steps.append(f"  f'(x)    = {dfx:.8f}")

        
        if abs(dfx) < 1e-15:
            steps.append("  ERROR CRÍTICO: La derivada es 0 (o muy cercana).")
            steps.append("  No se puede dividir. El método falla (pendiente horizontal).")
            return StepResult(steps=steps, error="zero_derivative")

        
        x_next = x_curr - (fx / dfx)
        error = abs(x_next - x_curr)
        
        steps.append(f"  x_sig    = {x_curr:.6f} - ({fx:.6f} / {dfx:.6f})")
        steps.append(f"           = {x_next:.8f}")
        steps.append(f"  Error    = {error:.8f}")

        
        if error < tol or abs(fx) < tol:
            steps.append("")
            steps.append("  ✓ Convergencia alcanzada")
            steps.append('════════════════════════════════════════════')
            steps.append(f"  RAÍZ APROXIMADA: {x_next:.10f}")
            return StepResult(steps=steps, vector=[x_next])

        x_curr = x_next
        steps.append("")

    steps.append("AVISO: Se alcanzó el número máximo de iteraciones sin converger completamente.")
    return StepResult(steps=steps, vector=[x_curr])


def solve_secant(expr: str, x0: float, x1: float, tol: float, max_iter: int) -> StepResult:
    """
    Resuelve usando el método de la Secante (requiere dos puntos iniciales).
    """
    steps: list[str] = []
    steps.append('════════════════════════════════════════════')
    steps.append('          MÉTODO DE LA SECANTE')
    steps.append('════════════════════════════════════════════')
    steps.append(f'Función f(x) = {expr}')
    steps.append(f'Puntos iniciales: x0={x0}, x1={x1}')
    steps.append('')
    steps.append('Fórmula: x(i+1) = x(i) - [f(x(i))*(x(i)-x(i-1))] / [f(x(i))-f(x(i-1))]')
    steps.append('----------------------------------------')

    x_prev = x0
    x_curr = x1

    fx_prev = _eval_function(expr, x_prev)
    
    for i in range(1, max_iter + 1):
        fx_curr = _eval_function(expr, x_curr)
        
        steps.append(f"Iteración {i}:")
        steps.append(f"  x(i-1) = {x_prev:.6f}, f(x(i-1)) = {fx_prev:.6f}")
        steps.append(f"  x(i)   = {x_curr:.6f}, f(x(i))   = {fx_curr:.6f}")

        denom = fx_curr - fx_prev
        if abs(denom) < 1e-15:
            steps.append("  ERROR: Denominador cero (f(x_i) ≈ f(x_i-1)).")
            return StepResult(steps=steps, error="zero_denominator")

       
        x_next = x_curr - (fx_curr * (x_curr - x_prev)) / denom
        error = abs(x_next - x_curr)

        steps.append(f"  x(i+1) = {x_curr:.6f} - ...")
        steps.append(f"  x(i+1) = {x_next:.8f}")
        steps.append(f"  Error est. = {error:.8f}")

        if error < tol or abs(fx_curr) < tol:
            steps.append("")
            steps.append("  ✓ Convergencia alcanzada")
            steps.append('════════════════════════════════════════════')
            steps.append(f"  RAÍZ: {x_next:.8f}")
            return StepResult(steps=steps, vector=[x_next])

        
        x_prev = x_curr
        fx_prev = fx_curr
        x_curr = x_next
        steps.append("")

    steps.append("AVISO: No convergió en el máximo de iteraciones.")
    return StepResult(steps=steps, vector=[x_curr])