# core.py
# Lógica optimizada usando numpy — compatible con la GUI original (mismos nombres/métodos).
# Mantiene logs paso-a-paso y comprobaciones tal como en tu jjj.py original.

from typing import List, Tuple
import numpy as np
import sys

EPS = 1e-12

def _fmt_row(row: np.ndarray) -> str:
    return "  ".join(f"{float(x):.4f}" for x in row)

def _fmt_matrix(mat: np.ndarray) -> str:
    return "\n".join(_fmt_row(mat[i, :]) for i in range(mat.shape[0]))


# ============================
# Núcleo de cálculo (modelo)
# ============================
class SistemaLineal:
    def __init__(self, matriz_aumentada: List[List[float]]):
        # Guardamos una copia como numpy array (float) para operaciones internas.
        self.matriz = np.array([row[:] for row in matriz_aumentada], dtype=float) if matriz_aumentada else np.array([[]], dtype=float)
        # homogéneo si todos los términos independientes (última columna) son ~0
        if self.matriz.size == 0:
            self.homogeneo = True
        else:
            self.homogeneo = bool(np.all(np.abs(self.matriz[:, -1]) < EPS))

    def _imprimir_matriz(self, paso: int, operacion: str) -> str:
        texto = f"Paso {paso} ({operacion}):\n"
        # formateamos cada fila a 4 decimales como en original
        for fila in self.matriz:
            texto += "  ".join(f"{valor:.4f}" for valor in fila) + "\n"
        return texto + "\n"

    def eliminacion_gaussiana(self) -> str:
        """Gauss-Jordan completo con logs e interpretación final (compatibilidad con jjj.py)."""
        return self._gauss_jordan(log_interpretar=True)

    def eliminacion_gaussiana_solo_pasos(self) -> str:
        """Gauss-Jordan devolviendo solo los pasos (sin interpretación)."""
        return self._gauss_jordan(log_interpretar=False)

    def _gauss_jordan(self, log_interpretar: bool) -> str:
        if self.matriz.size == 0 or self.matriz.shape[1] == 0:
            return "Matriz no válida."

        A = self.matriz  # view to work with
        m, n_tot = A.shape
        n_vars = n_tot - 1

        paso = 1
        log = ""
        fila_actual = 0

        # Iterar columnas de variables
        for col in range(n_vars):
            if fila_actual >= m:
                break

            # pivoteo parcial: fila con max abs en esta columna desde fila_actual
            subcol = np.abs(A[fila_actual:, col])
            if subcol.size == 0:
                break
            max_rel_idx = np.argmax(subcol) + fila_actual
            if abs(A[max_rel_idx, col]) < EPS:
                # no pivot en esta columna
                continue

            # intercambio si necesario
            if fila_actual != max_rel_idx:
                A[[fila_actual, max_rel_idx], :] = A[[max_rel_idx, fila_actual], :]
                log += self._imprimir_matriz(paso, f"Intercambio f{fila_actual + 1} ↔ f{max_rel_idx + 1}")
                paso += 1

            pivote = A[fila_actual, col]
            if abs(pivote) > EPS:
                # normalizar fila de pivote
                A[fila_actual, :] = A[fila_actual, :] / pivote
                log += self._imprimir_matriz(paso, f"f{fila_actual + 1} ← (1/{pivote:.4f}) · f{fila_actual + 1}")
                paso += 1

            # eliminar en forma vectorizada: hacer cero columna 'col' en todas las otras filas
            factors = A[:, col].copy()
            mask = (np.arange(m) != fila_actual) & (np.abs(factors) > EPS)
            if np.any(mask):
                # A[mask, :] -= factors[mask, None] * A[fila_actual, None, :]
                A[mask, :] = A[mask, :] - factors[mask, None] * A[fila_actual, None, :]
                # Para mantener log estilo original: un paso por fila modificada
                for i in np.nonzero(mask)[0]:
                    factor = factors[i]
                    log += self._imprimir_matriz(paso, f"f{i + 1} ← f{i + 1} − ({factor:.4f}) · f{fila_actual + 1}")
                    paso += 1

            fila_actual += 1

        if log_interpretar:
            log += self._interpretar_resultado()
        else:
            # si solo pasos, actualizamos la matriz interna
            self.matriz = A

        return log

    def _interpretar_resultado(self) -> str:
        """Interpretación tipo jjj.py: pivotes, libres, inconsistencia, homogeneidad, columnas pivote."""
        if self.matriz.size == 0:
            return "Matriz vacía."

        m, n_tot = self.matriz.shape
        n = n_tot - 1  # número de variables
        resultado = "Solución del sistema:\n"

        # detectar pivotes: buscamos leading 1 por fila (RREF parcial)
        pivotes = [-1] * n
        columnas_pivote = []
        filas_marcadas = set()

        for i in range(m):
            row = self.matriz[i, :n]
            nz = np.where(np.abs(row) > 1e-10)[0]
            if nz.size == 0:
                continue
            j_lead = int(nz[0])
            es_uno = abs(self.matriz[i, j_lead] - 1) < 1e-10
            columna_ceros_fuera = np.all(np.abs(self.matriz[np.arange(m) != i, j_lead]) < 1e-10)
            izquierda_ceros = np.all(np.abs(row[:j_lead]) < 1e-10)
            if es_uno and columna_ceros_fuera and izquierda_ceros and j_lead not in filas_marcadas:
                pivotes[j_lead] = i
                columnas_pivote.append(j_lead + 1)  # 1-based
                filas_marcadas.add(j_lead)

        # filas inconsistentes: 0 ... 0 | b != 0
        filas_inconsistentes = [i for i in range(m) if np.all(np.abs(self.matriz[i, :n]) < 1e-10) and abs(self.matriz[i, -1]) > 1e-10]
        inconsistente_var = {f"x{i + 1}" for i in filas_inconsistentes}

        soluciones = {}
        soluciones_numericas = {}

        for j in range(n):
            var_name = f"x{j + 1}"
            if var_name in inconsistente_var:
                soluciones[var_name] = f"{var_name} es inconsistente"
            elif pivotes[j] == -1:
                soluciones[var_name] = f"{var_name} es libre"
            else:
                fila = pivotes[j]
                constante = self.matriz[fila, -1]
                terminos = []
                for k in range(n):
                    if k != j and pivotes[k] == -1 and abs(self.matriz[fila, k]) > 1e-10:
                        coef = -self.matriz[fila, k]
                        coef_str = (f"{int(coef)}" if float(coef).is_integer() else f"{coef:.4f}")
                        terminos.append(f"{'+' if coef >= 0 else ''}{coef_str}x{k + 1}")
                const_str = (f"{int(constante)}" if float(constante).is_integer() else f"{constante:.4f}")
                if const_str == "0" and not terminos:
                    ecuacion = "0"
                else:
                    ecuacion = (const_str if const_str != "0" else "")
                    if terminos:
                        ecuacion = (ecuacion + " " if ecuacion else "") + " ".join(terminos).lstrip("+ ").strip()
                soluciones[var_name] = f"{var_name} = {ecuacion}".strip()
                if not terminos:
                    soluciones_numericas[var_name] = constante

        # agregar soluciones al resultado
        for j in range(n):
            var_name = f"x{j + 1}"
            if var_name in soluciones:
                resultado += f"{soluciones[var_name]}\n"

        rankA = len(columnas_pivote)
        hay_libres = any(p == -1 for p in pivotes)

        if filas_inconsistentes:
            resultado += "\nEl sistema es inconsistente y no tiene soluciones.\n"
        else:
            if self.homogeneo:
                if hay_libres:
                    resultado += (
                        f"\nSistema homogéneo: hay variables libres ⇒ hay infinitas soluciones (incluye la trivial x = 0).\n"
                        f"Diagnóstico: rango(A) = {rankA} < n = {n}. "
                        f"No hay pivote en todas las columnas (no se logra RREF con pivote por columna). "
                        f"⇒ La solución trivial **no es la única**.\n"
                    )
                else:
                    resultado += "\nSistema homogéneo: la solución es única y trivial (x = 0).\n"
            else:
                if hay_libres:
                    resultado += "\nHay infinitas soluciones debido a variables libres.\n"
                else:
                    if len(soluciones_numericas) == n and all(abs(val) < 1e-10 for val in soluciones_numericas.values()):
                        resultado += "\nSolución trivial.\n"
                    else:
                        resultado += "\nLa solución es única.\n"

        resultado += f"\nLas columnas pivote son: {', '.join(map(str, columnas_pivote)) or '—'}.\n"
        return resultado

    def columnas_pivote(self, num_vars: int) -> List[int]:
        """Devuelve las columnas pivote (1-based) entre las primeras num_vars columnas."""
        if self.matriz.size == 0:
            return []
        m, n_tot = self.matriz.shape
        m_vars = min(num_vars, n_tot - 1)
        cols = []
        for i in range(m):
            row = self.matriz[i, :m_vars]
            nz = np.where(np.abs(row) > 1e-10)[0]
            if nz.size == 0:
                continue
            lead = int(nz[0])
            if (abs(self.matriz[i, lead] - 1) < 1e-10 and np.all(np.abs(self.matriz[np.arange(m) != i, lead]) < 1e-10)):
                cols.append(lead + 1)
        return cols


# ============================
# Clases para Vectores
# ============================
class Vector:
    def __init__(self, componentes: List[float]):
        self.arr = np.array(componentes, dtype=float).copy()
        self.dimension = self.arr.size

    def __str__(self) -> str:
        return f"({', '.join(f'{float(x):.4f}' for x in self.arr)})"

    def __add__(self, other: 'Vector') -> 'Vector':
        if self.dimension != other.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión")
        return Vector((self.arr + other.arr).tolist())

    def __sub__(self, other: 'Vector') -> 'Vector':
        if self.dimension != other.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión")
        return Vector((self.arr - other.arr).tolist())

    def __mul__(self, escalar: float) -> 'Vector':
        return Vector((self.arr * escalar).tolist())

    def __rmul__(self, escalar: float) -> 'Vector':
        return self.__mul__(escalar)

    def producto_punto(self, other: 'Vector') -> float:
        if self.dimension != other.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión")
        return float(np.dot(self.arr, other.arr))

    def norma(self) -> float:
        return float(np.linalg.norm(self.arr))

    def es_cero(self) -> bool:
        return bool(np.all(np.abs(self.arr) < 1e-10))

    def opuesto(self) -> 'Vector':
        return Vector((-self.arr).tolist())


class OperacionesVectoriales:
    @staticmethod
    def verificar_propiedades_espacio_vectorial(vectores: List[Vector]) -> str:
        """Verifica las propiedades del espacio vectorial ℝⁿ manteniendo logs similares al original."""
        if not vectores:
            return "No hay vectores para verificar."

        resultado = "=== Verificación de Propiedades del Espacio Vectorial ℝⁿ ===\n\n"
        dim = vectores[0].dimension
        for v in vectores[1:]:
            if v.dimension != dim:
                return f"Error: Los vectores tienen dimensiones diferentes ({dim} vs {v.dimension})"
        resultado += f"Dimensión del espacio: ℝ^{dim}\n"
        resultado += f"Número de vectores: {len(vectores)}\n\n"

        # 1. Conmutativa
        if len(vectores) >= 2:
            v1, v2 = vectores[0], vectores[1]
            suma1 = v1 + v2
            suma2 = v2 + v1
            resultado += f"1. Conmutativa (v₁ + v₂ = v₂ + v₁):\n"
            resultado += f"    v₁ + v₂ = {suma1}\n"
            resultado += f"    v₂ + v₁ = {suma2}\n"
            resultado += f"    ✓ Cumple: {np.allclose(suma1.arr, suma2.arr)}\n\n"

        # 2. Asociativa
        if len(vectores) >= 3:
            v1, v2, v3 = vectores[0], vectores[1], vectores[2]
            suma1 = (v1 + v2) + v3
            suma2 = v1 + (v2 + v3)
            resultado += f"2. Asociativa ((v₁ + v₂) + v₃ = v₁ + (v₂ + v₃)):\n"
            resultado += f"    (v₁ + v₂) + v₃ = {suma1}\n"
            resultado += f"    v₁ + (v₂ + v₃) = {suma2}\n"
            resultado += f"    ✓ Cumple: {np.allclose(suma1.arr, suma2.arr)}\n\n"

        # 3. Vector cero y 4. opuesto
        vector_cero = Vector([0.0] * dim)
        resultado += f"3. Vector cero: {vector_cero}\n"
        resultado += f"    ✓ Existe el vector cero\n\n"

        if vectores:
            v = vectores[0]
            opuesto = v.opuesto()
            suma_cero = v + opuesto
            resultado += f"4. Vector opuesto para v₁ = {v}:\n"
            resultado += f"    -v₁ = {opuesto}\n"
            resultado += f"    v₁ + (-v₁) = {suma_cero}\n"
            resultado += f"    ✓ Es vector cero: {suma_cero.es_cero()}\n\n"

        # 5. Propiedades escalares
        if vectores:
            v = vectores[0]
            a, b = 2.0, 3.0
            prop1 = (a + b) * v
            prop2 = a * v + b * v
            prop3 = a * (b * v)
            prop4 = (a * b) * v
            resultado += f"5. Propiedades de multiplicación por escalar:\n"
            resultado += f"    (α + β)v = αv + βv: ✓ {np.allclose(prop1.arr, prop2.arr)}\n"
            resultado += f"    α(βv) = (αβ)v: ✓ {np.allclose(prop3.arr, prop4.arr)}\n"
        return resultado

    @staticmethod
    def combinacion_lineal(vectores: List[Vector], vector_objetivo: Vector) -> str:
        """Determina si vector_objetivo es combinación lineal de los vectores (con logs)."""
        if not vectores:
            return "No hay vectores para la combinación lineal."

        resultado = "=== Combinación Lineal de Vectores ===\n\n"
        resultado += f"Vectores dados: {len(vectores)}\n"
        for i, v in enumerate(vectores):
            resultado += f"v{i+1} = {v}\n"
        resultado += f"\nVector objetivo: {vector_objetivo}\n\n"

        dim = vectores[0].dimension
        for v in vectores + [vector_objetivo]:
            if v.dimension != dim:
                return "Error: Los vectores tienen dimensiones diferentes"

        resultado += "Planteo del sistema:\n"
        resultado += f"c₁v₁ + c₂v₂ + ... + c{len(vectores)}v{len(vectores)} = b\n\n"

        # construir matriz aumentada (n filas, k+1 cols)
        matriz_aumentada = []
        for i in range(dim):
            fila = [v.componentes[i] if isinstance(v, Vector) else float(v) for v in vectores]
            # ABOVE: vectores are Vector objects; ensure we get floats
            # simpler: use the .arr values
        # Build using numpy for clarity
        M = np.column_stack([v.arr for v in vectores])  # shape (dim, k)
        b = vector_objetivo.arr.reshape(-1, 1)  # shape (dim,1)
        aug = np.hstack([M, b])  # shape (dim, k+1)
        # log matriz aumentada
        resultado += "Matriz aumentada del sistema:\n"
        for i in range(aug.shape[0]):
            resultado += f"Fila {i+1}: {'  '.join(f'{x:8.4f}' for x in aug[i, :])}\n"
        resultado += "\n"
        # resolver con SistemaLineal (reutilizamos la clase con lista de listas)
        sistema = SistemaLineal(aug.tolist())
        resultado += sistema.eliminacion_gaussiana()
        return resultado

    @staticmethod
    def ecuacion_vectorial(vectores: List[Vector], vector_objetivo: Vector) -> str:
        if not vectores:
            return "No hay vectores para la ecuación."
        resultado = "=== Ecuación Vectorial ===\n\n"
        resultado += f"Ecuación: c₁v₁ + c₂v₂ + ... = b\n\n"
        for i, v in enumerate(vectores):
            resultado += f"v{i+1} = {v}\n"
        resultado += f"b = {vector_objetivo}\n\n"
        return resultado + OperacionesVectoriales.combinacion_lineal(vectores, vector_objetivo)

    @staticmethod
    def dependencia_independencia(vectores: List['Vector']) -> str:
        """Usa SistemaLineal para mostrar pasos y concluir independencia/dependencia."""
        if not vectores:
            return "No hay vectores para verificar independencia."

        n = vectores[0].dimension
        for v in vectores:
            if v.dimension != n:
                return "Error: los vectores tienen dimensiones diferentes."

        k = len(vectores)
        if k == 1:
            return ("=== Verificación de Independencia Lineal ===\n\n"
                    f"Conjunto de 1 vector en ℝ^{n}.\n"
                    f"{'Independiente (no es vector cero).' if not vectores[0].es_cero() else 'Dependiente (vector cero).'}\n")
        if k > n:
            return ("=== Verificación de Independencia Lineal ===\n\n"
                    f"n = {n}, k = {k} > n ⇒ Dependiente.\n"
                    "Motivo: hay más vectores que la dimensión del espacio.\n")

        # construir M (n x k) con vectores como columnas
        M = np.column_stack([v.arr for v in vectores])  # shape (n, k)
        # construir aumentada [M | 0]
        aug = np.hstack([M, np.zeros((n, 1))])
        header = "=== Verificación de Independencia Lineal (usando pasos de Gauss del módulo de sistemas) ===\n\n"
        header += "Matriz inicial [M | 0] (vectores como columnas y columna derecha nula):\n"
        header += "\n".join("  ".join(f"{x:8.4f}" for x in row) for row in aug) + "\n\n"
        sistema = SistemaLineal(aug.tolist())
        pasos = sistema.eliminacion_gaussiana_solo_pasos()
        cols_pivote = sistema.columnas_pivote(k)
        rango = len(cols_pivote)
        out = [header, pasos]
        out.append("=== Conclusión ===\n")
        out.append(f"Dimensión del espacio: ℝ^{n}\n")
        out.append(f"Número de vectores (k): {k}\n")
        out.append(f"Rango (por pasos de Gauss): {rango}\n")
        out.append(f"Columnas pivote (en los vectores): {', '.join(map(str, cols_pivote)) if cols_pivote else '—'}\n\n")
        if rango == k:
            out.append("r = k ⇒ Conjunto **INDEPENDIENTE**.\n"
                       "El sistema homogéneo M·c = 0 solo admite la solución trivial c = 0.\n")
        else:
            libres = k - rango
            out.append("r < k ⇒ Conjunto **DEPENDIENTE**.\n"
                       f"Hay {libres} variable(s) libre(s); existen soluciones no triviales c ≠ 0 con M·c = 0.\n")
        return "".join(out)


# ============================
# Clases para Matrices
# ============================
class Matriz:
    def __init__(self, filas: List[List[float]]):
        # almacenamos como numpy array internamente para operaciones
        self.filas = np.array([row[:] for row in filas], dtype=float) if filas else np.zeros((0, 0), dtype=float)
        self.m, self.n = self.filas.shape if self.filas.size else (0, 0)

    def __str__(self) -> str:
        if self.m == 0 or self.n == 0:
            return ""
        return "\n".join("  ".join(f"{float(x):8.4f}" for x in row) for row in self.filas)

    def __add__(self, other: 'Matriz') -> 'Matriz':
        if (self.m, self.n) != (other.m, other.n):
            raise ValueError(f"Las matrices deben tener las mismas dimensiones para sumar ({self.m}×{self.n} y {other.m}×{other.n})")
        res = self.filas + other.filas
        return Matriz(res.tolist())

    def __sub__(self, other: 'Matriz') -> 'Matriz':
        if (self.m, self.n) != (other.m, other.n):
            raise ValueError(f"Las matrices deben tener las mismas dimensiones para restar ({self.m}×{self.n} y {other.m}×{other.n})")
        res = self.filas - other.filas
        return Matriz(res.tolist())

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Matriz((self.filas * float(other)).tolist())
        if isinstance(other, Matriz):
            if self.n != other.m:
                raise ValueError(f"No se pueden multiplicar matrices {self.m}×{self.n} y {other.m}×{other.n}")
            prod = self.filas.dot(other.filas)
            return Matriz(prod.tolist())
        raise TypeError(f"La multiplicación no está definida para Matriz y {type(other)}")

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        raise TypeError(f"La multiplicación no está definida para {type(other)} y Matriz")

    def transpuesta(self) -> 'Matriz':
        return Matriz(self.filas.T.tolist())

    def es_cuadrada(self) -> bool:
        return self.m == self.n

    def es_identidad(self) -> bool:
        if not self.es_cuadrada():
            return False
        I = np.eye(self.m)
        return bool(np.allclose(self.filas, I, atol=1e-10))


class OperacionesMatriciales:
    @staticmethod
    def ecuacion_matricial(matriz_a: Matriz, matriz_b: Matriz) -> str:
        resultado = "=== Ecuación Matricial AX = B ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"

        if matriz_a.n != matriz_b.m:
            return resultado + f"Error: No se puede resolver AX = B.\nEl número de columnas de A ({matriz_a.n}) debe ser igual al número de filas de B ({matriz_b.m}).\n"

        resultado += "Planteo del sistema:\nPara cada columna j de B, resolver Axⱼ = bⱼ\n\n"

        for j in range(matriz_b.n):
            resultado += f"--- Columna {j+1} de B ---\n"
            aug = np.hstack([matriz_a.filas, matriz_b.filas[:, [j]]])
            resultado += f"Sistema Ax{j+1} = b{j+1}:\n"
            for i in range(aug.shape[0]):
                resultado += f"Fila {i+1}: {'  '.join(f'{x:8.4f}' for x in aug[i, :])}\n"
            resultado += "\n"
            sistema = SistemaLineal(aug.tolist())
            resultado += sistema.eliminacion_gaussiana()
            resultado += "\n" + "="*50 + "\n\n"

        return resultado

    @staticmethod
    def multiplicacion_matrices(matriz_a: Matriz, matriz_b: Matriz) -> str:
        resultado = "=== Multiplicación de Matrices A * B ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"

        try:
            producto = matriz_a * matriz_b
            resultado += f"Resultado A * B ({producto.m}×{producto.n}):\n{producto}\n\n"
            resultado += "Procedimiento paso a paso:\n"
            A = matriz_a.filas; B = matriz_b.filas
            for i in range(producto.m):
                for j in range(producto.n):
                    terminos = [f"({A[i,k]:.4f} × {B[k,j]:.4f})" for k in range(matriz_a.n)]
                    resultado += f"C[{i+1},{j+1}] = {' + '.join(terminos)} = {float(producto.filas[i,j]):.4f}\n"
        except ValueError as e:
            resultado += f"Error: {e}\n"
        return resultado

    @staticmethod
    def suma_matrices(matriz_a: Matriz, matriz_b: Matriz) -> str:
        resultado_str = "=== Suma de Matrices A + B ===\n\n"
        resultado_str += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado_str += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"
        try:
            suma = matriz_a + matriz_b
            resultado_str += f"Resultado A + B ({suma.m}×{suma.n}):\n{suma}\n\n"
            resultado_str += "Procedimiento paso a paso (C[i,j] = A[i,j] + B[i,j]):\n"
            for i in range(suma.m):
                for j in range(suma.n):
                    a_val = matriz_a.filas[i,j]
                    b_val = matriz_b.filas[i,j]
                    c_val = suma.filas[i,j]
                    resultado_str += f"C[{i+1},{j+1}] = {a_val:.4f} + {b_val:.4f} = {c_val:.4f}\n"
        except ValueError as e:
            resultado_str += f"Error: {e}\n"
        return resultado_str

    @staticmethod
    def resta_matrices(matriz_a: Matriz, matriz_b: Matriz) -> str:
        resultado_str = "=== Resta de Matrices A - B ===\n\n"
        resultado_str += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado_str += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"
        try:
            resta = matriz_a - matriz_b
            resultado_str += f"Resultado A - B ({resta.m}×{resta.n}):\n{resta}\n\n"
            resultado_str += "Procedimiento paso a paso (C[i,j] = A[i,j] - B[i,j]):\n"
            for i in range(resta.m):
                for j in range(resta.n):
                    a_val = matriz_a.filas[i,j]
                    b_val = matriz_b.filas[i,j]
                    c_val = resta.filas[i,j]
                    resultado_str += f"C[{i+1},{j+1}] = {a_val:.4f} - {b_val:.4f} = {c_val:.4f}\n"
        except ValueError as e:
            resultado_str += f"Error: {e}\n"
        return resultado_str

    @staticmethod
    def multiplicacion_por_escalar(matriz_a: Matriz, escalar: float) -> str:
        resultado_str = f"=== Multiplicación de Matriz por Escalar ({escalar:.4f}) * A ===\n\n"
        resultado_str += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        producto = matriz_a * escalar
        resultado_str += f"Resultado ({escalar:.4f}) * A ({producto.m}×{producto.n}):\n{producto}\n\n"
        resultado_str += f"Procedimiento paso a paso (C[i,j] = {escalar:.4f} * A[i,j]):\n"
        for i in range(producto.m):
            for j in range(producto.n):
                a_val = matriz_a.filas[i,j]
                c_val = producto.filas[i,j]
                resultado_str += f"C[{i+1},{j+1}] = {escalar:.4f} * {a_val:.4f} = {c_val:.4f}\n"
        return resultado_str

    @staticmethod
    def matriz_traspuesta(matriz_a: Matriz) -> str:
        resultado_str = "=== Matriz Traspuesta Aᵀ ===\n\n"
        resultado_str += f"Matriz Original A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        traspuesta = matriz_a.transpuesta()
        resultado_str += f"Matriz Traspuesta Aᵀ ({traspuesta.m}×{traspuesta.n}):\n{traspuesta}\n\n"
        resultado_str += "Procedimiento (Aᵀ[i,j] = A[j,i]):\n"
        resultado_str += "Se intercambian las filas por las columnas.\n"
        for i in range(traspuesta.m):
            resultado_str += f"Nueva Fila {i+1} = Antigua Columna {i+1}\n"
        resultado_str += "\nPropiedades teóricas (para referencia):\n"
        resultado_str += "1. (Aᵀ)ᵀ = A\n2. (A + B)ᵀ = Aᵀ + Bᵀ\n3. (kA)ᵀ = k(Aᵀ)\n4. (AB)ᵀ = Bᵀ * Aᵀ\n"
        return resultado_str

    @staticmethod
    def verificar_propiedad_suma_traspuesta(matriz_a: Matriz, matriz_b: Matriz) -> str:
        resultado = "=== Verificación de Propiedad: (A+B)ᵀ = Aᵀ + Bᵀ ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"
        try:
            resultado += "--- Cálculo del Lado Izquierdo: (A + B)ᵀ ---\n"
            suma_ab = matriz_a + matriz_b
            resultado += f"1. Calcular A + B:\n{suma_ab}\n\n"
            lhs = suma_ab.transpuesta()
            resultado += f"2. Transponer el resultado (A + B)ᵀ:\n{lhs}\n\n"
            resultado += "--- Cálculo del Lado Derecho: Aᵀ + Bᵀ ---\n"
            a_t = matriz_a.transpuesta()
            resultado += f"1. Calcular Aᵀ:\n{a_t}\n\n"
            b_t = matriz_b.transpuesta()
            resultado += f"2. Calcular Bᵀ:\n{b_t}\n\n"
            rhs = a_t + b_t
            resultado += f"3. Sumar Aᵀ + Bᵀ:\n{rhs}\n\n"
            resultado += "--- Conclusión ---\n"
            resultado += f"Lado Izquierdo:\n{lhs}\n\nLado Derecho:\n{rhs}\n\n"
            son_iguales = np.allclose(lhs.filas, rhs.filas, atol=1e-10)
            if son_iguales:
                resultado += "✓ Los resultados son iguales. La propiedad (A+B)ᵀ = Aᵀ + Bᵀ se cumple.\n"
            else:
                resultado += "✗ Los resultados NO son iguales. La propiedad no se cumple (revisar cálculo).\n"
        except ValueError as e:
            resultado += f"Error: No se puede verificar la propiedad.\n{e}\n"
        return resultado

    # ---- Helpers y métodos avanzados (inversa, determinantes) ----

    @staticmethod
    def _imprimir_matriz_aug(matriz: List[List[float]], paso: int, operacion: str, n_split: int) -> str:
        texto = f"Paso {paso} ({operacion}):\n"
        for fila in matriz:
            parte_a = "  ".join(f"{valor:8.4f}" for valor in fila[:n_split])
            parte_i = "  ".join(f"{valor:8.4f}" for valor in fila[n_split:])
            texto += f"  [ {parte_a} | {parte_i} ]\n"
        return texto + "\n"

    @staticmethod
    def _verificar_propiedades_invertibilidad(n: int, num_pivotes: int) -> str:
        resultado = "\n=== Verificación de Propiedades Teóricas ===\n"
        if num_pivotes == n:
            resultado += f"(c) La matriz A ({n}x{n}) tiene {num_pivotes} posiciones pivote.\n"
            resultado += "    Interpretación: Si A tiene n pivotes, entonces A es invertible. (Cumple)\n\n"
            resultado += "(d) La ecuación Ax=0 tiene solamente la solución trivial.\n"
            resultado += "    Interpretación: Dado que hay n pivotes, no hay variables libres. Si Ax=0 solo tiene la solución trivial, entonces A⁻¹ existe. (Cumple)\n\n"
            resultado += "(e) Las columnas de A forman un conjunto linealmente independiente.\n"
            resultado += "    Interpretación: Dado que hay n pivotes, las columnas son linealmente independientes, entonces A es una matriz invertible. (Cumple)\n"
        else:
            resultado += f"(c) La matriz A ({n}x{n}) tiene {num_pivotes} posiciones pivote (se esperaban {n}).\n"
            resultado += "    Interpretación: A no tiene n pivotes, por lo tanto, A NO es invertible. (No cumple)\n\n"
            resultado += "(d) La ecuación Ax=0 tiene soluciones no triviales (infinitas soluciones).\n"
            resultado += "    Interpretación: Dado que hay menos de n pivotes, existen variables libres. Si Ax=0 tiene soluciones no triviales, A⁻¹ NO existe. (No cumple)\n\n"
            resultado += "(e) Las columnas de A forman un conjunto linealmente dependiente.\n"
            resultado += "    Interpretación: Dado que hay menos de n pivotes, las columnas son linealmente dependientes, por lo tanto, A NO es invertible. (No cumple)\n"
        return resultado

    @staticmethod
    def inversa_gauss_jordan(matriz_a: Matriz) -> str:
        """Calcula la inversa por Gauss-Jordan mostrando pasos (preserva logs)."""
        if not matriz_a.es_cuadrada():
            return "Error: La matriz A debe ser cuadrada para calcular su inversa."

        n = matriz_a.m
        pasos_str = "=== Cálculo de Inversa A⁻¹ por Método de Gauss-Jordan ===\n\n"
        identidad = np.eye(n)
        aug = np.hstack([matriz_a.filas.copy(), identidad])
        pasos_str += OperacionesMatriciales._imprimir_matriz_aug(aug.tolist(), 0, "Construir [A | I]", n)
        paso = 1
        filas = n
        columnas_totales = 2 * n
        fila_actual = 0
        columnas_pivote = []

        for col in range(n):
            if fila_actual >= filas:
                break
            subcol = np.abs(aug[fila_actual:, col])
            if subcol.size == 0:
                break
            max_rel = np.argmax(subcol) + fila_actual
            if abs(aug[max_rel, col]) < EPS:
                continue
            if fila_actual != max_rel:
                aug[[fila_actual, max_rel], :] = aug[[max_rel, fila_actual], :]
                pasos_str += OperacionesMatriciales._imprimir_matriz_aug(aug.tolist(), paso, f"Intercambio f{fila_actual + 1} ↔ f{max_rel + 1}", n)
                paso += 1
            pivote = aug[fila_actual, col]
            if abs(pivote) > EPS:
                aug[fila_actual, :] = aug[fila_actual, :] / pivote
                pasos_str += OperacionesMatriciales._imprimir_matriz_aug(aug.tolist(), paso, f"f{fila_actual + 1} ← (1/{pivote:.4f}) · f{fila_actual + 1}", n)
                paso += 1
            factors = aug[:, col].copy()
            mask = (np.arange(filas) != fila_actual) & (np.abs(factors) > EPS)
            if np.any(mask):
                aug[mask, :] = aug[mask, :] - factors[mask, None] * aug[fila_actual, None, :]
                for i in np.nonzero(mask)[0]:
                    factor = factors[i]
                    pasos_str += OperacionesMatriciales._imprimir_matriz_aug(aug.tolist(), paso, f"f{i + 1} ← f{i + 1} − ({factor:.4f}) · f{fila_actual + 1}", n)
                    paso += 1
            columnas_pivote.append(col)
            fila_actual += 1

        num_pivotes = len(columnas_pivote)
        pasos_str += f"\n--- Proceso de Reducción Finalizado ---\n"
        pasos_str += OperacionesMatriciales._imprimir_matriz_aug(aug.tolist(), paso, "Matriz Reducida", n)
        parte_A_reducida = Matriz(aug[:, :n].tolist())
        if num_pivotes < n or not parte_A_reducida.es_identidad():
            pasos_str += "La matriz no es invertible porque no tiene pivote en cada fila/columna (no se redujo a la identidad).\n"
            pasos_str += f"Se encontraron {num_pivotes} pivotes, pero se necesitan {n}.\n"
        else:
            inversa = Matriz(aug[:, n:].tolist())
            pasos_str += f"La matriz es invertible. La inversa A⁻¹ es:\n{inversa}\n"
        pasos_str += OperacionesMatriciales._verificar_propiedades_invertibilidad(n, num_pivotes)
        return pasos_str

    @staticmethod
    def _submatriz(matriz: List[List[float]], i: int, j: int) -> List[List[float]]:
        return [[matriz[r][c] for c in range(len(matriz[0])) if c != j] for r in range(len(matriz)) if r != i]

    @staticmethod
    def determinante_sarrus(matriz_a: Matriz) -> str:
        if not matriz_a.es_cuadrada():
            return "Error: La matriz debe ser cuadrada para calcular su determinante."
        if matriz_a.m != 3:
            return f"Error: La Regla de Sarrus solo se aplica a matrices 3×3. Esta matriz es {matriz_a.m}×{matriz_a.n}."
        A = matriz_a.filas
        resultado = "=== Cálculo del Determinante por Regla de Sarrus ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        prod1 = A[0,0]*A[1,1]*A[2,2]
        prod2 = A[0,1]*A[1,2]*A[2,0]
        prod3 = A[0,2]*A[1,0]*A[2,1]
        suma_positiva = prod1 + prod2 + prod3
        prod4 = A[0,2]*A[1,1]*A[2,0]
        prod5 = A[0,0]*A[1,2]*A[2,1]
        prod6 = A[0,1]*A[1,0]*A[2,2]
        suma_negativa = prod4 + prod5 + prod6
        resultado += "Productos principales:\n"
        resultado += f"  P1 = {prod1:.4f}\n  P2 = {prod2:.4f}\n  P3 = {prod3:.4f}\n"
        resultado += f"Suma positiva = {suma_positiva:.4f}\n"
        resultado += "Productos secundarios:\n"
        resultado += f"  P4 = {prod4:.4f}\n  P5 = {prod5:.4f}\n  P6 = {prod6:.4f}\n"
        resultado += f"Suma negativa = {suma_negativa:.4f}\n\n"
        determinante = suma_positiva - suma_negativa
        resultado += f"det(A) = {suma_positiva:.4f} - {suma_negativa:.4f} = {determinante:.4f}\n\n"
        resultado += "✓ La matriz es invertible.\n" if abs(determinante) > 1e-10 else "✓ El determinante es cero, la matriz NO tiene inversa (es singular).\n"
        return resultado

    @staticmethod
    def determinante_cofactores(matriz_a: Matriz) -> str:
        if not matriz_a.es_cuadrada():
            return "Error: La matriz debe ser cuadrada para calcular su determinante."
        A = matriz_a.filas.tolist()
        resultado = "=== Cálculo del Determinante por Expansión por Cofactores ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        def det_rec(mat: List[List[float]], nivel: int = 0) -> Tuple[float, str]:
            n = len(mat)
            indent = '  ' * nivel
            if n == 1:
                val = mat[0][0]
                return val, f"{indent}det = {val:.4f}\n"
            if n == 2:
                det_val = mat[0][0]*mat[1][1] - mat[0][1]*mat[1][0]
                log = f"{indent}Matriz 2×2:\n{indent}[{mat[0][0]:.4f}  {mat[0][1]:.4f}]\n{indent}[{mat[1][0]:.4f}  {mat[1][1]:.4f}]\n"
                log += f"{indent}det = {mat[0][0]:.4f} × {mat[1][1]:.4f} - {mat[0][1]:.4f} × {mat[1][0]:.4f} = {det_val:.4f}\n"
                return det_val, log
            det_val = 0.0
            log = f"{indent}Expansión por la fila 1:\n"
            for j in range(n):
                signo = (-1) ** (1 + j + 1)
                menor = OperacionesMatriciales._submatriz(mat, 0, j)
                det_m, log_m = det_rec(menor, nivel + 1)
                cofactor = signo * det_m
                det_val += mat[0][j] * cofactor
                signo_str = "+" if signo > 0 else "-"
                log += f"{indent}Cofactor de A[1,{j+1}]:\n{indent}  Signo: {signo_str}\n"
                log += f"{indent}  Menor (eliminando fila 1 y columna {j+1}):\n"
                log += log_m
                log += f"{indent}  Cofactor = {signo:.0f} × {det_m:.4f} = {cofactor:.4f}\n"
                log += f"{indent}  Término: A[1,{j+1}] × cofactor = {mat[0][j]:.4f} × {cofactor:.4f} = {mat[0][j] * cofactor:.4f}\n\n"
            log += f"{indent}det = suma de términos = {det_val:.4f}\n"
            return det_val, log
        det_value, det_log = det_rec(A)
        resultado += det_log
        resultado += f"\n=== Resultado Final ===\n det(A) = {det_value:.4f}\n\n"
        resultado += "✓ El determinante es distinto de cero, por lo tanto A es invertible.\n" if abs(det_value) > 1e-10 else "✓ El determinante es cero, la matriz NO tiene inversa (es singular).\n"
        return resultado

    @staticmethod
    def determinante_cramer(matriz_a: Matriz) -> str:
        if not matriz_a.es_cuadrada():
            return "Error: La matriz debe ser cuadrada para calcular su determinante."
        if matriz_a.m > 3:
            return f"Nota: El método de Cramer es ilustrativo para matrices pequeñas. Esta matriz es {matriz_a.m}×{matriz_a.n}.\nUse expansión por cofactores para matrices grandes."
        resultado = "=== Cálculo del Determinante por Método de Cramer ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        if matriz_a.m == 1:
            det_value = matriz_a.filas[0,0]
        elif matriz_a.m == 2:
            A = matriz_a.filas
            det_value = A[0,0]*A[1,1] - A[0,1]*A[1,0]
        else:
            A = matriz_a.filas
            det_value = (A[0,0]*(A[1,1]*A[2,2] - A[1,2]*A[2,1])
                         - A[0,1]*(A[1,0]*A[2,2] - A[1,2]*A[2,0])
                         + A[0,2]*(A[1,0]*A[2,1] - A[1,1]*A[2,0]))
        resultado += f"\n=== Resultado Final ===\n det(A) = {det_value:.4f}\n\n"
        resultado += "✓ El determinante es distinto de cero.\n" if abs(det_value) > 1e-10 else "✓ El determinante es cero, la matriz NO tiene inversa (es singular).\n"
        return resultado

    @staticmethod
    def verificar_propiedades_determinante(matriz_a: Matriz) -> str:
        if not matriz_a.es_cuadrada():
            return "Error: La matriz debe ser cuadrada para verificar propiedades del determinante."
        resultado = "=== Verificación de Propiedades del Determinante ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        det_A = OperacionesMatriciales._calcular_det_directo(matriz_a.filas.tolist())
        resultado += f"Determinante de A: det(A) = {det_A:.4f}\n\n"
        # Propiedad 1: fila/col cero
        fila_cero = all(abs(x) < 1e-10 for x in matriz_a.filas[0])
        col_cero = all(abs(matriz_a.filas[i,0]) < 1e-10 for i in range(matriz_a.m))
        if fila_cero:
            resultado += f"✓ La fila 1 es cero → det(A) = 0. Verificado: {abs(det_A) < 1e-10}\n"
        elif col_cero:
            resultado += f"✓ La columna 1 es cero → det(A) = 0. Verificado: {abs(det_A) < 1e-10}\n"
        else:
            A_fila_cero = matriz_a.filas.copy()
            A_fila_cero[0, :] = 0.0
            det_fila_cero = OperacionesMatriciales._calcular_det_directo(A_fila_cero.tolist())
            resultado += f"Ejemplo: Si la fila 1 es cero, det = {det_fila_cero:.4f} (debe ser 0).\n"
        # Propiedad 2: filas iguales
        filas_iguales = any(i != j and np.allclose(matriz_a.filas[i,:], matriz_a.filas[j,:], atol=1e-10) for i in range(matriz_a.m) for j in range(matriz_a.m))
        if filas_iguales:
            resultado += f"✓ Hay filas iguales → det(A) = 0. Verificado: {abs(det_A) < 1e-10}\n"
        else:
            A_filas_iguales = matriz_a.filas.copy()
            if matriz_a.m >= 2:
                A_filas_iguales[1, :] = A_filas_iguales[0, :]
                det_filas_iguales = OperacionesMatriciales._calcular_det_directo(A_filas_iguales.tolist())
                resultado += f"Ejemplo: Si las filas 1 y 2 son iguales, det = {det_filas_iguales:.4f} (debe ser 0).\n"
        # Propiedad 3: intercambio cambia signo
        if matriz_a.m >= 2:
            A_intercambio = matriz_a.filas.copy()
            A_intercambio[[0,1], :] = A_intercambio[[1,0], :]
            det_intercambio = OperacionesMatriciales._calcular_det_directo(A_intercambio.tolist())
            resultado += f"\nSi intercambiamos las filas 1 y 2:\n det(A') = {det_intercambio:.4f}\n det(A) = {det_A:.4f}\n Verificación: det(A') = -det(A) → {abs(det_intercambio + det_A) < 1e-10}\n"
        # Propiedad 4: multiplicar fila por k
        k = 2.0
        A_k = matriz_a.filas.copy()
        if matriz_a.m >= 1:
            A_k[0, :] = A_k[0, :] * k
            det_k = OperacionesMatriciales._calcular_det_directo(A_k.tolist())
            resultado += f"\nSi multiplicamos la fila 1 por k = {k:.4f}:\n det(k·fila1) = {det_k:.4f}\n k × det(A) = {k * det_A:.4f}\n Verificación: {abs(det_k - k * det_A) < 1e-10}\n"
        resultado += "\n--- Propiedad multiplicativa det(AB) = det(A)×det(B) se verifica en otra función ---\n"
        return resultado

    @staticmethod
    def verificar_propiedad_multiplicativa(matriz_a: Matriz, matriz_b: Matriz) -> str:
        if not matriz_a.es_cuadrada() or not matriz_b.es_cuadrada():
            return "Error: Ambas matrices deben ser cuadradas."
        if matriz_a.n != matriz_b.m:
            return f"Error: No se pueden multiplicar matrices {matriz_a.m}×{matriz_a.n} y {matriz_b.m}×{matriz_b.n}."
        resultado = "=== Verificación de Propiedad: det(AB) = det(A) × det(B) ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"
        det_A = OperacionesMatriciales._calcular_det_directo(matriz_a.filas.tolist())
        det_B = OperacionesMatriciales._calcular_det_directo(matriz_b.filas.tolist())
        resultado += f"det(A) = {det_A:.4f}\n det(B) = {det_B:.4f}\n det(A)×det(B) = {det_A * det_B:.4f}\n\n"
        try:
            AB = matriz_a * matriz_b
            det_AB = OperacionesMatriciales._calcular_det_directo(AB.filas.tolist())
            resultado += f"Producto AB ({AB.m}×{AB.n}):\n{AB}\n\n det(AB) = {det_AB:.4f}\n\n"
            cumple = abs(det_AB - det_A * det_B) < 1e-10
            resultado += f"Verificación: {cumple}\n"
            resultado += "✓ La propiedad se cumple.\n" if cumple else "✗ La propiedad NO se cumple para estas matrices.\n"
        except Exception as e:
            resultado += f"Error al calcular AB: {e}\n"
        return resultado

    @staticmethod
    def _calcular_det_directo(mat: List[List[float]]) -> float:
        """Determinante directo recursivo (sin logs) — usado internamente para verificaciones."""
        n = len(mat)
        if n == 0:
            return 0.0
        if n == 1:
            return float(mat[0][0])
        if n == 2:
            return float(mat[0][0]*mat[1][1] - mat[0][1]*mat[1][0])
        det = 0.0
        for j in range(n):
            menor = OperacionesMatriciales._submatriz(mat, 0, j)
            signo = (-1) ** (1 + j + 1)
            det += mat[0][j] * signo * OperacionesMatriciales._calcular_det_directo(menor)
        return float(det)
    
# ==========================================================
# INICIO: CÓDIGO AÑADIDO PARA NOTACIÓN Y ERRORES NUMÉRICOS
# ==========================================================

class NotacionPosicional:
    """
    Contiene métodos estáticos para demostrar la notación posicional.
    """
    
    @staticmethod
    def descomponer_base10(numero_str: str) -> str:
        """
        Descompone un número en base 10, mostrando potencias,
        multiplicación y suma.
        Ejemplo: 254
        """
        try:
            # Validar que es un entero positivo
            if not numero_str.isdigit() or int(numero_str) < 0:
                return f"Error: '{numero_str}' no es un número entero positivo válido."
            
            n = len(numero_str)
            terminos_potencia = []
            terminos_multiplicacion = []
            suma_total = 0
            
            for i, digito_str in enumerate(numero_str):
                digito = int(digito_str)
                # Potencia (de derecha a izquierda, n-1, n-2, ..., 0)
                potencia = n - 1 - i
                valor_posicional = 10**potencia
                
                terminos_potencia.append(f"{digito} × 10^{potencia}")
                terminos_multiplicacion.append(f"{digito} × {valor_posicional}")
                
                suma_total += digito * valor_posicional

            resultado = [
                f"=== Descomposición de {numero_str} (Base 10) ===",
                "1. Usando potencias de 10:",
                f"   {numero_str} = {' + '.join(terminos_potencia)}",
                "\n2. Multiplicación por valor posicional:",
                f"   {numero_str} = {' + '.join(terminos_multiplicacion)}",
                "\n3. Suma final:",
                f"   {numero_str} = {suma_total}"
            ]
            return "\n".join(resultado)

        except Exception as e:
            return f"Error al procesar {numero_str} en base 10: {e}"

    @staticmethod
    def descomponer_base2(numero_bin_str: str) -> str:
        """
        Descompone un número en base 2, mostrando potencias,
        multiplicación y suma.
        Ejemplo: 1101
        """
        try:
            # Validar que es un binario válido
            if not all(c in '01' for c in numero_bin_str):
                 return f"Error: '{numero_bin_str}' no es un número binario válido (solo 0 y 1)."

            n = len(numero_bin_str)
            terminos_potencia = []
            terminos_multiplicacion = []
            suma_total = 0
            
            for i, digito_str in enumerate(numero_bin_str):
                digito = int(digito_str)
                # Potencia (de derecha a izquierda)
                potencia = n - 1 - i
                valor_posicional = 2**potencia
                
                terminos_potencia.append(f"{digito} × 2^{potencia}")
                terminos_multiplicacion.append(f"{digito} × {valor_posicional}")
                
                suma_total += digito * valor_posicional

            resultado = [
                f"=== Descomposición de {numero_bin_str} (Base 2) ===",
                "1. Usando potencias de 2:",
                f"   {numero_bin_str} = {' + '.join(terminos_potencia)}",
                "\n2. Multiplicación por valor posicional:",
                f"   {numero_bin_str} = {' + '.join(terminos_multiplicacion)}",
                "\n3. Suma final (conversión a Base 10):",
                f"   {numero_bin_str} = {suma_total}"
            ]
            return "\n".join(resultado)
            
        except Exception as e:
            return f"Error al procesar {numero_bin_str} en base 2: {e}"


class ErroresNumericos:
    """
    Contiene métodos estáticos para explicar y demostrar
    conceptos de error en métodos numéricos.
    """

    @staticmethod
    def calcular_errores_propagacion(xv: float, xa: float) -> str:
        """
        Calcula el error absoluto, relativo y la propagación del error
        a través de la función f(x) = sin(x) + x^2.
        """
        try:
            # --- 1. Definir la función f(x) ---
            def f(x):
                return np.sin(x) + x**2
            
            # --- 2. Errores en la Entrada (x) ---
            # Ea = |xv - xa|
            ea_x = np.abs(xv - xa)
            er_x = 0.0
            
            # Er = Ea / |xv|
            if np.abs(xv) > EPS: # Evitar división por cero
                er_x = ea_x / np.abs(xv)
            
            # --- 3. Calcular propagación (evaluar la función) ---
            yv = f(xv) # Valor verdadero de la función
            ya = f(xa) # Valor aproximado de la función
            
            # --- 4. Errores en la Salida (y = f(x)) ---
            # Este es el error "propagado"
            ea_y = np.abs(yv - ya)
            er_y = 0.0
            
            if np.abs(yv) > EPS:
                er_y = ea_y / np.abs(yv)
                
            # --- 5. Formatear salida tabular ---
            resultados = [
                "=== 5. Ejercicio de Cálculo de Error y Propagación ===",
                "Función: f(x) = sin(x) + x^2",
                f"Valor Verdadero (xv):   {xv:.10f}",
                f"Valor Aproximado (xa): {xa:.10f}",
                "\n" + ("-" * 60),
                " RESULTADOS EN FORMATO TABULAR:",
                (" " * 22) + "|      Entrada (x)      |   Salida (y = f(x))",
                ("-" * 60),
                f"Valor Verdadero       | {xv:20.10f} | {yv:20.10f}",
                f"Valor Aproximado    | {xa:20.10f} | {ya:20.10f}",
                f"Error Absoluto (Ea)   | {ea_x:20.10f} | {ea_y:20.10f}",
                f"Error Relativo (Er)   | {er_x:20.10f} | {er_y:20.10f}",
                f"Error Relativo (%)    | {er_x*100:19.8f}% | {er_y*100:19.8f}%",
                ("-" * 60),
                
                "\n--- Interpretación de los Resultados ---",
                f"Un error absoluto de {ea_x:.4e} en la entrada 'x' (un {er_x*100:.2f}%)",
                f"se propagó a través de la función, resultando en",
                f"un error absoluto de {ea_y:.4e} en la salida 'y' (un {er_y*100:.2f}%).",
            ]
            
            if er_y > (er_x * 1.1) and er_x > EPS: # Si el error propagado es > 10% más grande
                resultados.append("\nDiagnóstico: El error relativo fue *magnificado* por la función en este punto.")
            elif er_y < (er_x * 0.9) and er_y > EPS:
                resultados.append("\nDiagnóstico: El error relativo fue *atenuado* (reducido) por la función.")
            else:
                resultados.append("\nDiagnóstico: El error relativo se mantuvo relativamente estable.")
                
            return "\n".join(resultados)

        except Exception as e:
            return f"Error durante el cálculo de propagación: {e}"

    @staticmethod
    def ejemplo_punto_flotante() -> str:
        """
        Demuestra la imprecisión de los números de punto flotante.
        Ejemplo: 0.1 + 0.2
        """
        a = 0.1
        b = 0.2
        suma = a + b
        resultado = [
            "=== 3. Ejemplo de Punto Flotante (Imprecisión) ===",
            f"   Operación: 0.1 + 0.2",
            f"   Resultado: {suma}",
            f"   ¿Es igual a 0.3? {suma == 0.3}",
            "\nExplicación:",
            "   La computadora no puede representar exactamente números como 0.1 o 0.2",
            "   en binario (base 2). Son números 'infinitos' en binario, similar a",
            "   como 1/3 (0.333...) es infinito en decimal (base 10).",
            "   La máquina almacena aproximaciones muy cercanas.",
            "   Al sumar estas aproximaciones, el resultado es una aproximación",
            f"   de 0.3, pero no es *exactamente* 0.3. Es {suma:.17f}..."
        ]
        return "\n".join(resultado)

    @staticmethod
    def get_explicaciones_errores() -> str:
        """
        Devuelve una cadena con explicaciones y ejemplos de
        los 5 tipos de errores numéricos.
        """
        
        # 1. Error Inherente
        ex_inherente = [
            "\n--- Error Inherente ---",
            "   Definición: Es el error en los datos de entrada, antes de cualquier cálculo.",
            "   Proviene de mediciones (ej. un sensor, una regla) o de datos que ya",
            "   son el resultado de un cálculo previo.",
            "   Ejemplo: Medir la altura de una mesa. La medición es 1.51m, pero",
            "   el valor real *exacto* podría ser 1.5132...m. El error de 0.0032...",
            "   es inherente y se propagará por todos los cálculos que usen ese dato."
        ]
        
        # 2. Error de Redondeo
        val_redondeo = 1.0 / 3.0
        ex_redondeo = [
            "\n--- Error de Redondeo ---",
            "   Definición: Ocurre porque la computadora solo puede almacenar un número",
            "   finito de dígitos.",
            "   Ejemplo: 1/3 es 0.33333... (infinito). La máquina lo almacena como",
            f"   algo similar a {val_redondeo:.17f}. La diferencia entre el valor",
            "   real y el almacenado es el error de redondeo."
        ]

        # 3. Error de Truncamiento
        e_aprox = 1 + 1 + (1**2 / 2) + (1**3 / 6) # 4 términos de e^x
        e_real = np.e
        ex_truncamiento = [
            "\n--- Error de Truncamiento ---",
            "   Definición: Ocurre al 'truncar' o cortar un proceso matemático",
            "   infinito para obtener una aproximación finita.",
            "   Ejemplo: La serie de Taylor para e^x es 1 + x + x²/2! + x³/3! + ... (infinita).",
            f"   Si calculamos e¹ (x=1) usando solo 4 términos: 1+1+1/2+1/6 = {e_aprox:.4f}",
            f"   El valor real de 'e' es {e_real:.7f}...",
            "   El error (la parte de la serie que 'cortamos') es el error de truncamiento."
        ]

        # 4. Overflow y Underflow
        max_float = sys.float_info.max
        min_float = sys.float_info.min
        try:
            # np.seterr(over='ignore') # numpy ya lo maneja
            overflow = max_float * 10
            underflow = min_float / (10**10) # Forzarlo a 0.0
        except Exception:
            overflow = float('inf')
            underflow = 0.0
            
        ex_overflow = [
            "\n--- Overflow y Underflow ---",
            f"   El número más grande almacenable (float64) es aprox: {max_float:e}",
            f"   El número positivo más pequeño (subnormal) es aprox: {min_float:e}",
            "",
            "   Overflow (Desbordamiento):",
            "     Ocurre cuando un cálculo produce un número MÁS GRANDE que el máximo.",
            f"     Ej: {max_float:e} * 10 = {overflow}",
            "     Python (y numpy) lo manejan como 'inf' (infinito).",
            "",
            "   Underflow (Subdesbordamiento):",
            "     Ocurre cuando un cálculo produce un número MÁS PEQUEÑO",
            "     (más cercano a cero) que el mínimo positivo almacenable.",
            f"     Ej: {min_float:e} / 10**10 = {underflow}",
            "     La máquina lo redondea a 0.0, perdiendo toda la precisión."
        ]
        
        # 5. Error del Modelo Matemático
        ex_modelo = [
            "\n--- Error del Modelo Matemático ---",
            "   Definición: Es la discrepancia entre el fenómeno real y el modelo",
            "   matemático usado para describirlo.",
            "   Ejemplo: Usar un modelo de crecimiento poblacional exponencial (P = P₀·eᵏᵗ)",
            "   para una población de bacterias. Este modelo asume recursos infinitos.",
            "   En la realidad, la comida se acaba y el crecimiento se frena (un modelo",
            "   logístico sería mejor). El error no está en el *cálculo*, sino en",
            "   que la *ecuación* (el modelo) es una simplificación de la realidad."
        ]
        
        linea_sep = "\n" + "="*50 + "\n"
        final_str = [
            "=== 2. Conceptos de Error en Métodos Numéricos ==="
        ]
        final_str.extend(ex_inherente)
        final_str.extend(ex_redondeo)
        final_str.extend(ex_truncamiento)
        final_str.extend(ex_overflow)
        final_str.extend(ex_modelo)
        final_str.append(linea_sep)
        final_str.append(ErroresNumericos.ejemplo_punto_flotante())

        return "\n".join(final_str)

class TallerNumPy:
    """
    Contiene métodos estáticos para el "Taller Guiado" sobre
    precisión numérica y manejo de errores en NumPy.
    """

    @staticmethod
    def taller_grande_pequeno(a_str: str, b_str: str) -> str:
        """Calcula (a+b)-a para demostrar pérdida de precisión."""
        resultados = [
            "=== Taller: Pérdida de Precisión (Grande + Pequeño) ===",
        ]
        try:
            a_grande = float(a_str)
            b_pequeno = float(b_str)
            
            suma_paso1 = a_grande + b_pequeno
            resultado_final = (a_grande + b_pequeno) - a_grande

            resultados.extend([
                f"   Valor 'a' (grande): {a_grande:e}",
                f"   Valor 'b' (pequeño): {b_pequeno:e}",
                "   Operación: (a + b) - a",
                "\n   En teoría, el resultado debería ser 'b'.",
                "\n--- Cálculo ---",
                f"   Paso 1 (a + b):   {suma_paso1:e}",
                f"   Paso 2 (a+b)-a: {resultado_final:e}",
                "\n--- Conclusión ---",
            ])

            if np.isclose(a_grande, suma_paso1):
                 resultados.append(
                    f"   El valor 'b' ({b_pequeno:e}) se 'perdió' por completo.\n"
                    f"   Esto pasa porque la precisión de un float no es suficiente\n"
                    f"   para almacenar la diferencia de magnitud entre 'a' y 'b'."
                 )
            else:
                 resultados.append(
                    f"   El resultado {resultado_final:e} es cercano a 'b'.\n"
                    f"   En este caso, la diferencia de magnitud no fue\n"
                    f"   suficientemente grande para perder toda la precisión."
                 )
            return "\n".join(resultados)

        except Exception as e:
            return f"{resultados[0]}\nError en la entrada: {e}"


    @staticmethod
    def taller_cancelacion(c_str: str, d_str: str) -> str:
        """Calcula (c-d) para demostrar cancelación catastrófica."""
        resultados = [
            "=== Taller: Cancelación Catastrófica ===",
        ]
        try:
            c = float(c_str)
            d = float(d_str)
            resta = c - d

            resultados.extend([
                "   Sustracción de números casi iguales.",
                f"   Valor 'c': {c:.16f}",
                f"   Valor 'd': {d:.16f}",
                f"   Resultado (c - d): {resta:e}",
                "\n--- Conclusión ---",
                "   Cuando restas números muy similares, cualquier pequeño",
                "   error de redondeo en 'c' o 'd' se magnifica.",
                "   El resultado final puede tener muy pocas cifras",
                "   significativas correctas, o incluso ser 0.0."
            ])
            return "\n".join(resultados)
            
        except Exception as e:
            return f"{resultados[0]}\nError en la entrada: {e}"


    @staticmethod
    def run_taller_demos() -> str:
        """
        Ejecuta ejemplos de float32/64 e inf/nan que no requieren
        entrada del usuario.
        """
        resultados = [
            "=== Demos NumPy (float32/64 e inf/nan) ===",
        ]

        # --- NumPy y Tipos de Datos (float32 vs float64) ---
        a32 = np.float32(0.1)
        b32 = np.float32(0.2)
        suma32 = a32 + b32
        
        a64 = np.float64(0.1)
        b64 = np.float64(0.2)
        suma64 = a64 + b64

        resultados.extend([
            "\n--- 1. NumPy y Tipos de Datos (float32 vs float64) ---",
            "   float32 (precisión simple, ~7 dígitos decimales)",
            f"   np.float32(0.1) = {a32:.10f}",
            f"   np.float32(0.2) = {b32:.10f}",
            f"   Suma (float32):    {suma32:.10f}",
            "",
            "   float64 (precisión doble, ~15-16 dígitos, default en Python)",
            f"   np.float64(0.1) = {a64:.17f}",
            f"   np.float64(0.2) = {b64:.17f}",
            f"   Suma (float64):    {suma64:.17f}",
            "   Conclusión: Ambos son inexactos, pero float32 pierde precisión mucho antes.",
        ])

        # --- NumPy: Manejo de Errores (inf y nan) ---
        with np.errstate(divide='ignore', over='ignore'): # Suprime warnings
            div_cero = 1.0 / np.array([0.0])
            indeterminado = 0.0 / np.array([0.0])
            overflow = np.exp(1000) # Número demasiado grande

        resultados.extend([
            "\n--- 2. NumPy: Manejo de Errores Especiales ---",
            "   NumPy devuelve valores especiales en lugar de detener el programa.",
            "",
            "   División por cero:",
            f"   1.0 / np.array([0.0])  = {div_cero}",
            "",
            "   Indeterminado:",
            f"   0.0 / np.array([0.0])  = {indeterminado} (Not a Number)",
            "",
            "   Overflow (Desbordamiento):",
            f"   np.exp(1000) = {overflow}",
        ])

        return "\n".join(resultados)