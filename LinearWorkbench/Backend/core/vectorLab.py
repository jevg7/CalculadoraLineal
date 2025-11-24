from .common import Matrix, Vector, StepResult, format_matrix, clone_matrix


def _matrix_from_vectors_as_columns(vectors: list[Vector]) -> Matrix:
    if not vectors:
        return []
    dim = len(vectors[0])
    return [[vec[i] for vec in vectors] for i in range(dim)]


def _gaussian_for_rank(m: Matrix) -> tuple[Matrix, int]:
    a = clone_matrix(m)
    rows = len(a)
    cols = len(a[0]) if a else 0
    rank = 0
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        pivot = max(range(r, rows), key=lambda i: abs(a[i][c]))
        if abs(a[pivot][c]) < 1e-10:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        for j in range(c, cols):
            a[r][j] /= pv
        for i in range(r + 1, rows):
            factor = a[i][c]
            for j in range(c, cols):
                a[i][j] -= factor * a[r][j]
        rank += 1
        r += 1
    return a, rank


def check_independence(vectors: list[Vector]) -> StepResult:
    if not vectors:
        return StepResult(steps=["No hay vectores"], error="no_vectors")

    dim = len(vectors[0])
    steps: list[str] = []
    steps.append(f"ANÁLISIS DE INDEPENDENCIA EN R^{dim}")
    m = _matrix_from_vectors_as_columns(vectors)
    steps.append("Matriz [v1 v2 ... vn]:")
    steps.append(format_matrix(m))

    reduced, rank = _gaussian_for_rank(m)
    steps.append("Forma escalonada:")
    steps.append(format_matrix(reduced))
    steps.append(f"Rango = {rank}, número de vectores = {len(vectors)}")

    indep = rank == len(vectors)
    if indep:
        steps.append("Conclusión: conjunto linealmente INDEPENDIENTE")
    else:
        steps.append("Conclusión: conjunto linealmente DEPENDIENTE")
    return StepResult(steps=steps, matrix=reduced, solution_type="unique" if indep else "infinite")


def check_basis(vectors: list[Vector]) -> StepResult:
    if not vectors:
        return StepResult(steps=["No hay vectores"], error="no_vectors")
    dim = len(vectors[0])
    steps: list[str] = []
    if len(vectors) != dim:
        steps.append(f"Hay {len(vectors)} vectores pero la dimensión es {dim} → no puede ser base")
        return StepResult(steps=steps, error="wrong_cardinality")
    m = _matrix_from_vectors_as_columns(vectors)
    reduced, rank = _gaussian_for_rank(m)
    steps.append("Forma escalonada:")
    steps.append(format_matrix(reduced))
    steps.append(f"Rango = {rank}")
    if rank == dim:
        steps.append("Conclusión: los vectores forman una BASE de R^n")
        return StepResult(steps=steps, matrix=reduced)
    else:
        steps.append("Conclusión: NO forman base")
        return StepResult(steps=steps, matrix=reduced, error="not_basis")
