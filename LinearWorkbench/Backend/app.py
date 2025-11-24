from typing import List, Optional, Literal
from fastapi import FastAPI
from pydantic import BaseModel

from core.matrixOperations import (
    add_matrices_with_steps,
    subtract_matrices_with_steps,
    multiply_matrices_with_steps,
    scalar_multiply_with_steps,
    transpose_with_steps,
    inverse_with_steps,
)
from core.linearSystems import solve_linear_system_gauss_jordan
from core.vectorLab import check_independence, check_basis
from core.determinants import determinant_with_steps
from core.numericalConcepts import (
    decompose_base10,
    decompose_base2,
    demonstrate_roundoff,
    demonstrate_truncation,
    demonstrate_propagation,
    solve_bisection,
    solve_false_position,
)


app = FastAPI(title="Numerical Lab API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class MatrixPayload(BaseModel):
    data: List[List[float]]


class MatrixOperationRequest(BaseModel):
    operation: Literal["add", "subtract", "multiply", "scalar", "transpose", "inverse"]
    a: MatrixPayload
    b: Optional[MatrixPayload] = None
    scalar: Optional[float] = None


class MatrixOperationResponse(BaseModel):
    result: Optional[List[List[float]]] = None
    steps: List[str]
    error: Optional[str] = None


class LinearSystemRequest(BaseModel):
    augmented: List[List[float]]


class LinearSystemResponse(BaseModel):
    solution_type: Optional[Literal["unique", "infinite", "none"]] = None
    solution: Optional[List[float]] = None
    steps: List[str]
    error: Optional[str] = None


class VectorsRequest(BaseModel):
    vectors: List[List[float]]


class VectorsResponse(BaseModel):
    steps: List[str]
    solution_type: Optional[str] = None
    error: Optional[str] = None


class DeterminantRequest(BaseModel):
    matrix: List[List[float]]
    method: Literal["cofactors", "sarrus", "cramer"] = "cofactors"


class DeterminantResponse(BaseModel):
    determinant: Optional[float] = None
    steps: List[str]
    error: Optional[str] = None


class DecompositionRequest(BaseModel):
    value: str


class NumericalRoundoffRequest(BaseModel):
    value: float
    n: int


class NumericalTruncationRequest(BaseModel):
    x: float
    max_terms: int


class NumericalPropagationRequest(BaseModel):
    a: float
    b: float


class BisectionRequest(BaseModel):
    expr: str
    a: float
    b: float
    tol: float = 1e-4
    max_iter: int = 50


class NumericalResponse(BaseModel):
    value: Optional[float] = None
    values: Optional[List[float]] = None
    steps: List[str]
    error: Optional[str] = None


@app.post("/matrix/operate", response_model=MatrixOperationResponse)
def matrix_operate(payload: MatrixOperationRequest):
    a = payload.a.data
    b = payload.b.data if payload.b else None

    if payload.operation in ("add", "subtract", "multiply") and b is None:
        return MatrixOperationResponse(steps=["Falta matriz B"], error="missing_b")
    if payload.operation == "scalar" and payload.scalar is None:
        return MatrixOperationResponse(steps=["Falta escalar"], error="missing_scalar")

    if payload.operation == "add":
        res = add_matrices_with_steps(a, b)          # type: ignore[arg-type]
    elif payload.operation == "subtract":
        res = subtract_matrices_with_steps(a, b)     # type: ignore[arg-type]
    elif payload.operation == "multiply":
        res = multiply_matrices_with_steps(a, b)     # type: ignore[arg-type]
    elif payload.operation == "scalar":
        res = scalar_multiply_with_steps(a, payload.scalar)  # type: ignore[arg-type]
    elif payload.operation == "transpose":
        res = transpose_with_steps(a)
    elif payload.operation == "inverse":
        res = inverse_with_steps(a)
    else:
        return MatrixOperationResponse(steps=["Operación no soportada"], error="unsupported")

    return MatrixOperationResponse(result=res.matrix, steps=res.steps, error=res.error)


@app.post("/linear-systems/solve", response_model=LinearSystemResponse)
def solve_linear_system_api(payload: LinearSystemRequest):
    res = solve_linear_system_gauss_jordan(payload.augmented)
    return LinearSystemResponse(
        solution_type=res.solution_type,
        solution=res.vector,
        steps=res.steps,
        error=res.error,
    )


@app.post("/vectors/independence", response_model=VectorsResponse)
def vectors_independence(payload: VectorsRequest):
    res = check_independence(payload.vectors)
    return VectorsResponse(steps=res.steps, solution_type=res.solution_type, error=res.error)


@app.post("/vectors/basis", response_model=VectorsResponse)
def vectors_basis(payload: VectorsRequest):
    res = check_basis(payload.vectors)
    return VectorsResponse(steps=res.steps, solution_type=res.solution_type, error=res.error)


@app.post("/determinants/calculate", response_model=DeterminantResponse)
def determinants_calculate(payload: DeterminantRequest):
    res = determinant_with_steps(payload.matrix, payload.method)
    return DeterminantResponse(determinant=res.determinant, steps=res.steps, error=res.error)


@app.post("/numerical/decompose/base10", response_model=NumericalResponse)
def numerical_decompose_base10(payload: DecompositionRequest):
    res = decompose_base10(payload.value)
    return NumericalResponse(steps=res.steps, error=res.error)


@app.post("/numerical/decompose/base2", response_model=NumericalResponse)
def numerical_decompose_base2(payload: DecompositionRequest):
    res = decompose_base2(payload.value)
    value = res.vector[0] if res.vector else None
    return NumericalResponse(values=res.vector, value=value, steps=res.steps, error=res.error)


@app.post("/numerical/errors/roundoff", response_model=NumericalResponse)
def numerical_roundoff(payload: NumericalRoundoffRequest):
    res = demonstrate_roundoff(payload.value, payload.n)
    return NumericalResponse(steps=res.steps, error=res.error)


@app.post("/numerical/errors/truncation", response_model=NumericalResponse)
def numerical_truncation(payload: NumericalTruncationRequest):
    res = demonstrate_truncation(payload.x, payload.max_terms)
    return NumericalResponse(steps=res.steps, error=res.error)


@app.post("/numerical/errors/propagation", response_model=NumericalResponse)
def numerical_propagation(payload: NumericalPropagationRequest):
    res = demonstrate_propagation(payload.a, payload.b)
    return NumericalResponse(steps=res.steps, error=res.error)


@app.post("/numerical/bisection", response_model=NumericalResponse)
def numerical_bisection(payload: BisectionRequest):
    res = solve_bisection(payload.expr, payload.a, payload.b, payload.tol, payload.max_iter)
    value = res.vector[0] if res.vector else None
    return NumericalResponse(value=value, steps=res.steps, error=res.error)

@app.post("/numerical/false-position", response_model=NumericalResponse)
def numerical_false_position(payload: BisectionRequest):
    res = solve_false_position(payload.expr, payload.a, payload.b, payload.tol, payload.max_iter)
    value = res.vector[0] if res.vector else None
    return NumericalResponse(
        value=value,
        steps=res.steps,
        error=res.error,
    )
@app.get("/")
def root():
    return {"message": "Numerical Lab API running"}
