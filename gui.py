import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, simpledialog
from typing import List, Tuple

# ==================================================
# === INICIO: CÓDIGO AÑADIDO ===
# ==================================================
#
# Importamos las clases de lógica desde tu archivo core.py
# Esto permite que la GUI llame a las funciones de cálculo.
#
try:
    from core import (
        SistemaLineal,
        Vector,
        OperacionesVectoriales,
        Matriz,
        OperacionesMatriciales,
        NotacionPosicional,
        ErroresNumericos,
        TallerNumPy
    )
except ImportError:
    messagebox.showerror(
        "Error Crítico",
        "No se pudo encontrar el archivo 'core.py'.\n\n"
        "Asegúrate de que 'core.py' esté en la misma carpeta que 'gui.py'."
    )
    exit()
# ==================================================
# === FIN: CÓDIGO AÑADIDO ===
# ==================================================


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
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        
        self._build_matrices_tab()
        self._build_vectores_tab()
        self._build_matrices_operations_tab()
        self._build_determinantes_tab()
        self._build_conceptos_tab()
    
    def _build_matrices_tab(self):
        matrices_frame = ttk.Frame(self.notebook)
        self.notebook.add(matrices_frame, text="Sistemas Lineales")
        
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
        
        self.var_m.set(3)
        self.var_n.set(3)
        self._render_grid(3, 3)

    def _check_linear_independence(self):
        try:
            vectores = self._read_vectors()
            resultado = OperacionesVectoriales.dependencia_independencia(vectores)
            self.txt_vectores.delete("1.0", tk.END)
            self.txt_vectores.insert(tk.END, resultado)
            self._status("Verificación de independencia lineal completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en verificación de independencia lineal.")
    
    
    def _build_vectores_tab(self):
        vectores_frame = ttk.Frame(self.notebook)
        self.notebook.add(vectores_frame, text="Vectores")
        
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
        ttk.Button(ops_buttons, text="Independencia lineal", command=self._check_linear_independence).pack(side=tk.LEFT, padx=(0,8))

        
        card_input = ttk.Frame(vectores_frame, style="Card.TFrame")
        card_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,8))
        input_frame = ttk.Frame(card_input)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        ttk.Label(input_frame, text="Ingreso de vectores", style="Header.TLabel").pack(anchor="w", pady=(0,6))
        
        self.vector_canvas = tk.Canvas(input_frame, highlightthickness=0)
        self.vector_frame = ttk.Frame(self.vector_canvas)
        self.vector_scroll_y = ttk.Scrollbar(input_frame, orient="vertical", command=self.vector_canvas.yview)
        self.vector_canvas.configure(yscrollcommand=self.vector_scroll_y.set)
        self.vector_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vector_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.vector_canvas_window = self.vector_canvas.create_window((0, 0), window=self.vector_frame, anchor="nw")
        self.vector_frame.bind("<Configure>", lambda e: self.vector_canvas.configure(scrollregion=self.vector_canvas.bbox("all")))
        self.vector_canvas.bind("<Configure>", self._on_vector_canvas_resize)
        
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
        
        self.var_dimension.set(3)
        self.var_num_vectores.set(3)
        self._render_vector_grid(3, 3)
    
    def _build_matrices_operations_tab(self):
        matrices_ops_frame = ttk.Frame(self.notebook)
        self.notebook.add(matrices_ops_frame, text="Matrices")
        
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
        
        card_ops = ttk.Frame(matrices_ops_frame, style="Card.TFrame")
        card_ops.pack(fill=tk.X, padx=10, pady=(0,8))
        ops = ttk.Frame(card_ops)
        ops.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(ops, text="Operaciones:", style="Header.TLabel").pack(anchor="w")
        
        ops_buttons = ttk.Frame(ops)
        ops_buttons.pack(fill=tk.X, pady=(4,0))
        
        ttk.Button(ops_buttons, text="Ecuación AX=B", command=self._matrix_equation).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Multiplicar A*B", command=self._multiply_matrices).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Sumar A+B", command=self._sum_matrices).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Restar A-B", command=self._subtract_matrices).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="A * escalar", command=self._multiply_by_scalar).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Transpuesta de A", command=self._transpose_matrix).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Verificar (A+B)ᵀ", command=self._verify_transpose_sum_property).pack(side=tk.LEFT, padx=(0,8))
        
        # ==================================================
        # === INICIO: CÓDIGO AÑADIDO PARA LA TAREA 6 ===
        # ==================================================
        ttk.Button(ops_buttons, text="Inversa de A", command=self._calculate_inverse).pack(side=tk.LEFT, padx=(0,8))
        # ==================================================
        # === FIN: CÓDIGO AÑADIDO PARA LA TAREA 6 ===
        # ==================================================
        
        # ==================================================
        # === INICIO: CÓDIGO AÑADIDO PARA LA TAREA 7 ===
        # ==================================================
        ttk.Button(ops_buttons, text="Verificar det(AB)", command=self._verify_det_multiplicative_matrices).pack(side=tk.LEFT, padx=(0,8))
        # ==================================================
        # === FIN: CÓDIGO AÑADIDO PARA LA TAREA 7 ===
        # ==================================================
        
        card_input = ttk.Frame(matrices_ops_frame, style="Card.TFrame")
        card_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,8))
        input_frame = ttk.Frame(card_input)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        ttk.Label(input_frame, text="Ingreso de matrices", style="Header.TLabel").pack(anchor="w", pady=(0,6))
        
        self.matrix_canvas = tk.Canvas(input_frame, highlightthickness=0)
        self.matrix_frame = ttk.Frame(self.matrix_canvas)
        self.matrix_scroll_y = ttk.Scrollbar(input_frame, orient="vertical", command=self.matrix_canvas.yview)
        self.matrix_canvas.configure(yscrollcommand=self.matrix_scroll_y.set)
        self.matrix_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.matrix_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.matrix_canvas_window = self.matrix_canvas.create_window((0, 0), window=self.matrix_frame, anchor="nw")
        self.matrix_frame.bind("<Configure>", lambda e: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all")))
        self.matrix_canvas.bind("<Configure>", self._on_matrix_canvas_resize)
        
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

        for j in range(n):
            ttk.Label(self.grid_frame, text=f"x{j+1}").grid(row=0, column=j, padx=4, pady=4)
        ttk.Label(self.grid_frame, text="| b").grid(row=0, column=n, padx=4, pady=4)

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
        for child in self.vector_frame.winfo_children():
            child.destroy()
        self.vector_entries: List[List[ttk.Entry]] = []
        
        for j in range(dimension):
            ttk.Label(self.vector_frame, text=f"x{j+1}").grid(row=0, column=j+1, padx=4, pady=4)
        
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
        dim = max(2, int(self.var_dimension.get() or 2))
        num = max(1, int(self.var_num_vectores.get() or 1))
        self._render_vector_grid(dim, num)
        self._status(f"Vectores {num}×{dim} creados.")
    
    def _read_vectors(self) -> List[Vector]:
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
        try:
            vectores = self._read_vectors()
            if len(vectores) < 2:
                messagebox.showwarning("Advertencia", "Se necesitan al menos 2 vectores para combinación lineal.")
                return
            
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
        try:
            vectores = self._read_vectors()
            if len(vectores) < 2:
                messagebox.showwarning("Advertencia", "Se necesitan al menos 2 vectores para ecuación vectorial.")
                return
            
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
        for fila in getattr(self, 'vector_entries', []):
            for e in fila:
                e.delete(0, tk.END)
                e.insert(0, "0")
        self.txt_vectores.delete("1.0", tk.END)
        self._status("Campos de vectores limpiados.")
    
    def _copy_vector_output(self):
        contenido = self.txt_vectores.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(contenido)
        self._status("Resultado de vectores copiado.")
    
    def _export_vector_output(self):
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
        self._verify_properties()
    
    # ---------- Métodos para matrices ----------
    def _render_matrix_grid(self, ma: int, na: int, mb: int, nb: int):
        for child in self.matrix_frame.winfo_children():
            child.destroy()
        self.matrix_a_entries: List[List[ttk.Entry]] = []
        self.matrix_b_entries: List[List[ttk.Entry]] = []
        
        ttk.Label(self.matrix_frame, text="Matriz A", style="Header.TLabel").grid(row=0, column=0, columnspan=na, pady=(0,10))
        
        for j in range(na):
            ttk.Label(self.matrix_frame, text=f"Col {j+1}").grid(row=1, column=j+1, padx=4, pady=4)
        
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
        
        ttk.Separator(self.matrix_frame, orient="horizontal").grid(row=ma+2, column=0, columnspan=na+1, sticky="ew", pady=20)
        
        ttk.Label(self.matrix_frame, text="Matriz B", style="Header.TLabel").grid(row=ma+3, column=0, columnspan=nb, pady=(0,10))
        
        for j in range(nb):
            ttk.Label(self.matrix_frame, text=f"Col {j+1}").grid(row=ma+4, column=j+1, padx=4, pady=4)
        
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
        ma = max(1, int(self.var_mat_a_m.get() or 1))
        na = max(1, int(self.var_mat_a_n.get() or 1))
        mb = max(1, int(self.var_mat_b_m.get() or 1))
        nb = max(1, int(self.var_mat_b_n.get() or 1))
        self._render_matrix_grid(ma, na, mb, nb)
        self._status(f"Matrices A({ma}×{na}) y B({mb}×{nb}) creadas.")
    
    def _read_matrices(self) -> tuple[Matriz, Matriz]:
        ma = int(self.var_mat_a_m.get())
        na = int(self.var_mat_a_n.get())
        mb = int(self.var_mat_b_m.get())
        nb = int(self.var_mat_b_n.get())
        
        filas_a = []
        for i in range(ma):
            fila = []
            for j in range(na):
                val = self.matrix_a_entries[i][j].get().strip().replace(",", ".")
                if val in ("", "-", "."):
                    raise ValueError(f"Matriz A[{i+1},{j+1}] tiene valor vacío o incompleto.")
                fila.append(float(val))
            filas_a.append(fila)
        
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
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.multiplicacion_matrices(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Multiplicación de matrices completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en multiplicación de matrices.")

    def _sum_matrices(self):
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.suma_matrices(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Suma de matrices completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en la suma de matrices.")

    def _subtract_matrices(self):
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.resta_matrices(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Resta de matrices completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en la resta de matrices.")

    def _multiply_by_scalar(self):
        try:
            escalar = simpledialog.askfloat("Entrada de escalar", "Ingrese el valor del escalar:", parent=self.master)
            if escalar is None:
                return

            matriz_a, _ = self._read_matrices()
            resultado = OperacionesMatriciales.multiplicacion_por_escalar(matriz_a, escalar)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Multiplicación por escalar completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en la multiplicación por escalar.")

    def _transpose_matrix(self):
        try:
            matriz_a, _ = self._read_matrices()
            resultado = OperacionesMatriciales.matriz_traspuesta(matriz_a)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Cálculo de la traspuesta completado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en el cálculo de la traspuesta.")

    def _verify_transpose_sum_property(self):
        """Verifica la propiedad (A+B)^T = A^T + B^T"""
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.verificar_propiedad_suma_traspuesta(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Verificación de propiedad completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error durante la verificación.")

    # ==================================================
    # === INICIO: CÓDIGO AÑADIDO PARA LA TAREA 6 ===
    # ==================================================
    def _calculate_inverse(self):
        """Calcula la inversa de la Matriz A usando Gauss-Jordan."""
        try:
            # _read_matrices() lee A y B, solo necesitamos A
            matriz_a, _ = self._read_matrices() 
            
            resultado = OperacionesMatriciales.inversa_gauss_jordan(matriz_a)
            
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Cálculo de inversa de A completado.")
            
        except ValueError as ve:
             # Errores de validación (celdas vacías, etc.)
            messagebox.showerror("Error de entrada", str(ve))
            self._status("Error en los datos de la Matriz A.")
        except Exception as e:
            # Otros errores (ej. dimensiones)
            messagebox.showerror("Error", str(e))
            self._status("Error durante el cálculo de la inversa.")
    # ==================================================
    # === FIN: CÓDIGO AÑADIDO PARA LA TAREA 6 ===
    # ==================================================

    def _solve_matrices(self):
        self._matrix_equation()
    
    def _verify_det_multiplicative_matrices(self):
        """Verifica la propiedad det(AB) = det(A) × det(B) desde la pestaña de Matrices."""
        try:
            matriz_a, matriz_b = self._read_matrices()
            resultado = OperacionesMatriciales.verificar_propiedad_multiplicativa(matriz_a, matriz_b)
            self.txt_matrices.delete("1.0", tk.END)
            self.txt_matrices.insert(tk.END, resultado)
            self._status("Propiedad multiplicativa verificada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en verificación de propiedad multiplicativa.")
    
    def _load_matrix_example(self):
        self._render_matrix_grid(3, 3, 3, 2)
        
        datos_a = [
            [1, 0, 5],
            [2, 1, 6],
            [3, 4, 0]
        ]
        for i in range(3):
            for j in range(3):
                e = self.matrix_a_entries[i][j]
                e.delete(0, tk.END)
                e.insert(0, str(datos_a[i][j]))
        
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
        contenido = self.txt_matrices.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(contenido)
        self._status("Resultado de matrices copiado.")
    
    def _export_matrix_output(self):
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
    
    # ==================================================
    # === INICIO: MÉTODOS GUI PARA TAREA 7 ===
    # ==================================================
    
    def _build_determinantes_tab(self):
        """Construye la pestaña de Determinantes."""
        determinantes_frame = ttk.Frame(self.notebook)
        self.notebook.add(determinantes_frame, text="Determinantes")
        
        card_cfg = ttk.Frame(determinantes_frame, style="Card.TFrame")
        card_cfg.pack(fill=tk.X, padx=10, pady=(10, 8))
        cfg = ttk.Frame(card_cfg)
        cfg.pack(fill=tk.X, padx=10, pady=8)
        
        self.var_det_n = tk.IntVar()
        
        ttk.Label(cfg, text="Matriz cuadrada A:").grid(row=0, column=0, sticky="w")
        ttk.Label(cfg, text="Tamaño (n×n):").grid(row=0, column=1, sticky="w")
        self.sp_det_n = ttk.Spinbox(cfg, from_=1, to=8, width=6, textvariable=self.var_det_n, command=self._apply_det_size)
        self.sp_det_n.grid(row=0, column=2, padx=(6,14))
        
        ttk.Button(cfg, text="Crear matriz", command=self._apply_det_size).grid(row=0, column=3, padx=(8,0))
        ttk.Button(cfg, text="Ejemplo", command=self._load_det_example).grid(row=0, column=4, padx=(8,0))
        ttk.Button(cfg, text="Limpiar", command=self._clear_det).grid(row=0, column=5, padx=(8,0))
        
        card_ops = ttk.Frame(determinantes_frame, style="Card.TFrame")
        card_ops.pack(fill=tk.X, padx=10, pady=(0,8))
        ops = ttk.Frame(card_ops)
        ops.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(ops, text="Métodos de cálculo:", style="Header.TLabel").pack(anchor="w")
        
        ops_buttons = ttk.Frame(ops)
        ops_buttons.pack(fill=tk.X, pady=(4,0))
        
        ttk.Button(ops_buttons, text="Método de Cramer", command=self._det_cramer).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Regla de Sarrus", command=self._det_sarrus).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(ops_buttons, text="Cofactores", command=self._det_cofactores).pack(side=tk.LEFT, padx=(0,8))
        
        ttk.Label(ops, text="Propiedades:", style="Header.TLabel").pack(anchor="w", pady=(10,0))
        
        props_buttons = ttk.Frame(ops)
        props_buttons.pack(fill=tk.X, pady=(4,0))
        
        ttk.Button(props_buttons, text="Verificar propiedades", command=self._verify_det_properties).pack(side=tk.LEFT, padx=(0,8))
        ttk.Button(props_buttons, text="Verificar det(AB)", command=self._verify_det_multiplicative).pack(side=tk.LEFT, padx=(0,8))
        
        card_input = ttk.Frame(determinantes_frame, style="Card.TFrame")
        card_input.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0,8))
        input_frame = ttk.Frame(card_input)
        input_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=8)
        
        ttk.Label(input_frame, text="Ingreso de matriz cuadrada A", style="Header.TLabel").pack(anchor="w", pady=(0,6))
        
        self.det_canvas = tk.Canvas(input_frame, highlightthickness=0, height=200)
        self.det_frame = ttk.Frame(self.det_canvas)
        self.det_scroll_y = ttk.Scrollbar(input_frame, orient="vertical", command=self.det_canvas.yview)
        self.det_canvas.configure(yscrollcommand=self.det_scroll_y.set)
        self.det_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.det_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.det_canvas_window = self.det_canvas.create_window((0, 0), window=self.det_frame, anchor="nw")
        self.det_frame.bind("<Configure>", lambda e: self.det_canvas.configure(scrollregion=self.det_canvas.bbox("all")))
        self.det_canvas.bind("<Configure>", self._on_det_canvas_resize)
        
        
        card_out_det = ttk.Frame(determinantes_frame, style="Card.TFrame")
        card_out_det.pack(fill=tk.BOTH, expand=True, padx=10)
        out_det = ttk.Frame(card_out_det)
        out_det.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        out_det.columnconfigure(0, weight=1)
        out_det.rowconfigure(1, weight=1)
        
        ttk.Label(out_det, text="Resultados", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.txt_determinantes = tk.Text(out_det, wrap="word", height=30, font=("Consolas", 10))
        self.txt_determinantes.grid(row=1, column=0, sticky="nsew", pady=(4,0))
        
        btns_det = ttk.Frame(out_det)
        btns_det.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns_det, text="Copiar resultado", command=self._copy_det_output).pack(side=tk.LEFT)
        ttk.Button(btns_det, text="Exportar pasos…", command=self._export_det_output).pack(side=tk.LEFT, padx=(8,0))
        
        self.var_det_n.set(3)
        self._render_det_grid(3)
    
    def _on_det_canvas_resize(self, event):
        self.det_canvas.itemconfigure(self.det_canvas_window, width=event.width)

    def _on_conceptos_canvas_resize(self, event):
        """Ajusta el ancho del frame interior al ancho del canvas."""
        self.conceptos_canvas.itemconfigure(self.conceptos_canvas_window, width=event.width)
    
    def _render_det_grid(self, n: int):
        """Renderiza la cuadrícula para ingresar una matriz cuadrada."""
        for child in self.det_frame.winfo_children():
            child.destroy()
        self.det_entries: List[List[ttk.Entry]] = []
        
        for j in range(n):
            ttk.Label(self.det_frame, text=f"Col {j+1}").grid(row=0, column=j+1, padx=4, pady=4)
        
        vcmd_num = (self.register(self._validate_number), "%P")
        for i in range(n):
            ttk.Label(self.det_frame, text=f"Fila {i+1}").grid(row=i+1, column=0, padx=4, pady=4)
            fila_entries: List[ttk.Entry] = []
            for j in range(n):
                e = ttk.Entry(self.det_frame, width=8, justify="center", validate="key", validatecommand=vcmd_num)
                e.grid(row=i+1, column=j+1, padx=3, pady=3)
                e.insert(0, "0")
                fila_entries.append(e)
            self.det_entries.append(fila_entries)
        
        for j in range(n + 1):
            self.det_frame.columnconfigure(j, weight=1)
    
    def _apply_det_size(self):
        n = max(1, int(self.var_det_n.get() or 1))
        self._render_det_grid(n)
        self._status(f"Matriz cuadrada {n}×{n} creada.")
    
    def _read_det_matrix(self) -> Matriz:
        """Lee la matriz cuadrada ingresada."""
        n = int(self.var_det_n.get())
        
        filas = []
        for i in range(n):
            fila = []
            for j in range(n):
                val = self.det_entries[i][j].get().strip().replace(",", ".")
                if val in ("", "-", "."):
                    raise ValueError(f"Matriz A[{i+1},{j+1}] tiene valor vacío o incompleto.")
                fila.append(float(val))
            filas.append(fila)
        
        return Matriz(filas)
    
    def _det_cramer(self):
        """Calcula el determinante usando el método de Cramer."""
        try:
            matriz_a = self._read_det_matrix()
            resultado = OperacionesMatriciales.determinante_cramer(matriz_a)
            self.txt_determinantes.delete("1.0", tk.END)
            self.txt_determinantes.insert(tk.END, resultado)
            self._status("Determinante por método de Cramer calculado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en cálculo de determinante.")
    
    def _det_sarrus(self):
        """Calcula el determinante usando la Regla de Sarrus."""
        try:
            matriz_a = self._read_det_matrix()
            resultado = OperacionesMatriciales.determinante_sarrus(matriz_a)
            self.txt_determinantes.delete("1.0", tk.END)
            self.txt_determinantes.insert(tk.END, resultado)
            self._status("Determinante por Regla de Sarrus calculado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en cálculo de determinante.")
    
    def _det_cofactores(self):
        """Calcula el determinante usando expansión por cofactores."""
        try:
            matriz_a = self._read_det_matrix()
            resultado = OperacionesMatriciales.determinante_cofactores(matriz_a)
            self.txt_determinantes.delete("1.0", tk.END)
            self.txt_determinantes.insert(tk.END, resultado)
            self._status("Determinante por cofactores calculado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en cálculo de determinante.")
    
    def _verify_det_properties(self):
        """Verifica las propiedades del determinante."""
        try:
            matriz_a = self._read_det_matrix()
            resultado = OperacionesMatriciales.verificar_propiedades_determinante(matriz_a)
            self.txt_determinantes.delete("1.0", tk.END)
            self.txt_determinantes.insert(tk.END, resultado)
            self._status("Propiedades del determinante verificadas.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en verificación de propiedades.")
    
    def _verify_det_multiplicative(self):
        """Verifica la propiedad det(AB) = det(A) × det(B)."""
        try:
            # Necesitamos leer también la matriz B de la pestaña de Matrices
            # Por simplicidad, usaremos un diálogo para ingresar B
            matriz_a = self._read_det_matrix()
            
            # Crear diálogo para ingresar matriz B
            dialog = tk.Toplevel(self.master)
            dialog.title("Matriz B para verificar det(AB)")
            dialog.geometry("500x300")
            dialog.transient(self.master)
            dialog.grab_set()
            
            resultado = [None]
            
            ttk.Label(dialog, text=f"Ingrese matriz B cuadrada (debe ser {matriz_a.n}×{matriz_a.n}):", 
                     font=("Segoe UI", 10, "bold")).pack(pady=10)
            
            frame_b = ttk.Frame(dialog)
            frame_b.pack(pady=10)
            
            b_entries = []
            for i in range(matriz_a.n):
                fila_entries = []
                for j in range(matriz_a.n):
                    e = ttk.Entry(frame_b, width=6, justify="center")
                    e.grid(row=i, column=j, padx=3, pady=3)
                    e.insert(0, "0")
                    fila_entries.append(e)
                b_entries.append(fila_entries)
            
            def ok_clicked():
                try:
                    filas_b = []
                    for i in range(matriz_a.n):
                        fila = []
                        for j in range(matriz_a.n):
                            val = b_entries[i][j].get().strip().replace(",", ".")
                            if val in ("", "-", "."):
                                raise ValueError(f"Matriz B[{i+1},{j+1}] tiene valor vacío o incompleto.")
                            fila.append(float(val))
                        filas_b.append(fila)
                    resultado[0] = Matriz(filas_b)
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
            
            if resultado[0] is None:
                return
            
            matriz_b = resultado[0]
            res = OperacionesMatriciales.verificar_propiedad_multiplicativa(matriz_a, matriz_b)
            self.txt_determinantes.delete("1.0", tk.END)
            self.txt_determinantes.insert(tk.END, res)
            self._status("Propiedad multiplicativa verificada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status("Error en verificación de propiedad multiplicativa.")
    
    def _load_det_example(self):
        """Carga un ejemplo de matriz 3×3."""
        self._render_det_grid(3)
        datos = [
            [2, 1, -1],
            [-3, -1, 2],
            [-2, 1, 2]
        ]
        for i in range(3):
            for j in range(3):
                e = self.det_entries[i][j]
                e.delete(0, tk.END)
                e.insert(0, str(datos[i][j]))
        self._status("Ejemplo de matriz 3×3 cargado.")
    
    def _clear_det(self):
        """Limpia los campos de la pestaña de determinantes."""
        for fila in getattr(self, 'det_entries', []):
            for e in fila:
                e.delete(0, tk.END)
                e.insert(0, "0")
        self.txt_determinantes.delete("1.0", tk.END)
        self._status("Campos de determinantes limpiados.")
    
    def _copy_det_output(self):
        """Copia el resultado de determinantes al portapapeles."""
        contenido = self.txt_determinantes.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(contenido)
        self._status("Resultado de determinantes copiado.")
    
    def _export_det_output(self):
        """Exporta el resultado de determinantes a un archivo."""
        contenido = self.txt_determinantes.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showinfo("Exportar", "No hay contenido para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar resultado de determinantes",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
            initialfile="determinantes_resultado.txt",
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Exportar", f"Archivo guardado en:\n{ruta}")
                self._status("Resultado de determinantes exportado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
    
    # ==================================================
    # === FIN: MÉTODOS GUI PARA TAREA 7 ===
    # ==================================================

    # ==================================================
    # === INICIO: MÉTODOS GUI PARA CONCEPTOS NUMÉRICOS ===
    # ==================================================
    
    def _build_conceptos_tab(self):
        """Construye la pestaña de Conceptos Numéricos."""
        conceptos_frame = ttk.Frame(self.notebook)
        self.notebook.add(conceptos_frame, text="Conceptos Numéricos")
        
        # --- Frame de Entradas (AHORA SCROLLABLE) ---
        # 1. Contenedor para el lienzo y la barra de scroll
        card_cfg_container = ttk.Frame(conceptos_frame, style="Card.TFrame")
        card_cfg_container.pack(fill=tk.X, padx=10, pady=(10, 8)) # Se empaqueta en la parte superior

        # 2. Lienzo (Canvas) y Barra de Scroll (Scrollbar)
        # Le damos una altura fija para que la ventana de salida siempre sea visible
        self.conceptos_canvas = tk.Canvas(card_cfg_container, highlightthickness=0, height=350)
        self.conceptos_scroll_y = ttk.Scrollbar(card_cfg_container, orient="vertical", command=self.conceptos_canvas.yview)
        self.conceptos_canvas.configure(yscrollcommand=self.conceptos_scroll_y.set)
        
        self.conceptos_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.conceptos_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3. Frame interno (el que realmente se "mueve" con el scroll)
        self.conceptos_scroll_frame = ttk.Frame(self.conceptos_canvas)
        self.conceptos_canvas_window = self.conceptos_canvas.create_window((0, 0), window=self.conceptos_scroll_frame, anchor="nw")
        
        # 4. Binds (eventos) para que el scroll sepa qué tan grande es el contenido
        self.conceptos_scroll_frame.bind("<Configure>", lambda e: self.conceptos_canvas.configure(scrollregion=self.conceptos_canvas.bbox("all")))
        self.conceptos_canvas.bind("<Configure>", self._on_conceptos_canvas_resize) # Añadiremos este método
        
        # ---
        # 5. CONTENIDO DE ENTRADA (exactamente el mismo que antes)
        #    Solo cambiamos 'card_cfg' por 'self.conceptos_scroll_frame'
        # ---
        cfg = ttk.Frame(self.conceptos_scroll_frame)
        cfg.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cfg, text="1. Notación Posicional", style="Header.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Base 10
        ttk.Label(cfg, text="Número (Base 10):").grid(row=1, column=0, sticky="e", padx=(5,10))
        self.entry_base10 = ttk.Entry(cfg, width=20)
        self.entry_base10.grid(row=1, column=1, sticky="w")
        self.entry_base10.insert(0, "254") # Ejemplo
        ttk.Button(cfg, text="Descomponer Base 10", command=self._run_base10).grid(row=1, column=2, padx=(10,0))
        
        # Base 2
        ttk.Label(cfg, text="Número (Base 2):").grid(row=2, column=0, sticky="e", padx=(5,10), pady=(10,0))
        self.entry_base2 = ttk.Entry(cfg, width=20)
        self.entry_base2.grid(row=2, column=1, sticky="w", pady=(10,0))
        self.entry_base2.insert(0, "1101") # Ejemplo
        ttk.Button(cfg, text="Descomponer Base 2", command=self._run_base2).grid(row=2, column=2, padx=(10,0), pady=(10,0))
        
        ttk.Separator(cfg, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew", pady=20)

        ttk.Label(cfg, text="2. Errores Numéricos y Punto Flotante", style="Header.TLabel").grid(row=4, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        ttk.Button(cfg, text="Mostrar Explicaciones de Errores", command=self._run_errores).grid(row=5, column=1, sticky="w")
        
        # --- Separador y Taller NumPy ---
        ttk.Separator(cfg, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=20)
        
        ttk.Label(cfg, text="3. Manejo de números flotantes y otros (NumPy)", style="Header.TLabel").grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # 4.1 Pérdida de Precisión
        ttk.Label(cfg, text="Número Grande (a):").grid(row=8, column=0, sticky="e", padx=(5,10), pady=(5,0))
        self.entry_taller_a = ttk.Entry(cfg, width=20)
        self.entry_taller_a.grid(row=8, column=1, sticky="w", pady=(5,0))
        self.entry_taller_a.insert(0, "1e20") # Sugerencia
        
        ttk.Label(cfg, text="Número Pequeño (b):").grid(row=9, column=0, sticky="e", padx=(5,10), pady=(5,0))
        self.entry_taller_b = ttk.Entry(cfg, width=20)
        self.entry_taller_b.grid(row=9, column=1, sticky="w", pady=(5,0))
        self.entry_taller_b.insert(0, "0.123") # Sugerencia
        
        ttk.Button(cfg, text="Probar (a+b)-a", command=self._run_taller_grande_pequeno).grid(row=9, column=2, padx=(10,0), pady=(5,0))

        # 4.2 Cancelación Catastrófica
        ttk.Label(cfg, text="Número 'c':").grid(row=10, column=0, sticky="e", padx=(5,10), pady=(5,0))
        self.entry_taller_c = ttk.Entry(cfg, width=20)
        self.entry_taller_c.grid(row=10, column=1, sticky="w", pady=(5,0))
        self.entry_taller_c.insert(0, "1.00000000000001") # Sugerencia
        
        ttk.Label(cfg, text="Número 'd':").grid(row=11, column=0, sticky="e", padx=(5,10), pady=(5,0))
        self.entry_taller_d = ttk.Entry(cfg, width=20)
        self.entry_taller_d.grid(row=11, column=1, sticky="w", pady=(5,0))
        self.entry_taller_d.insert(0, "1.0") # Sugerencia
        
        ttk.Button(cfg, text="Probar (c-d)", command=self._run_taller_cancelacion).grid(row=11, column=2, padx=(10,0), pady=(5,0))

        # 4.3 Demos
        ttk.Button(cfg, text="Mostrar Demos (float32, inf, nan)", command=self._run_taller_demos).grid(row=12, column=1, sticky="w", pady=(10,0))

        # --- Separador y Ejercicio Principal de Error ---
        ttk.Separator(cfg, orient="horizontal").grid(row=13, column=0, columnspan=3, sticky="ew", pady=20)
        
        ttk.Label(cfg, text="4. Ejercicio de Propagación de Error", style="Header.TLabel").grid(row=14, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        ttk.Label(cfg, text="Valor Verdadero (xv):").grid(row=15, column=0, sticky="e", padx=(5,10), pady=(5,0))
        self.entry_error_xv = ttk.Entry(cfg, width=20)
        self.entry_error_xv.grid(row=15, column=1, sticky="w", pady=(5,0))
        self.entry_error_xv.insert(0, "1.570796") # Ejemplo: Pi/2
        
        ttk.Label(cfg, text="Valor Aproximado (xa):").grid(row=16, column=0, sticky="e", padx=(5,10), pady=(5,0))
        self.entry_error_xa = ttk.Entry(cfg, width=20)
        self.entry_error_xa.grid(row=16, column=1, sticky="w", pady=(5,0))
        self.entry_error_xa.insert(0, "1.57") # Ejemplo: Aproximación
        
        ttk.Button(cfg, text="Calcular Errores", command=self._run_error_propagation).grid(row=16, column=2, padx=(10,0), pady=(5,0))
        
        # --- FIN DEL CONTENIDO DE ENTRADA ---

        # --- Frame de Salida (Se empaqueta *después* del de entrada) ---
        card_out_det = ttk.Frame(conceptos_frame, style="Card.TFrame")
        # Esto hace que la salida llene el *resto* del espacio disponible
        card_out_det.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10)) 
        out_det = ttk.Frame(card_out_det)
        out_det.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        out_det.columnconfigure(0, weight=1)
        out_det.rowconfigure(1, weight=1)
        
        ttk.Label(out_det, text="Resultados y Explicaciones", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.txt_conceptos = tk.Text(out_det, wrap="word", height=10, font=("Consolas", 10)) # Se reduce altura por defecto
        self.txt_conceptos.grid(row=1, column=0, sticky="nsew", pady=(4,0))
        
        btns_det = ttk.Frame(out_det)
        btns_det.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns_det, text="Copiar resultado", command=self._copy_conceptos_output).pack(side=tk.LEFT)
        ttk.Button(btns_det, text="Limpiar", command=self._clear_conceptos).pack(side=tk.LEFT, padx=(8,0))
        
        # Cargar un ejemplo inicial
        self._run_base10()

    def _run_base10(self):
        """Llama a la descomposición de base 10."""
        num_str = self.entry_base10.get().strip()
        resultado = NotacionPosicional.descomponer_base10(num_str)
        self.txt_conceptos.delete("1.0", tk.END)
        self.txt_conceptos.insert(tk.END, resultado)
        self._status("Descomposición Base 10 calculada.")

    def _run_base2(self):
        """Llama a la descomposición de base 2."""
        num_str = self.entry_base2.get().strip()
        resultado = NotacionPosicional.descomponer_base2(num_str)
        self.txt_conceptos.delete("1.0", tk.END)
        self.txt_conceptos.insert(tk.END, resultado)
        self._status("Descomposición Base 2 calculada.")

    def _run_errores(self):
        """Muestra las explicaciones de errores."""
        resultado = ErroresNumericos.get_explicaciones_errores()
        self.txt_conceptos.delete("1.0", tk.END)
        self.txt_conceptos.insert(tk.END, resultado)
        self._status("Explicaciones de errores mostradas.")

    def _clear_conceptos(self):
        """Limpia los campos de la pestaña de conceptos."""
        self.entry_base10.delete(0, tk.END)
        self.entry_base10.insert(0, "254")
        self.entry_base2.delete(0, tk.END)
        self.entry_base2.insert(0, "1101")
        
        # --- AÑADIR ESTAS LÍNEAS ---
        self.entry_taller_a.delete(0, tk.END)
        self.entry_taller_a.insert(0, "1e20")
        self.entry_taller_b.delete(0, tk.END)
        self.entry_taller_b.insert(0, "0.123")
        self.entry_taller_c.delete(0, tk.END)
        self.entry_taller_c.insert(0, "1.00000000000001")
        self.entry_taller_d.delete(0, tk.END)
        self.entry_taller_d.insert(0, "1.0")
        # --- FIN AÑADIR ---
        
        self.entry_error_xv.delete(0, tk.END)
        self.entry_error_xv.insert(0, "1.570796")
        self.entry_error_xa.delete(0, tk.END)
        self.entry_error_xa.insert(0, "1.57")
        
        self.txt_conceptos.delete("1.0", tk.END)
        self._status("Campos de conceptos limpiados.")
    
    def _copy_conceptos_output(self):
        """Copia el resultado de conceptos al portapapeles."""
        contenido = self.txt_conceptos.get("1.0", tk.END)
        if not contenido.strip():
            messagebox.showinfo("Copiar", "No hay contenido para copiar.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(contenido)
        self._status("Resultado de conceptos copiado.")
    
    def _run_taller_grande_pequeno(self):
        """Prueba la suma de un número grande y uno pequeño."""
        try:
            a_str = self.entry_taller_a.get().strip().replace(",", ".")
            b_str = self.entry_taller_b.get().strip().replace(",", ".")
            resultado = TallerNumPy.taller_grande_pequeno(a_str, b_str)
            self.txt_conceptos.delete("1.0", tk.END)
            self.txt_conceptos.insert(tk.END, resultado)
            self._status("Prueba (a+b)-a completada.")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la prueba: {e}")
            self._status("Error en Taller (a+b)-a.")
            
    def _run_taller_cancelacion(self):
        """Prueba la resta de números casi iguales."""
        try:
            c_str = self.entry_taller_c.get().strip().replace(",", ".")
            d_str = self.entry_taller_d.get().strip().replace(",", ".")
            resultado = TallerNumPy.taller_cancelacion(c_str, d_str)
            self.txt_conceptos.delete("1.0", tk.END)
            self.txt_conceptos.insert(tk.END, resultado)
            self._status("Prueba (c-d) completada.")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la prueba: {e}")
            self._status("Error en Taller (c-d).")
            
    def _run_taller_demos(self):
        """Llama a las demos de NumPy que no usan entrada."""
        resultado = TallerNumPy.run_taller_demos()
        self.txt_conceptos.delete("1.0", tk.END)
        self.txt_conceptos.insert(tk.END, resultado)
        self._status("Demos de NumPy (float32, inf, nan) mostradas.")
    
    def _run_error_propagation(self):
        """Calcula el error absoluto, relativo y de propagación."""
        try:
            # Leer los valores de los campos de entrada
            xv_str = self.entry_error_xv.get().strip().replace(",", ".")
            xa_str = self.entry_error_xa.get().strip().replace(",", ".")
            
            if not xv_str or not xa_str:
                raise ValueError("Los campos no pueden estar vacíos.")
                
            xv = float(xv_str)
            xa = float(xa_str)
            
            # Llamar a la función de core.py
            resultado = ErroresNumericos.calcular_errores_propagacion(xv, xa)
            
            # Mostrar en el cuadro de texto
            self.txt_conceptos.delete("1.0", tk.END)
            self.txt_conceptos.insert(tk.END, resultado)
            self._status("Cálculo de propagación de error completado.")
            
        except ValueError as ve:
            messagebox.showerror("Error de entrada", f"Valor no válido: {ve}")
            self._status("Error: Ingrese números válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{e}")
            self._status("Error en el cálculo.")
    
    # ==================================================
    # === FIN: MÉTODOS GUI PARA CONCEPTOS NUMÉRICOS ===
    # ==================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AlgebraLinealGUI(root)
    root.mainloop()