from flask import Flask, request, jsonify
from flask_cors import CORS

from core.matrices import (
    add_matrices,
    subtract_matrices,
    multiply_matrices,
    scalar_multiply,
    transpose_matrix,
    inverse_matrix
)
from core.systems import solve_linear_system
from core.determinants import determinant_cofactors, determinant_sarrus
from core.vectors import check_independence, check_basis
from core.numerical import decompose_base10, decompose_base2, floating_point_demo

app = Flask(__name__)


CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
    }
})


@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 200



@app.route("/")
def home():
    return jsonify({
        "message": "Backend activo correctamente.",
        "endpoints": [
            "/api/matrices/add",
            "/api/matrices/subtract",
            "/api/matrices/multiply",
            "/api/matrices/scalar",
            "/api/matrices/transpose",
            "/api/matrices/inverse",
            "/api/systems/solve",
            "/api/determinants/laplace",
            "/api/determinants/cofactors",
            "/api/determinants/sarrus",
            "/api/vectors/independence",
            "/api/vectors/basis",
            "/api/numerical/base10",
            "/api/numerical/base2",
            "/api/numerical/floating"
        ]
    })



@app.post("/api/matrix/operation")
def api_matrix_operation():
    data = request.json
    operation = data.get("operation")
    A = data.get("firstMatrix")
    B = data.get("secondMatrix")
    scalar = data.get("scalar")

    try:
        # Suma
        if operation == "add":
            result = add_matrices(A, B)
            return jsonify({"result": result, "steps": [], "error": None})

        # Resta
        elif operation == "subtract":
            result = subtract_matrices(A, B)
            return jsonify({"result": result, "steps": [], "error": None})

        # Multiplicación
        elif operation == "multiply":
            result = multiply_matrices(A, B)
            return jsonify({"result": result, "steps": [], "error": None})

        # Multiplicación por escalar
        elif operation == "scalar":
            result = scalar_multiply(A, scalar)
            return jsonify({"result": result, "steps": [], "error": None})

        # Transposición
        elif operation == "transpose":
            result = transpose_matrix(A)
            return jsonify({"result": result, "steps": [], "error": None})

        # Inversa
        elif operation == "inverse":
            result = inverse_matrix(A)
            return jsonify({"result": result, "steps": [], "error": None})

        else:
            return jsonify({"result": None, "steps": [], "error": "Operación no reconocida"}), 400

    except Exception as e:
        return jsonify({
            "result": None,
            "steps": [],
            "error": str(e)
        }), 400


@app.post("/api/systems/solve")
def api_solve_system():
    """
    Endpoint exacto para LinearSystems.tsx:
    recibe: { "matrix": [...] }
    responde: { "type": "...", "solution": [...], "steps": [...] }
    """
    try:
        data = request.json
        matrix = data.get("matrix")

        if matrix is None:
            return jsonify({"error": "No se envió ninguna matriz"}), 400

        result = solve_linear_system(matrix)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "type": "none",
            "solution": None,
            "steps": [f"Error interno en el servidor: {str(e)}"]
        }), 500


@app.post("/api/determinant")
def api_determinant():
    data = request.json
    matrix = data.get("matrix")
    method = data.get("method", "cofactors")

    if matrix is None:
        return jsonify({"error": "No se envió ninguna matriz"}), 400

    try:
        
        result = determinant_cofactors(matrix, method)

        return jsonify({
            "determinant": result["determinant"],
            "steps": result["steps"]
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "determinant": None,
            "steps": []
        }), 400



@app.post("/api/vectors/independence")
def api_vectors_independence():
    data = request.json

    vectors = data.get("vectors")
    dimension = data.get("dimension")

    if vectors is None or dimension is None:
        return jsonify({
            "error": "Se requieren 'vectors' y 'dimension'.",
            "details": []
        }), 400

    result = check_independence(vectors, dimension)
    return jsonify(result)


@app.post("/api/vectors/basis")
def api_vectors_basis():
    data = request.json

    vectors = data.get("vectors")
    dimension = data.get("dimension")

    if vectors is None or dimension is None:
        return jsonify({
            "error": "Se requieren 'vectors' y 'dimension'.",
            "details": []
        }), 400

    result = check_basis(vectors, dimension)
    return jsonify(result)


@app.route("/api/numerical/base10", methods=["POST", "OPTIONS"])
def api_num_base10():
    if request.method == "OPTIONS":
        return "", 200
    data = request.json
    return jsonify({"steps": decompose_base10(data["number"])})


@app.route("/api/numerical/base2", methods=["POST", "OPTIONS"])
def api_num_base2():
    if request.method == "OPTIONS":
        return "", 200
    data = request.json
    return jsonify({"steps": decompose_base2(data["number"])})


@app.route("/api/numerical/floating", methods=["GET", "OPTIONS"])
def api_float_demo():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify(floating_point_demo())



if __name__ == "__main__":
    app.run(debug=True)
