import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List

"""
Aplicación de una sola pieza (NO modular) con interfaz cuidada en Tkinter.
- Sin librerías externas (solo tkinter/ttk de la librería estándar).
- Calcula sistemas lineales por Eliminación Gaussiana con pivoteo parcial.
- Operaciones con vectores: suma, multiplicación por escalar, combinación lineal.
- Ecuaciones vectoriales y matriciales.
- UI con pestañas, validación de entradas, ayuda, exportar y copiar.

Ejecuta:  python matriz_e_interfaz.py
"""

# ============================
# Núcleo de cálculo (modelo)
# ============================
class SistemaLineal:
    def __init__(self, matriz_aumentada: List[List[float]]):
        self.matriz = [fila[:] for fila in matriz_aumentada]

    def _imprimir_matriz(self, paso: int, operacion: str) -> str:
        texto = f"Paso {paso} ({operacion}):\n"
        for fila in self.matriz:
            texto += "  ".join(f"{valor:.4f}" for valor in fila) + "\n"
        return texto + "\n"

    def eliminacion_gaussiana(self) -> str:
        if not self.matriz:
            return "Matriz no válida."

        paso = 1
        resultado = ""
        filas, columnas = len(self.matriz), len(self.matriz[0])
        fila_actual = 0

        for col in range(columnas - 1):
            if fila_actual >= filas:
                break

            max_row = max(range(fila_actual, filas), key=lambda i: abs(self.matriz[i][col]))
            if abs(self.matriz[max_row][col]) < 1e-12:
                continue

            if fila_actual != max_row:
                self.matriz[fila_actual], self.matriz[max_row] = self.matriz[max_row], self.matriz[fila_actual]
                resultado += self._imprimir_matriz(paso, f"Intercambio f{fila_actual + 1} ↔ f{max_row + 1}")
                paso += 1

            pivote = self.matriz[fila_actual][col]

            if abs(pivote) > 1e-12:
                self.matriz[fila_actual] = [x / pivote for x in self.matriz[fila_actual]]
                resultado += self._imprimir_matriz(paso, f"f{fila_actual + 1} ← (1/{pivote:.4f}) · f{fila_actual + 1}")
                paso += 1

            for i in range(filas):
                if i != fila_actual:
                    factor = self.matriz[i][col]
                    if abs(factor) > 1e-12:
                        self.matriz[i] = [self.matriz[i][k] - factor * self.matriz[fila_actual][k] for k in range(columnas)]
                        resultado += self._imprimir_matriz(paso, f"f{i + 1} ← f{i + 1} − ({factor:.4f}) · f{fila_actual + 1}")
                        paso += 1

            fila_actual += 1

        resultado += self._interpretar_resultado()
        return resultado

    def _interpretar_resultado(self) -> str:
        n, m = len(self.matriz), len(self.matriz[0]) - 1
        pivotes = [-1] * m
        resultado = "Solución del sistema:\n"
        soluciones = {}
        soluciones_numericas = {}
        columnas_pivote = []

        for j in range(m):
            for i in range(n):
                if (abs(self.matriz[i][j] - 1) < 1e-10 and 
                    all(abs(self.matriz[k][j]) < 1e-10 for k in range(n) if k != i)):
                    pivotes[j] = i
                    columnas_pivote.append(j + 1)
                    break

        fila_inconsistente = [
            i for i, fila in enumerate(self.matriz)
            if all(abs(val) < 1e-10 for val in fila[:-1]) and abs(fila[-1]) > 1e-10
        ]
        inconsistente_var = {f"x{i + 1}" for i in fila_inconsistente}

        for j in range(m):
            var_name = f"x{j + 1}"
            if var_name in inconsistente_var:
                soluciones[var_name] = f"{var_name} es inconsistente"
            elif pivotes[j] == -1:
                soluciones[var_name] = f"{var_name} es libre"
            else:
                fila = pivotes[j]
                constante = self.matriz[fila][-1]
                constante_str = (f"{int(constante)}" if float(constante).is_integer() else f"{constante:.4f}")
                terminos = []
                for k in range(m):
                    if k != j and pivotes[k] == -1 and abs(self.matriz[fila][k]) > 1e-10:
                        coef = -self.matriz[fila][k]
                        coef_str = (f"{int(coef)}" if float(coef).is_integer() else f"{coef:.4f}")
                        terminos.append(f"{'+' if coef >= 0 else ''}{coef_str}x{k + 1}")

                if constante_str == "0" and not terminos:
                    ecuacion = "0"
                else:
                    ecuacion = (constante_str if constante_str != "0" else "")
                    if terminos:
                        ecuacion = (ecuacion + " " if ecuacion else "") + " ".join(terminos).lstrip("+ ").strip()

                soluciones[var_name] = f"{var_name} = {ecuacion}".strip()

                if not terminos:
                    soluciones_numericas[var_name] = constante

        for i in range(m):
            var_name = f"x{i + 1}"
            if var_name in soluciones:
                resultado += f"{soluciones[var_name]}\n"

        if inconsistente_var:
            resultado += "\nEl sistema es inconsistente y no tiene soluciones.\n"
        elif any(pivote == -1 for pivote in pivotes):
            resultado += "\nHay infinitas soluciones debido a variables libres.\n"
        else:
            if len(soluciones_numericas) == m and all(abs(val) < 1e-10 for val in soluciones_numericas.values()):
                resultado += "\nSolución trivial.\n"
            else:
                resultado += "\nLa solución es única.\n"

        resultado += f"\nLas columnas pivote son: {', '.join(map(str, columnas_pivote))}.\n"
        return resultado


# ============================
# Clases para Vectores
# ============================
class Vector:
    def __init__(self, componentes: List[float]):
        self.componentes = componentes[:]
        self.dimension = len(componentes)
    
    def __str__(self) -> str:
        return f"({', '.join(f'{x:.4f}' for x in self.componentes)})"
    
    def __add__(self, other: 'Vector') -> 'Vector':
        if self.dimension != other.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión")
        return Vector([a + b for a, b in zip(self.componentes, other.componentes)])
    
    def __sub__(self, other: 'Vector') -> 'Vector':
        if self.dimension != other.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión")
        return Vector([a - b for a, b in zip(self.componentes, other.componentes)])
    
    def __mul__(self, escalar: float) -> 'Vector':
        return Vector([x * escalar for x in self.componentes])
    
    def __rmul__(self, escalar: float) -> 'Vector':
        return self.__mul__(escalar)
    
    def producto_punto(self, other: 'Vector') -> float:
        if self.dimension != other.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión")
        return sum(a * b for a, b in zip(self.componentes, other.componentes))
    
    def norma(self) -> float:
        return (sum(x**2 for x in self.componentes))**0.5
    
    def es_cero(self) -> bool:
        return all(abs(x) < 1e-10 for x in self.componentes)
    
    def opuesto(self) -> 'Vector':
        return Vector([-x for x in self.componentes])


class OperacionesVectoriales:
    @staticmethod
    def verificar_propiedades_espacio_vectorial(vectores: List[Vector]) -> str:
        """Verifica las propiedades del espacio vectorial ℝⁿ"""
        if not vectores:
            return "No hay vectores para verificar."
        
        resultado = "=== Verificación de Propiedades del Espacio Vectorial ℝⁿ ===\n\n"
        
        # Verificar que todos los vectores tengan la misma dimensión
        dim = vectores[0].dimension
        for v in vectores[1:]:
            if v.dimension != dim:
                return f"Error: Los vectores tienen dimensiones diferentes ({dim} vs {v.dimension})"
        
        resultado += f"Dimensión del espacio: ℝ^{dim}\n"
        resultado += f"Número de vectores: {len(vectores)}\n\n"
        
        # 1. Propiedad conmutativa de la suma
        if len(vectores) >= 2:
            v1, v2 = vectores[0], vectores[1]
            suma1 = v1 + v2
            suma2 = v2 + v1
            conmutativa = suma1.componentes == suma2.componentes
            resultado += f"1. Conmutativa (v₁ + v₂ = v₂ + v₁):\n"
            resultado += f"   v₁ + v₂ = {suma1}\n"
            resultado += f"   v₂ + v₁ = {suma2}\n"
            resultado += f"   ✓ Cumple: {conmutativa}\n\n"
        
        # 2. Propiedad asociativa de la suma
        if len(vectores) >= 3:
            v1, v2, v3 = vectores[0], vectores[1], vectores[2]
            suma1 = (v1 + v2) + v3
            suma2 = v1 + (v2 + v3)
            asociativa = suma1.componentes == suma2.componentes
            resultado += f"2. Asociativa ((v₁ + v₂) + v₃ = v₁ + (v₂ + v₃)):\n"
            resultado += f"   (v₁ + v₂) + v₃ = {suma1}\n"
            resultado += f"   v₁ + (v₂ + v₃) = {suma2}\n"
            resultado += f"   ✓ Cumple: {asociativa}\n\n"
        
        # 3. Existencia del vector cero
        vector_cero = Vector([0.0] * dim)
        resultado += f"3. Vector cero: {vector_cero}\n"
        resultado += f"   ✓ Existe el vector cero\n\n"
        
        # 4. Existencia del vector opuesto
        if vectores:
            v = vectores[0]
            opuesto = v.opuesto()
            suma_cero = v + opuesto
            resultado += f"4. Vector opuesto para v₁ = {v}:\n"
            resultado += f"   -v₁ = {opuesto}\n"
            resultado += f"   v₁ + (-v₁) = {suma_cero}\n"
            resultado += f"   ✓ Es vector cero: {suma_cero.es_cero()}\n\n"
        
        # 5. Propiedades de multiplicación por escalar
        if vectores:
            v = vectores[0]
            escalar1, escalar2 = 2.0, 3.0
            prop1 = (escalar1 + escalar2) * v
            prop2 = escalar1 * v + escalar2 * v
            distributiva1 = prop1.componentes == prop2.componentes
            
            prop3 = escalar1 * (escalar2 * v)
            prop4 = (escalar1 * escalar2) * v
            asociativa_escalar = prop3.componentes == prop4.componentes
            
            resultado += f"5. Propiedades de multiplicación por escalar:\n"
            resultado += f"   (α + β)v = αv + βv: ✓ {distributiva1}\n"
            resultado += f"   α(βv) = (αβ)v: ✓ {asociativa_escalar}\n"
        
        return resultado
    
    @staticmethod
    def combinacion_lineal(vectores: List[Vector], vector_objetivo: Vector) -> str:
        """Determina si el vector objetivo es combinación lineal de los vectores dados"""
        if not vectores:
            return "No hay vectores para la combinación lineal."
        
        resultado = "=== Combinación Lineal de Vectores ===\n\n"
        resultado += f"Vectores dados: {len(vectores)}\n"
        for i, v in enumerate(vectores):
            resultado += f"v{i+1} = {v}\n"
        resultado += f"\nVector objetivo: {vector_objetivo}\n\n"
        
        # Verificar dimensiones
        dim = vectores[0].dimension
        for v in vectores + [vector_objetivo]:
            if v.dimension != dim:
                return f"Error: Los vectores tienen dimensiones diferentes"
        
        # Plantear el sistema: c₁v₁ + c₂v₂ + ... + cₙvₙ = b
        resultado += "Planteo del sistema:\n"
        resultado += f"c₁v₁ + c₂v₂ + ... + c{len(vectores)}v{len(vectores)} = b\n\n"
        
        # Construir matriz aumentada
        matriz_aumentada = []
        for i in range(dim):
            fila = []
            for v in vectores:
                fila.append(v.componentes[i])
            fila.append(vector_objetivo.componentes[i])
            matriz_aumentada.append(fila)
        
        resultado += "Matriz aumentada del sistema:\n"
        for i, fila in enumerate(matriz_aumentada):
            resultado += f"Fila {i+1}: {'  '.join(f'{x:8.4f}' for x in fila)}\n"
        resultado += "\n"
        
        # Resolver usando eliminación gaussiana
        sistema = SistemaLineal(matriz_aumentada)
        resultado += sistema.eliminacion_gaussiana()
        
        return resultado
    
    @staticmethod
    def ecuacion_vectorial(vectores: List[Vector], vector_objetivo: Vector) -> str:
        """Resuelve la ecuación vectorial c₁v₁ + c₂v₂ + ... + cₙvₙ = b"""
        if not vectores:
            return "No hay vectores para la ecuación."
        
        resultado = "=== Ecuación Vectorial ===\n\n"
        resultado += f"Ecuación: c₁v₁ + c₂v₂ + ... + c{len(vectores)}v{len(vectores)} = b\n\n"
        
        for i, v in enumerate(vectores):
            resultado += f"v{i+1} = {v}\n"
        resultado += f"b = {vector_objetivo}\n\n"
        
        # Usar el mismo método que combinación lineal
        return resultado + OperacionesVectoriales.combinacion_lineal(vectores, vector_objetivo)


# ============================
# Clases para Matrices
# ============================
class Matriz:
    def __init__(self, filas: List[List[float]]):
        self.filas = [fila[:] for fila in filas]
        self.m = len(filas)  # número de filas
        self.n = len(filas[0]) if filas else 0  # número de columnas
    
    def __str__(self) -> str:
        return "\n".join("  ".join(f"{x:8.4f}" for x in fila) for fila in self.filas)
    
    def __mul__(self, other):
        """Multiplicación de matrices A * B"""
        if self.n != other.m:
            raise ValueError(f"No se pueden multiplicar matrices {self.m}×{self.n} y {other.m}×{other.n}")
        
        resultado = []
        for i in range(self.m):
            fila = []
            for j in range(other.n):
                suma = 0
                for k in range(self.n):
                    suma += self.filas[i][k] * other.filas[k][j]
                fila.append(suma)
            resultado.append(fila)
        
        return Matriz(resultado)
    
    def es_cuadrada(self) -> bool:
        return self.m == self.n
    
    def es_identidad(self) -> bool:
        if not self.es_cuadrada():
            return False
        for i in range(self.m):
            for j in range(self.n):
                if i == j and abs(self.filas[i][j] - 1) > 1e-10:
                    return False
                elif i != j and abs(self.filas[i][j]) > 1e-10:
                    return False
        return True


class OperacionesMatriciales:
    @staticmethod
    def ecuacion_matricial(matriz_a: Matriz, matriz_b: Matriz) -> str:
        """Resuelve la ecuación matricial AX = B"""
        resultado = "=== Ecuación Matricial AX = B ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"
        
        # Verificar dimensiones
        if matriz_a.n != matriz_b.m:
            return resultado + f"Error: No se puede resolver AX = B.\n"
            + f"El número de columnas de A ({matriz_a.n}) debe ser igual al número de filas de B ({matriz_b.m}).\n"
        
        resultado += "Planteo del sistema:\n"
        resultado += "Para cada columna j de B, resolver Axⱼ = bⱼ\n\n"
        
        # Resolver para cada columna de B
        soluciones = []
        for j in range(matriz_b.n):
            resultado += f"--- Columna {j+1} de B ---\n"
            
            # Construir sistema Ax = b para la columna j
            matriz_aumentada = []
            for i in range(matriz_a.m):
                fila = matriz_a.filas[i][:] + [matriz_b.filas[i][j]]
                matriz_aumentada.append(fila)
            
            resultado += f"Sistema Axⱼ = bⱼ:\n"
            for i, fila in enumerate(matriz_aumentada):
                resultado += f"Fila {i+1}: {'  '.join(f'{x:8.4f}' for x in fila)}\n"
            resultado += "\n"
            
            # Resolver usando eliminación gaussiana
            sistema = SistemaLineal(matriz_aumentada)
            resultado += sistema.eliminacion_gaussiana()
            resultado += "\n" + "="*50 + "\n\n"
        
        return resultado
    
    @staticmethod
    def multiplicacion_matrices(matriz_a: Matriz, matriz_b: Matriz) -> str:
        """Multiplica dos matrices A * B"""
        resultado = "=== Multiplicación de Matrices A * B ===\n\n"
        resultado += f"Matriz A ({matriz_a.m}×{matriz_a.n}):\n{matriz_a}\n\n"
        resultado += f"Matriz B ({matriz_b.m}×{matriz_b.n}):\n{matriz_b}\n\n"
        
        try:
            producto = matriz_a * matriz_b
            resultado += f"Resultado A * B ({producto.m}×{producto.n}):\n{producto}\n\n"
            
            # Mostrar el procedimiento paso a paso
            resultado += "Procedimiento paso a paso:\n"
            for i in range(producto.m):
                for j in range(producto.n):
                    terminos = []
                    for k in range(matriz_a.n):
                        terminos.append(f"({matriz_a.filas[i][k]:.4f} × {matriz_b.filas[k][j]:.4f})")
                    resultado += f"C[{i+1},{j+1}] = {' + '.join(terminos)} = {producto.filas[i][j]:.4f}\n"
            
        except ValueError as e:
            resultado += f"Error: {e}\n"
        
        return resultado


# ============================
# Interfaz (Tkinter)
# ============================
class AlgebraLinealGUI(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master.title("Calculadora de Álgebra Lineal")
        self.master.geometry("1200x700")
        self.master.minsize(1000, 600)
        self.pack(fill=tk.BOTH, expand=True)

        self._init_style()
        self._build_menu()
        self._build_header()
        self._build_notebook()
        self._bind_shortcuts()

        # Estado inicial
        self._status("Listo.")

    # ---------- Estilos y menús ----------
    def _init_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("TButton", padding=6)
        style.configure("TEntry", padding=4)
        style.configure("Card.TFrame", relief="groove", borderwidth=1)

    def _build_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        m_archivo = tk.Menu(menubar, tearoff=0)
        m_archivo.add_command(label="Exportar pasos…", command=self._export, accelerator="Ctrl+S")
        m_archivo.add_separator()
        m_archivo.add_command(label="Salir", command=self.master.quit)

        m_editar = tk.Menu(menubar, tearoff=0)
        m_editar.add_command(label="Copiar resultado", command=self._copy_output, accelerator="Ctrl+C")
        m_editar.add_command(label="Limpiar", command=self._clear_all, accelerator="Ctrl+L")

        m_ayuda = tk.Menu(menubar, tearoff=0)
        m_ayuda.add_command(label="Acerca de", command=self._about)

        menubar.add_cascade(label="Archivo", menu=m_archivo)
        menubar.add_cascade(label="Edición", menu=m_editar)
        menubar.add_cascade(label="Ayuda", menu=m_ayuda)

    def _bind_shortcuts(self):
        self.master.bind_all("<Control-s>", lambda e: self._export())
        self.master.bind_all("<Control-S>", lambda e: self._export())
        self.master.bind_all("<Control-c>", lambda e: self._copy_output())
        self.master.bind_all("<Control-C>", lambda e: self._copy_output())
        self.master.bind_all("<Control-l>", lambda e: self._clear_all())
        self.master.bind_all("<Control-L>", lambda e: self._clear_all())

    # ---------- Construcción de UI ----------
    def _build_header(self):
        topbar = ttk.Frame(self)
        topbar.pack(fill=tk.X, padx=12, pady=(10, 6))

        title = ttk.Label(topbar, text="Calculadora de Sistemas Lineales (Gauss)", style="Header.TLabel")
        title.pack(side=tk.LEFT)

        self.status = ttk.Label(topbar, text="", anchor="e")
        self.status.pack(side=tk.RIGHT)

    def _build_notebook(self):
        # Crear notebook con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        
        # Pestaña 1: Sistemas Lineales (matrices)
        self._build_matrices_tab()
        
        # Pestaña 2: Vectores
        self._build_vectores_tab()
        
        # Pestaña 3: Matrices
        self._build_matrices_operations_tab()
    
    def _build_matrices_tab(self):
        # Frame para la pestaña de matrices
        matrices_frame = ttk.Frame(self.notebook)
        self.notebook.add(matrices_frame, text="Sistemas Lineales")
        
        # Panel de configuración
        card_cfg = ttk.Frame(matrices_frame, style="Card.TFrame")
        card_cfg.pack(fill=tk.X, padx=10, pady=(10, 8))
        cfg = ttk.Frame(card_cfg)
        cfg.pack(fill=tk.X, padx=10, pady=8)

        self.var_m = tk.IntVar()
        self.var_n = tk.IntVar()

        vcmd = (self.register(self._validate_int), "%P")
        ttk.Label(cfg, text="Ecuaciones (m):").grid(row=0, column=0, sticky="w")
        self.sp_m = ttk.Spinbox(cfg, from_=1, to=12, width=6, textvariable=self.var_m, validate="key", validatecommand=vcmd, command=self._apply_size)
        self.sp_m.grid(row=0, column=1, padx=(6,14))

        ttk.Label(cfg, text="Incógnitas (n):").grid(row=0, column=2, sticky="w")
        self.sp_n = ttk.Spinbox(cfg, from_=1, to=12, width=6, textvariable=self.var_n, validate="key", validatecommand=vcmd, command=self._apply_size)
        self.sp_n.grid(row=0, column=3, padx=(6,14))

        ttk.Button(cfg, text="Crear matriz", command=self._apply_size).grid(row=0, column=4)
        ttk.Button(cfg, text="Ejemplo", command=self._load_example).grid(row=0, column=5, padx=(8,0))
        ttk.Button(cfg, text="Resolver", command=self._solve).grid(row=0, column=6, padx=8)
        ttk.Button(cfg, text="Limpiar", command=self._clear_all).grid(row=0, column=7)

        # Panel de matriz
        card_mat = ttk.Frame(matrices_frame, style="Card.TFrame")
        card_mat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,8))
        mat = ttk.Frame(card_mat)
        mat.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        ttk.Label(mat, text="Matriz aumentada [A | b]  (última columna = término independiente)", style="Header.TLabel").pack(anchor="w", pady=(0,6))

        self.canvas = tk.Canvas(mat, highlightthickness=0)
        self.grid_frame = ttk.Frame(self.canvas)
        self.scroll_y = ttk.Scrollbar(mat, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Panel de resultados
        card_out = ttk.Frame(matrices_frame, style="Card.TFrame")
        card_out.pack(fill=tk.BOTH, expand=True, padx=10)
        out = ttk.Frame(card_out)
        out.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        out.columnconfigure(0, weight=1)
        out.rowconfigure(1, weight=1)

        ttk.Label(out, text="Pasos y solución", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.txt = tk.Text(out, wrap="word", height=12, font=("Consolas", 10))
        self.txt.grid(row=1, column=0, sticky="nsew", pady=(4,0))

        btns = ttk.Frame(out)
        btns.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns, text="Copiar resultado", command=self._copy_output).pack(side=tk.LEFT)
        ttk.Button(btns, text="Exportar pasos…", command=self._export).pack(side=tk.LEFT, padx=(8,0))
        
        # Estado inicial para matrices
        self.var_m.set(3)
        self.var_n.set(3)
        self._render_grid(3, 3)
    
    def _build_vectores_tab(self):
        # Frame para la pestaña de vectores
        vectores_frame = ttk.Frame(self.notebook)
        self.notebook.add(vectores_frame, text="Vectores")
        
        # Panel de configuración de vectores
        card_cfg = ttk.Frame(vectores_frame, style="Card.TFrame")
        card_cfg.pack(fill=tk.X, padx=10, pady=(10, 8))
        cfg = ttk.Frame(card_cfg)
        cfg.pack(fill=tk.X, padx=10, pady=8)
        
        self.var_dimension = tk.IntVar()
        self.var_num_vectores = tk.IntVar()
        
        ttk.Label(cfg, text="Dimensión:").grid(row=0, column=0, sticky="w")
        self.sp_dim = ttk.Spinbox(cfg, from_=2, to=10, width=6, textvariable=self.var_dimension, command=self._apply_vector_size)
        self.sp_dim.grid(row=0, column=1, padx=(6,14))
        
        ttk.Label(cfg, text="Número de vectores:").grid(row=0, column=2, sticky="w")
        self.sp_num_vec = ttk.Spinbox(cfg, from_=1, to=8, width=6, textvariable=self.var_num_vectores, command=self._apply_vector_size)
        self.sp_num_vec.grid(row=0, column=3, padx=(6,14))
        
        ttk.Button(cfg, text="Crear vectores", command=self._apply_vector_size).grid(row=0, column=4)
        ttk.Button(cfg, text="Ejemplo", command=self._load_vector_example).grid(row=0, column=5, padx=(8,0))
        ttk.Button(cfg, text="Resolver", command=self._solve_vectors).grid(row=0, column=6, padx=8)
        ttk.Button(cfg, text="Limpiar", command=self._clear_vectors).grid(row=0, column=7, padx=(8,0))
        
        # Panel de operaciones
        card_ops = ttk.Frame(vectores_frame, style="Card.TFrame")
        card_ops.pack(fill=tk.X, padx=10, pady=(0,8))
        ops = ttk.Frame(card_ops)
        ops.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(ops, text="Operaciones:", style="Header.TLabel").pack(anchor="w")
        
        ops_buttons = ttk.Frame(ops)
        ops_buttons.pack(fill=tk.X, pady=(4,0))
        
        ttk.Button(ops_buttons, text="Verificar propiedades", command=self._verify_properties).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Combinación lineal", command=self._linear_combination).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Ecuación vectorial", command=self._vector_equation).pack(side=tk.LEFT, padx=(0,8))
        
        # Panel de entrada de vectores
        card_input = ttk.Frame(vectores_frame, style="Card.TFrame")
        card_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,8))
        input_frame = ttk.Frame(card_input)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        ttk.Label(input_frame, text="Ingreso de vectores", style="Header.TLabel").pack(anchor="w", pady=(0,6))
        
        # Canvas para vectores
        self.vector_canvas = tk.Canvas(input_frame, highlightthickness=0)
        self.vector_frame = ttk.Frame(self.vector_canvas)
        self.vector_scroll_y = ttk.Scrollbar(input_frame, orient="vertical", command=self.vector_canvas.yview)
        self.vector_canvas.configure(yscrollcommand=self.vector_scroll_y.set)
        self.vector_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vector_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.vector_canvas_window = self.vector_canvas.create_window((0, 0), window=self.vector_frame, anchor="nw")
        self.vector_frame.bind("<Configure>", lambda e: self.vector_canvas.configure(scrollregion=self.vector_canvas.bbox("all")))
        self.vector_canvas.bind("<Configure>", self._on_vector_canvas_resize)
        
        # Panel de resultados para vectores
        card_out_vec = ttk.Frame(vectores_frame, style="Card.TFrame")
        card_out_vec.pack(fill=tk.BOTH, expand=True, padx=10)
        out_vec = ttk.Frame(card_out_vec)
        out_vec.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        out_vec.columnconfigure(0, weight=1)
        out_vec.rowconfigure(1, weight=1)

        ttk.Label(out_vec, text="Resultados", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.txt_vectores = tk.Text(out_vec, wrap="word", height=12, font=("Consolas", 10))
        self.txt_vectores.grid(row=1, column=0, sticky="nsew", pady=(4,0))

        btns_vec = ttk.Frame(out_vec)
        btns_vec.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns_vec, text="Copiar resultado", command=self._copy_vector_output).pack(side=tk.LEFT)
        ttk.Button(btns_vec, text="Exportar pasos…", command=self._export_vector_output).pack(side=tk.LEFT, padx=(8,0))
        
        # Estado inicial para vectores
        self.var_dimension.set(3)
        self.var_num_vectores.set(3)
        self._render_vector_grid(3, 3)
    
    def _build_matrices_operations_tab(self):
        # Frame para la pestaña de operaciones con matrices
        matrices_ops_frame = ttk.Frame(self.notebook)
        self.notebook.add(matrices_ops_frame, text="Matrices")
        
        # Panel de configuración
        card_cfg = ttk.Frame(matrices_ops_frame, style="Card.TFrame")
        card_cfg.pack(fill=tk.X, padx=10, pady=(10, 8))
        cfg = ttk.Frame(card_cfg)
        cfg.pack(fill=tk.X, padx=10, pady=8)
        
        self.var_mat_a_m = tk.IntVar()
        self.var_mat_a_n = tk.IntVar()
        self.var_mat_b_m = tk.IntVar()
        self.var_mat_b_n = tk.IntVar()
        
        ttk.Label(cfg, text="Matriz A:").grid(row=0, column=0, sticky="w")
        ttk.Label(cfg, text="Filas:").grid(row=0, column=1, sticky="w")
        self.sp_mat_a_m = ttk.Spinbox(cfg, from_=1, to=8, width=6, textvariable=self.var_mat_a_m, command=self._apply_matrix_size)
        self.sp_mat_a_m.grid(row=0, column=2, padx=(6,14))
        ttk.Label(cfg, text="Columnas:").grid(row=0, column=3, sticky="w")
        self.sp_mat_a_n = ttk.Spinbox(cfg, from_=1, to=8, width=6, textvariable=self.var_mat_a_n, command=self._apply_matrix_size)
        self.sp_mat_a_n.grid(row=0, column=4, padx=(6,14))
        
        ttk.Label(cfg, text="Matriz B:").grid(row=1, column=0, sticky="w")
        ttk.Label(cfg, text="Filas:").grid(row=1, column=1, sticky="w")
        self.sp_mat_b_m = ttk.Spinbox(cfg, from_=1, to=8, width=6, textvariable=self.var_mat_b_m, command=self._apply_matrix_size)
        self.sp_mat_b_m.grid(row=1, column=2, padx=(6,14))
        ttk.Label(cfg, text="Columnas:").grid(row=1, column=3, sticky="w")
        self.sp_mat_b_n = ttk.Spinbox(cfg, from_=1, to=8, width=6, textvariable=self.var_mat_b_n, command=self._apply_matrix_size)
        self.sp_mat_b_n.grid(row=1, column=4, padx=(6,14))
        
        ttk.Button(cfg, text="Crear matrices", command=self._apply_matrix_size).grid(row=0, column=5, padx=(8,0))
        ttk.Button(cfg, text="Ejemplo", command=self._load_matrix_example).grid(row=0, column=6, padx=(8,0))
        ttk.Button(cfg, text="Resolver", command=self._solve_matrices).grid(row=0, column=7, padx=8)
        ttk.Button(cfg, text="Limpiar", command=self._clear_matrices).grid(row=0, column=8, padx=(8,0))
        
        # Panel de operaciones
        card_ops = ttk.Frame(matrices_ops_frame, style="Card.TFrame")
        card_ops.pack(fill=tk.X, padx=10, pady=(0,8))
        ops = ttk.Frame(card_ops)
        ops.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(ops, text="Operaciones:", style="Header.TLabel").pack(anchor="w")
        
        ops_buttons = ttk.Frame(ops)
        ops_buttons.pack(fill=tk.X, pady=(4,0))
        
        ttk.Button(ops_buttons, text="Ecuación AX=B", command=self._matrix_equation).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Multiplicar A*B", command=self._multiply_matrices).pack(side=tk.LEFT, padx=(0,8))
        
        # Panel de entrada de matrices
        card_input = ttk.Frame(matrices_ops_frame, style="Card.TFrame")
        card_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,8))
        input_frame = ttk.Frame(card_input)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        ttk.Label(input_frame, text="Ingreso de matrices", style="Header.TLabel").pack(anchor="w", pady=(0,6))
        
        # Canvas para matrices
        self.matrix_canvas = tk.Canvas(input_frame, highlightthickness=0)
        self.matrix_frame = ttk.Frame(self.matrix_canvas)
        self.matrix_scroll_y = ttk.Scrollbar(input_frame, orient="vertical", command=self.matrix_canvas.yview)
        self.matrix_canvas.configure(yscrollcommand=self.matrix_scroll_y.set)
        self.matrix_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.matrix_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.matrix_canvas_window = self.matrix_canvas.create_window((0, 0), window=self.matrix_frame, anchor="nw")
        self.matrix_frame.bind("<Configure>", lambda e: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all")))
        self.matrix_canvas.bind("<Configure>", self._on_matrix_canvas_resize)
        
        # Panel de resultados para matrices
        card_out_mat = ttk.Frame(matrices_ops_frame, style="Card.TFrame")
        card_out_mat.pack(fill=tk.BOTH, expand=True, padx=10)
        out_mat = ttk.Frame(card_out_mat)
        out_mat.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        out_mat.columnconfigure(0, weight=1)
        out_mat.rowconfigure(1, weight=1)

        ttk.Label(out_mat, text="Resultados", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.txt_matrices = tk.Text(out_mat, wrap="word", height=12, font=("Consolas", 10))
        self.txt_matrices.grid(row=1, column=0, sticky="nsew", pady=(4,0))

        btns_mat = ttk.Frame(out_mat)
        btns_mat.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns_mat, text="Copiar resultado", command=self._copy_matrix_output).pack(side=tk.LEFT)
        ttk.Button(btns_mat, text="Exportar pasos…", command=self._export_matrix_output).pack(side=tk.LEFT, padx=(8,0))
        
        # Estado inicial para matrices
        self.var_mat_a_m.set(3)
        self.var_mat_a_n.set(3)
        self.var_mat_b_m.set(3)
        self.var_mat_b_n.set(3)
        self._render_matrix_grid(3, 3, 3, 3)

    # ---------- Helpers de UI ----------
    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
    
    def _on_vector_canvas_resize(self, event):
        self.vector_canvas.itemconfigure(self.vector_canvas_window, width=event.width)
    
    def _on_matrix_canvas_resize(self, event):
        self.matrix_canvas.itemconfigure(self.matrix_canvas_window, width=event.width)

    def _validate_int(self, new_value: str) -> bool:
        if new_value == "":
            return True
        try:
            v = int(new_value)
            return 1 <= v <= 99
        except ValueError:
            return False

    def _status(self, text: str):
        self.status.config(text=text)

    # ---------- Render de grid ----------
    def _render_grid(self, m: int, n: int):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.entries: List[List[ttk.Entry]] = []

        # Encabezados
        for j in range(n):
            ttk.Label(self.grid_frame, text=f"x{j+1}").grid(row=0, column=j, padx=4, pady=4)
        ttk.Label(self.grid_frame, text="| b").grid(row=0, column=n, padx=4, pady=4)

        # Celdas
        vcmd_num = (self.register(self._validate_number), "%P")
        for i in range(m):
            fila_entries: List[ttk.Entry] = []
            for j in range(n + 1):
                e = ttk.Entry(self.grid_frame, width=10, justify="center", validate="key", validatecommand=vcmd_num)
                e.grid(row=i + 1, column=j, padx=3, pady=3)
                e.insert(0, "0")
                fila_entries.append(e)
            self.entries.append(fila_entries)

        for j in range(n + 1):
            self.grid_frame.columnconfigure(j, weight=1)

        self.var_m.set(m); self.var_n.set(n)

    def _validate_number(self, new_value: str) -> bool:
        if new_value == "" or new_value == "-" or new_value == ".":
            return True
        # permitir decimales con "," o "."
        try:
            float(new_value.replace(",", "."))
            return True
        except ValueError:
            return False

    # ---------- Acciones ----------
    def _apply_size(self):
        m = max(1, int(self.var_m.get() or 1))
        n = max(1, int(self.var_n.get() or 1))
        self._render_grid(m, n)
        self._status(f"Tamaño matriz {m}×{n} creado.")

    def _read_matrix(self) -> List[List[float]]:
        mat: List[List[float]] = []
        for i in range(int(self.var_m.get())):
            fila = []
            for j in range(int(self.var_n.get()) + 1):
                val = self.entries[i][j].get().strip().replace(",", ".")
                if val in ("", "-", "."):
                    raise ValueError("Hay celdas vacías o con un número incompleto.")
                fila.append(float(val))
            mat.append(fila)
        return mat

    def _solve(self):
        try:
            matriz = self._read_matrix()
        except Exception as e:
            messagebox.showerror("Error de entrada", str(e))
            self._status("Corrige los datos y vuelve a intentar.")
            return

        sistema = SistemaLineal(matriz)
        salida = "=== Resolviendo por Eliminación Gaussiana ===\n\n" + sistema.eliminacion_gaussiana()
        self.txt.delete("1.0", tk.END)
        self.txt.insert(tk.END, salida)
        self._status("Cálculo finalizado.")

    def _clear_all(self):
        for fila in getattr(self, 'entries', []):
            for e in fila:
                e.delete(0, tk.END); e.insert(0, "0")
        self.txt.delete("1.0", tk.END)
        self._status("Campos limpiados.")

    def _load_example(self):
        self._render_grid(3, 3)
        datos = [
            [2, 1, -1, 8],
            [-3, -1, 2, -11],
            [-2, 1, 2, -3],
        ]
        for i in range(3):
            for j in range(4):
                e = self.entries[i][j]
                e.delete(0, tk.END)
                e.insert(0, str(datos[i][j]))
        self._status("Ejemplo cargado (3×3).")

    def _export(self):
        contenido = self.txt.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showinfo("Exportar", "No hay contenido para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar pasos",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
            initialfile="gauss_pasos.txt",
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Exportar", f"Archivo guardado en:\n{ruta}")
                self._status("Pasos exportados.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def _copy_output(self):
        contenido = self.txt.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear(); self.master.clipboard_append(contenido)
        self._status("Resultado copiado.")

    def _about(self):
        messagebox.showinfo(
            "Acerca de",
            "Calculadora de Álgebra Lineal\n"
            "Sistemas lineales, vectores y matrices\n"
            "Tkinter — sin librerías externas\n"
            "Atajos: Ctrl+S exportar, Ctrl+C copiar, Ctrl+L limpiar"
        )
    
    # ---------- Métodos para vectores ----------
    def _render_vector_grid(self, dimension: int, num_vectores: int):
        """Renderiza el grid para entrada de vectores"""
        for child in self.vector_frame.winfo_children():
            child.destroy()
        self.vector_entries: List[List[ttk.Entry]] = []
        
        # Encabezados
        for j in range(dimension):
            ttk.Label(self.vector_frame, text=f"x{j+1}").grid(row=0, column=j+1, padx=4, pady=4)
        
        # Vectores
        vcmd_num = (self.register(self._validate_number), "%P")
        for i in range(num_vectores):
            ttk.Label(self.vector_frame, text=f"v{i+1}").grid(row=i+1, column=0, padx=4, pady=4)
            fila_entries: List[ttk.Entry] = []
            for j in range(dimension):
                e = ttk.Entry(self.vector_frame, width=10, justify="center", validate="key", validatecommand=vcmd_num)
                e.grid(row=i+1, column=j+1, padx=3, pady=3)
                e.insert(0, "0")
                fila_entries.append(e)
            self.vector_entries.append(fila_entries)
        
        for j in range(dimension + 1):
            self.vector_frame.columnconfigure(j, weight=1)
    
    def _apply_vector_size(self):
        """Aplica el nuevo tamaño para vectores"""
        dim = max(2, int(self.var_dimension.get() or 2))
        num = max(1, int(self.var_num_vectores.get() or 1))
        self._render_vector_grid(dim, num)
        self._status(f"Vectores {num}×{dim} creados.")
    
    def _read_vectors(self) -> List[Vector]:
        """Lee los vectores ingresados"""
        vectores = []
        dim = int(self.var_dimension.get())
        num = int(self.var_num_vectores.get())
        
        for i in range(num):
            componentes = []
            for j in range(dim):
                val = self.vector_entries[i][j].get().strip().replace(",", ".")
                if val in ("", "-", "."):
                    raise ValueError(f"Vector v{i+1} tiene componentes vacías o incompletas.")
                componentes.append(float(val))
            vectores.append(Vector(componentes))
        
        return vectores
    
    def _verify_properties(self):
        """Verifica las propiedades del espacio vectorial"""
        try:
            vectores = self._read_vectors()
            resultado = OperacionesVectoriales.verificar_propiedades_espacio_vectorial(vectores)
            self.txt_vectores.delete("1.0", tk.END)
            self.txt_vectores.insert(tk.END, resultado)
            self._status("Verificación de propiedades completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en verificación de propiedades.")
    
    def _linear_combination(self):
        """Resuelve combinación lineal"""
        try:
            vectores = self._read_vectors()
            if len(vectores) < 2:
                messagebox.showwarning("Advertencia", "Se necesitan al menos 2 vectores para combinación lineal.")
                return
            
            # Pedir vector objetivo
            dim = vectores[0].dimension
            vector_objetivo = self._get_vector_objetivo(dim)
            if vector_objetivo is None:
                return
            
            resultado = OperacionesVectoriales.combinacion_lineal(vectores, vector_objetivo)
            self.txt_vectores.delete("1.0", tk.END)
            self.txt_vectores.insert(tk.END, resultado)
            self._status("Combinación lineal calculada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en combinación lineal.")
    
    def _vector_equation(self):
        """Resuelve ecuación vectorial"""
        try:
            vectores = self._read_vectors()
            if len(vectores) < 2:
                messagebox.showwarning("Advertencia", "Se necesitan al menos 2 vectores para ecuación vectorial.")
                return
            
            # Pedir vector objetivo
            dim = vectores[0].dimension
            vector_objetivo = self._get_vector_objetivo(dim)
            if vector_objetivo is None:
                return
            
            resultado = OperacionesVectoriales.ecuacion_vectorial(vectores, vector_objetivo)
            self.txt_vectores.delete("1.0", tk.END)
            self.txt_vectores.insert(tk.END, resultado)
            self._status("Ecuación vectorial resuelta.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en ecuación vectorial.")
    
    def _get_vector_objetivo(self, dimension: int) -> Vector:
        """Solicita al usuario el vector objetivo"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Vector objetivo")
        dialog.geometry("400x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        resultado = [None]
        
        ttk.Label(dialog, text=f"Ingrese el vector objetivo ({dimension} componentes):", font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        frame_entries = ttk.Frame(dialog)
        frame_entries.pack(pady=10)
        
        entries = []
        for i in range(dimension):
            ttk.Label(frame_entries, text=f"x{i+1}:").grid(row=0, column=i, padx=5)
            e = ttk.Entry(frame_entries, width=8, justify="center")
            e.grid(row=1, column=i, padx=5)
            e.insert(0, "0")
            entries.append(e)
        
        def ok_clicked():
            try:
                componentes = []
                for e in entries:
                    val = e.get().strip().replace(",", ".")
                    if val in ("", "-", "."):
                        raise ValueError("Componentes vacías o incompletas.")
                    componentes.append(float(val))
                resultado[0] = Vector(componentes)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        def cancel_clicked():
            dialog.destroy()
        
        frame_buttons = ttk.Frame(dialog)
        frame_buttons.pack(pady=20)
        ttk.Button(frame_buttons, text="Aceptar", command=ok_clicked).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_buttons, text="Cancelar", command=cancel_clicked).pack(side=tk.LEFT, padx=10)
        
        dialog.wait_window()
        return resultado[0]
    
    def _load_vector_example(self):
        """Carga un ejemplo de vectores"""
        self._render_vector_grid(3, 3)
        datos = [
            [1, 2, 3],
            [2, 1, 1],
            [3, 3, 4]
        ]
        for i in range(3):
            for j in range(3):
                e = self.vector_entries[i][j]
                e.delete(0, tk.END)
                e.insert(0, str(datos[i][j]))
        self._status("Ejemplo de vectores cargado (3×3).")
    
    def _clear_vectors(self):
        """Limpia todos los campos de vectores"""
        for fila in getattr(self, 'vector_entries', []):
            for e in fila:
                e.delete(0, tk.END)
                e.insert(0, "0")
        self.txt_vectores.delete("1.0", tk.END)
        self._status("Campos de vectores limpiados.")
    
    def _copy_vector_output(self):
        """Copia el resultado de vectores al portapapeles"""
        contenido = self.txt_vectores.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(contenido)
        self._status("Resultado de vectores copiado.")
    
    def _export_vector_output(self):
        """Exporta el resultado de vectores a archivo"""
        contenido = self.txt_vectores.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showinfo("Exportar", "No hay contenido para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar resultado de vectores",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
            initialfile="vectores_resultado.txt",
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Exportar", f"Archivo guardado en:\n{ruta}")
                self._status("Resultado de vectores exportado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
    
    def _solve_vectors(self):
        """Método resolver para vectores - ejecuta verificación de propiedades por defecto"""
        self._verify_properties()
    
    # ---------- Métodos para matrices ----------
    def _render_matrix_grid(self, ma: int, na: int, mb: int, nb: int):
        """Renderiza el grid para entrada de matrices A y B"""
        for child in self.matrix_frame.winfo_children():
            child.destroy()
        self.matrix_a_entries: List[List[ttk.Entry]] = []
        self.matrix_b_entries: List[List[ttk.Entry]] = []
        
        # Matriz A
        ttk.Label(self.matrix_frame, text="Matriz A", style="Header.TLabel").grid(row=0, column=0, columnspan=na, pady=(0,10))
        
        # Encabezados matriz A
        for j in range(na):
            ttk.Label(self.matrix_frame, text=f"Col {j+1}").grid(row=1, column=j+1, padx=4, pady=4)
        
        # Filas matriz A
        vcmd_num = (self.register(self._validate_number), "%P")
        for i in range(ma):
            ttk.Label(self.matrix_frame, text=f"Fila {i+1}").grid(row=i+2, column=0, padx=4, pady=4)
            fila_entries: List[ttk.Entry] = []
            for j in range(na):
                e = ttk.Entry(self.matrix_frame, width=8, justify="center", validate="key", validatecommand=vcmd_num)
                e.grid(row=i+2, column=j+1, padx=3, pady=3)
                e.insert(0, "0")
                fila_entries.append(e)
            self.matrix_a_entries.append(fila_entries)
        
        # Separador
        ttk.Separator(self.matrix_frame, orient="horizontal").grid(row=ma+2, column=0, columnspan=na+1, sticky="ew", pady=20)
        
        # Matriz B
        ttk.Label(self.matrix_frame, text="Matriz B", style="Header.TLabel").grid(row=ma+3, column=0, columnspan=nb, pady=(0,10))
        
        # Encabezados matriz B
        for j in range(nb):
            ttk.Label(self.matrix_frame, text=f"Col {j+1}").grid(row=ma+4, column=j+1, padx=4, pady=4)
        
        # Filas matriz B
        for i in range(mb):
            ttk.Label(self.matrix_frame, text=f"Fila {i+1}").grid(row=ma+5+i, column=0, padx=4, pady=4)
            fila_entries: List[ttk.Entry] = []
            for j in range(nb):
                e = ttk.Entry(self.matrix_frame, width=8, justify="center", validate="key", validatecommand=vcmd_num)
                e.grid(row=ma+5+i, column=j+1, padx=3, pady=3)
                e.insert(0, "0")
                fila_entries.append(e)
            self.matrix_b_entries.append(fila_entries)
        
        for j in range(max(na, nb) + 1):
            self.matrix_frame.columnconfigure(j, weight=1)
    
    def _apply_matrix_size(self):
        """Aplica el nuevo tamaño para matrices"""
        ma = max(1, int(self.var_mat_a_m.get() or 1))
        na = max(1, int(self.var_mat_a_n.get() or 1))
        mb = max(1, int(self.var_mat_b_m.get() or 1))
        nb = max(1, int(self.var_mat_b_n.get() or 1))
        self._render_matrix_grid(ma, na, mb, nb)
        self._status(f"Matrices A({ma}×{na}) y B({mb}×{nb}) creadas.")
    
    def _read_matrices(self) -> tuple[Matriz, Matriz]:
        """Lee las matrices A y B ingresadas"""
        ma = int(self.var_mat_a_m.get())
        na = int(self.var_mat_a_n.get())
        mb = int(self.var_mat_b_m.get())
        nb = int(self.var_mat_b_n.get())
        
        # Leer matriz A
        filas_a = []
        for i in range(ma):
            fila = []
            for j in range(na):
                val = self.matrix_a_entries[i][j].get().strip().replace(",", ".")
                if val in ("", "-", "."):
                    raise ValueError(f"Matriz A[{i+1},{j+1}] tiene valor vacío o incompleto.")
                fila.append(float(val))
            filas_a.append(fila)
        
        # Leer matriz B
        filas_b = []
        for i in range(mb):
            fila = []
            for j in range(nb):
                val = self.matrix_b_entries[i][j].get().strip().replace(",", ".")
                if val in ("", "-", "."):
                    raise ValueError(f"Matriz B[{i+1},{j+1}] tiene valor vacío o incompleto.")
                fila.append(float(val))
            filas_b.append(fila)
        
        return Matriz(filas_a), Matriz(filas_b)
    
    def _matrix_equation(self):
        """Resuelve la ecuación matricial AX = B"""
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.ecuacion_matricial(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Ecuación matricial AX=B resuelta.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en ecuación matricial.")
    
    def _multiply_matrices(self):
        """Multiplica las matrices A * B"""
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.multiplicacion_matrices(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Multiplicación de matrices completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en multiplicación de matrices.")
    
    def _solve_matrices(self):
        """Método resolver para matrices - ejecuta ecuación AX=B por defecto"""
        self._matrix_equation()
    
    def _load_matrix_example(self):
        """Carga un ejemplo de matrices"""
        self._render_matrix_grid(3, 3, 3, 2)
        
        # Matriz A 3x3
        datos_a = [
            [1, 2, 3],
            [2, 1, 1],
            [3, 3, 4]
        ]
        for i in range(3):
            for j in range(3):
                e = self.matrix_a_entries[i][j]
                e.delete(0, tk.END)
                e.insert(0, str(datos_a[i][j]))
        
        # Matriz B 3x2
        datos_b = [
            [1, 2],
            [3, 4],
            [5, 6]
        ]
        for i in range(3):
            for j in range(2):
                e = self.matrix_b_entries[i][j]
                e.delete(0, tk.END)
                e.insert(0, str(datos_b[i][j]))
        
        self._status("Ejemplo de matrices cargado (A: 3×3, B: 3×2).")
    
    def _clear_matrices(self):
        """Limpia todos los campos de matrices"""
        for fila in getattr(self, 'matrix_a_entries', []):
            for e in fila:
                e.delete(0, tk.END)
                e.insert(0, "0")
        for fila in getattr(self, 'matrix_b_entries', []):
            for e in fila:
                e.delete(0, tk.END)
                e.insert(0, "0")
        self.txt_matrices.delete("1.0", tk.END)
        self._status("Campos de matrices limpiados.")
    
    def _copy_matrix_output(self):
        """Copia el resultado de matrices al portapapeles"""
        contenido = self.txt_matrices.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(contenido)
        self._status("Resultado de matrices copiado.")
    
    def _export_matrix_output(self):
        """Exporta el resultado de matrices a archivo"""
        contenido = self.txt_matrices.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showinfo("Exportar", "No hay contenido para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar resultado de matrices",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
            initialfile="matrices_resultado.txt",
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Exportar", f"Archivo guardado en:\n{ruta}")
                self._status("Resultado de matrices exportado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AlgebraLinealGUI(root)
    root.mainloop()
