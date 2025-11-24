from .common import Matrix, StepResult, format_matrix, clone_matrix


def solve_linear_system_gauss_jordan(augmented: Matrix) -> StepResult:
    if not augmented:
        return StepResult(steps=["Matriz vacía"], error="empty")

    steps: list[str] = []
    a = clone_matrix(augmented)
    n = len(a)
    m = len(a[0])

    steps.append("MÉTODO DE GAUSS-JORDAN SOBRE [A|b]")
    steps.append(format_matrix(a))
    steps.append("")

    current_row = 0
    for col in range(m - 1):
        if current_row >= n:
            break
        pivot = max(range(current_row, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-10:
            continue
        if pivot != current_row:
            a[current_row], a[pivot] = a[pivot], a[current_row]
        pv = a[current_row][col]
        for j in range(col, m):
            a[current_row][j] /= pv
        for r in range(n):
            if r == current_row:
                continue
            factor = a[r][col]
            for j in range(col, m):
                a[r][j] -= factor * a[current_row][j]
        current_row += 1

    steps.append("Forma escalonada reducida:")
    steps.append(format_matrix(a))
    steps.append("")

    # inconsistente?
    for i in range(n):
        if all(abs(v) < 1e-10 for v in a[i][: m - 1]) and abs(a[i][m - 1]) > 1e-10:
            steps.append(f"Fila {i+1}: 0 = {a[i][m - 1]} → sistema inconsistente")
            return StepResult(steps=steps, solution_type="none")

    # contar pivotes
    leading_cols = set()
    for i in range(n):
        for j in range(m - 1):
            if abs(a[i][j] - 1.0) < 1e-10 and all(abs(a[i][k]) < 1e-10 for k in range(j)):
                leading_cols.add(j)
                break

    num_vars = m - 1
    free_vars = num_vars - len(leading_cols)
    if free_vars > 0:
        steps.append("Hay variables libres → infinitas soluciones")
        return StepResult(steps=steps, solution_type="infinite")

    sol = [0.0] * num_vars
    for i in range(n):
        pivot_col = None
        for j in range(m - 1):
            if abs(a[i][j] - 1.0) < 1e-10 and all(abs(a[i][k]) < 1e-10 for k in range(j)):
                pivot_col = j
                break
        if pivot_col is not None:
            sol[pivot_col] = a[i][m - 1]

    for idx, val in enumerate(sol, start=1):
        steps.append(f"x{idx} = {val}")
    return StepResult(steps=steps, vector=sol, solution_type="unique")
