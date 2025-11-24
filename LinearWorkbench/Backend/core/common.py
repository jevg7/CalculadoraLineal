from dataclasses import dataclass
from typing import List, Optional, Literal

Matrix = List[List[float]]
Vector = List[float]


@dataclass
class StepResult:
    steps: List[str]
    matrix: Optional[Matrix] = None
    vector: Optional[Vector] = None
    determinant: Optional[float] = None
    solution_type: Optional[Literal["unique", "infinite", "none"]] = None
    error: Optional[str] = None


def format_matrix(m: Matrix, decimals: int = 4) -> str:
    if not m:
        return "[ ]"
    return "\n".join(
        "[ " + " ".join(f"{v:.{decimals}f}".rjust(10) for v in row) + " ]"
        for row in m
    )


def clone_matrix(m: Matrix) -> Matrix:
    return [row[:] for row in m]
