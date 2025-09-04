import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List

"""
Aplicación de una sola pieza (NO modular) con interfaz cuidada en Tkinter.
- Sin librerías externas (solo tkinter/ttk de la librería estándar).
- Calcula sistemas lineales por Eliminación Gaussiana con pivoteo parcial.
- UI con cabecera, secciones, validación de entradas, ayuda, exportar y copiar.

Ejecuta:  python gauss_gui.py
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
# Interfaz (Tkinter)
# ============================
class GaussGUI(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master.title("Sistemas Lineales — Eliminación Gaussiana")
        self.master.geometry("1060x640")
        self.master.minsize(900, 560)
        self.pack(fill=tk.BOTH, expand=True)

        self._init_style()
        self._build_menu()
        self._build_header()
        self._build_sections()
        self._bind_shortcuts()

        # Estado inicial
        self.var_m.set(3)
        self.var_n.set(3)
        self._render_grid(3, 3)
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

    def _build_sections(self):
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        # Panel de configuración
        card_cfg = ttk.Frame(content, style="Card.TFrame")
        card_cfg.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 8))
        cfg = ttk.Frame(card_cfg); cfg.pack(fill=tk.X, padx=10, pady=8)

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
        card_mat = ttk.Frame(content, style="Card.TFrame")
        card_mat.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0,8))
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
        card_out = ttk.Frame(content, style="Card.TFrame")
        card_out.grid(row=2, column=0, sticky="nsew", padx=0)
        out = ttk.Frame(card_out); out.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        out.columnconfigure(0, weight=1)
        out.rowconfigure(1, weight=1)

        ttk.Label(out, text="Pasos y solución", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.txt = tk.Text(out, wrap="word", height=12, font=("Consolas", 10))
        self.txt.grid(row=1, column=0, sticky="nsew", pady=(4,0))

        btns = ttk.Frame(out)
        btns.grid(row=2, column=0, sticky="e", pady=(6,0))
        ttk.Button(btns, text="Copiar resultado", command=self._copy_output).pack(side=tk.LEFT)
        ttk.Button(btns, text="Exportar pasos…", command=self._export).pack(side=tk.LEFT, padx=(8,0))

    # ---------- Helpers de UI ----------
    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

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
            "Calculadora de Sistemas Lineales (Gauss)\n"
            "Tkinter — sin librerías externas\n"
            "Atajos: Ctrl+S exportar, Ctrl+C copiar, Ctrl+L limpiar"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = GaussGUI(root)
    # Barra inferior de acciones rápidas
    toolbar = ttk.Frame(root)
    toolbar.pack(fill=tk.X, padx=12, pady=(0,10))
    ttk.Button(toolbar, text="Resolver", command=app._solve).pack(side=tk.LEFT)
    ttk.Button(toolbar, text="Ejemplo", command=app._load_example).pack(side=tk.LEFT, padx=(8,0))
    ttk.Button(toolbar, text="Limpiar", command=app._clear_all).pack(side=tk.LEFT, padx=(8,0))
    root.mainloop()
