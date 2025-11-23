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
CORS(app)



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




@app.post("/api/matrices/add")
def api_add():
    data = request.json
    result = add_matrices(data["A"], data["B"])
    return jsonify({"result": result})


@app.post("/api/matrices/subtract")
def api_subtract():
    data = request.json
    result = subtract_matrices(data["A"], data["B"])
    return jsonify({"result": result})


@app.post("/api/matrices/multiply")
def api_multiply():
    data = request.json
    result = multiply_matrices(data["A"], data["B"])
    return jsonify({"result": result})


@app.post("/api/matrices/scalar")
def api_scalar():
    data = request.json
    result = scalar_multiply(data["matrix"], data["scalar"])
    return jsonify({"result": result})


@app.post("/api/matrices/transpose")
def api_transpose():
    data = request.json
    result = transpose_matrix(data["matrix"])
    return jsonify({"result": result})


@app.post("/api/matrices/inverse")
def api_inverse():
    data = request.json
    result = inverse_matrix(data["matrix"])
    return jsonify({"result": result})




@app.post("/api/systems/solve")
def api_solve_system():
    data = request.json
    sol, steps = solve_system(data["matrix"])
    return jsonify({"solution": sol, "steps": steps})



@app.post("/api/determinants/cofactors")
def api_det_cofactors():
    data = request.json
    return jsonify({"determinant": determinant_cofactors(data["matrix"])})


@app.post("/api/determinants/sarrus")
def api_det_sarrus():
    data = request.json
    return jsonify({"determinant": determinant_sarrus(data["matrix"])})




@app.post("/api/vectors/independence")
def api_vectors_independence():
    data = request.json
    result = check_independence(data["vectors"])
    return jsonify(result)


@app.post("/api/vectors/basis")
def api_vectors_basis():
    data = request.json
    result = check_basis(data["vectors"])
    return jsonify(result)




@app.post("/api/numerical/base10")
def api_num_base10():
    data = request.json
    return jsonify({"steps": decompose_base10(data["number"])})


@app.post("/api/numerical/base2")
def api_num_base2():
    data = request.json
    return jsonify({"steps": decompose_base2(data["number"])})


@app.get("/api/numerical/floating")
def api_float_demo():
    return jsonify(floating_point_demo())


if __name__ == "__main__":
    app.run(debug=True)
