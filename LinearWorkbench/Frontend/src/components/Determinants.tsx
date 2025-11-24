import { useState } from 'react';
import { MatrixVariable, Matrix } from '../App';
import { Calculator, AlertCircle, Sigma } from 'lucide-react';
import { formatNumber } from '../utils/fractions';

const API_BASE = 'http://localhost:8000';

interface DeterminantsProps {
  variables: MatrixVariable[];
  useFractions: boolean;
}

type Method = 'cofactors' | 'sarrus' | 'cramer';

export function Determinants({ variables, useFractions }: DeterminantsProps) {
  const [selectedMatrix, setSelectedMatrix] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [method, setMethod] = useState<Method>('cofactors');
  const [result, setResult] = useState<{
    determinant?: number;
    steps: string[];
  } | null>(null);
  const [error, setError] = useState<string>('');

  // Método simplificado para 2×2: multiplicar diagonales y restar
  const calculateDeterminant2x2 = (m: Matrix, steps: string[], showDetails: boolean = true, methodName: string = 'MÉTODO PARA MATRIZ 2×2'): number => {
    if (showDetails) {
      steps.push('════════════════════════════════════════════');
      steps.push(`   ${methodName}`);
      steps.push('════════════════════════════════════════════');
      steps.push('');
      steps.push('Multiplicar diagonales y restar');
      steps.push('Matriz:');
      steps.push(formatMatrix(m));
      steps.push('');
      steps.push('Fórmula: det = (a·d) - (b·c)');
      steps.push('');
    }
    
    const a = m[0][0], b = m[0][1];
    const c = m[1][0], d = m[1][1];
    
    const diagonal_principal = a * d;
    const diagonal_secundaria = b * c;
    
    if (showDetails) {
      steps.push('Calcular diagonal principal (↘):');
      steps.push(`  Elementos: a = ${a}, d = ${d}`);
      steps.push(`  Producto: (${a}) × (${d}) = ${formatNumber(diagonal_principal, useFractions)}`);
      steps.push('');
      
      steps.push('Calcular diagonal secundaria (↙):');
      steps.push(`  Elementos: b = ${b}, c = ${c}`);
      steps.push(`  Producto: (${b}) × (${c}) = ${formatNumber(diagonal_secundaria, useFractions)}`);
      steps.push('');
      
      steps.push('Restar las diagonales:');
    }
    
    const det = diagonal_principal - diagonal_secundaria;
    
    if (showDetails) {
      steps.push(`  det = ${formatNumber(diagonal_principal, useFractions)} - ${formatNumber(diagonal_secundaria, useFractions)} = ${formatNumber(det, useFractions)}`);
      steps.push('');
      steps.push('════════════════════════════════════════════');
      steps.push(`  RESULTADO: det = ${formatNumber(det, useFractions)}`);
      steps.push('════════════════════════════════════════════');
    }
    
    return det;
  };

  // Método simplificado para 3×3: regla de Sarrus (versión mejorada para Sarrus)
  const calculateDeterminant3x3Sarrus = (m: Matrix, steps: string[], showDetails: boolean = true, methodName: string = 'REGLA DE SARRUS PARA MATRIZ 3×3'): number => {
    if (showDetails) {
      steps.push('════════════════════════════════════════════');
      steps.push(`   ${methodName}`);
      steps.push('════════════════════════════════════════════');
      steps.push('');
      steps.push('Paso 1: Matriz original:');
      steps.push(formatMatrix(m));
      steps.push('');
      steps.push('Paso 2: Extender la matriz (Regla de Sarrus)');
      steps.push('Repetir las primeras dos columnas a la derecha:');
      steps.push('');
    }
    
    // Mostrar matriz extendida con formato mejorado
    const extended = m.map((row, i) => {
      const values = [...row, row[0], row[1]];
      return '[ ' + values.map((v, j) => {
        const formatted = formatNumber(v, useFractions, 2).padStart(8);
        // Separar visualmente las columnas extendidas
        if (j === 3) return ' | ' + formatted;
        return formatted;
      }).join(' ') + ' ]';
    }).join('\n');
    
    if (showDetails) {
      steps.push(extended);
      steps.push('');
      steps.push('Nota: Las columnas después de | son repeticiones');
      steps.push('');
    }
    
    // Diagonales hacia la derecha (↘) - POSITIVAS
    const d1 = m[0][0] * m[1][1] * m[2][2];
    const d2 = m[0][1] * m[1][2] * m[2][0];
    const d3 = m[0][2] * m[1][0] * m[2][1];
    
    if (showDetails) {
      steps.push('Paso 3: Diagonales DESCENDENTES (↘) → SUMAR');
      steps.push('Estas diagonales van de izquierda a derecha:');
      steps.push('');
      steps.push(`  Diagonal 1: m[0][0] × m[1][1] × m[2][2]`);
      steps.push(`             ${m[0][0]} × ${m[1][1]} × ${m[2][2]} = ${formatNumber(d1, useFractions)}`);
      steps.push('');
      steps.push(`  Diagonal 2: m[0][1] × m[1][2] × m[2][0]`);
      steps.push(`             ${m[0][1]} × ${m[1][2]} × ${m[2][0]} = ${formatNumber(d2, useFractions)}`);
      steps.push('');
      steps.push(`  Diagonal 3: m[0][2] × m[1][0] × m[2][1]`);
      steps.push(`             ${m[0][2]} × ${m[1][0]} × ${m[2][1]} = ${formatNumber(d3, useFractions)}`);
      steps.push('');
      steps.push(`  Suma POSITIVA = ${formatNumber(d1, useFractions)} + ${formatNumber(d2, useFractions)} + ${formatNumber(d3, useFractions)}`);
      steps.push(`                = ${formatNumber(d1 + d2 + d3, useFractions)}`);
      steps.push('');
    }
    
    // Diagonales hacia la izquierda (↙) - NEGATIVAS
    const d4 = m[0][2] * m[1][1] * m[2][0];
    const d5 = m[0][0] * m[1][2] * m[2][1];
    const d6 = m[0][1] * m[1][0] * m[2][2];
    
    if (showDetails) {
      steps.push('Paso 4: Diagonales ASCENDENTES (↗) → RESTAR');
      steps.push('Estas diagonales van de derecha a izquierda:');
      steps.push('');
      steps.push(`  Diagonal 4: m[0][2] × m[1][1] × m[2][0]`);
      steps.push(`             ${m[0][2]} × ${m[1][1]} × ${m[2][0]} = ${formatNumber(d4, useFractions)}`);
      steps.push('');
      steps.push(`  Diagonal 5: m[0][0] × m[1][2] × m[2][1]`);
      steps.push(`             ${m[0][0]} × ${m[1][2]} × ${m[2][1]} = ${formatNumber(d5, useFractions)}`);
      steps.push('');
      steps.push(`  Diagonal 6: m[0][1] × m[1][0] × m[2][2]`);
      steps.push(`             ${m[0][1]} × ${m[1][0]} × ${m[2][2]} = ${formatNumber(d6, useFractions)}`);
      steps.push('');
      steps.push(`  Suma NEGATIVA = ${formatNumber(d4, useFractions)} + ${formatNumber(d5, useFractions)} + ${formatNumber(d6, useFractions)}`);
      steps.push(`                = ${formatNumber(d4 + d5 + d6, useFractions)}`);
      steps.push('');
    }
    
    const det = (d1 + d2 + d3) - (d4 + d5 + d6);
    
    if (showDetails) {
      steps.push('Paso 5: Aplicar la fórmula de Sarrus');
      steps.push('');
      steps.push('  det = (Suma Positiva) - (Suma Negativa)');
      steps.push('');
      steps.push(`  det = ${formatNumber(d1 + d2 + d3, useFractions)} - (${formatNumber(d4 + d5 + d6, useFractions)})`);
      steps.push(`  det = ${formatNumber(d1 + d2 + d3, useFractions)} - ${formatNumber(d4 + d5 + d6, useFractions)}`);
      steps.push(`  det = ${formatNumber(det, useFractions)}`);
      steps.push('');
      steps.push('════════════════════════════════════════════');
      steps.push(`  ✓ RESULTADO FINAL: det = ${formatNumber(det, useFractions)}`);
      steps.push('════════════════════════════════════════════');
    }
    
    return det;
  };

  // Método simplificado para 3×3: versión original para Cramer
  const calculateDeterminant3x3Original = (m: Matrix, steps: string[], showDetails: boolean = true, methodName: string = 'REGLA DE SARRUS PARA MATRIZ 3×3'): number => {
    if (showDetails) {
      steps.push('════════════════════════════════════════════');
      steps.push(`   ${methodName}`);
      steps.push('════════════════════════════════════════════');
      steps.push('');
      steps.push('Matriz original:');
      steps.push(formatMatrix(m));
      steps.push('');
      steps.push('Extender la matriz:');
      steps.push('Repetir las primeras dos columnas a la derecha:');
    }
    
    // Mostrar matriz extendida
    const extended = m.map((row, i) => 
      '[ ' + [...row, row[0], row[1]].map(v => formatNumber(v, useFractions, 2).padStart(8)).join(' ') + ' ]'
    ).join('\n');
    
    if (showDetails) {
      steps.push(extended);
      steps.push('');
    }
    
    // Diagonales hacia la derecha (↘)
    const d1 = m[0][0] * m[1][1] * m[2][2];
    const d2 = m[0][1] * m[1][2] * m[2][0];
    const d3 = m[0][2] * m[1][0] * m[2][1];
    
    if (showDetails) {
      steps.push('Diagonales hacia la DERECHA (↘):');
      steps.push('Multiplicar elementos de cada diagonal:');
      steps.push(`  d1: ${m[0][0]} × ${m[1][1]} × ${m[2][2]} = ${formatNumber(d1, useFractions)}`);
      steps.push(`  d2: ${m[0][1]} × ${m[1][2]} × ${m[2][0]} = ${formatNumber(d2, useFractions)}`);
      steps.push(`  d3: ${m[0][2]} × ${m[1][0]} × ${m[2][1]} = ${formatNumber(d3, useFractions)}`);
      steps.push('');
      steps.push(`  Suma derecha = ${formatNumber(d1, useFractions)} + ${formatNumber(d2, useFractions)} + ${formatNumber(d3, useFractions)} = ${formatNumber(d1 + d2 + d3, useFractions)}`);
      steps.push('');
    }
    
    // Diagonales hacia la izquierda (↙)
    const d4 = m[0][2] * m[1][1] * m[2][0];
    const d5 = m[0][0] * m[1][2] * m[2][1];
    const d6 = m[0][1] * m[1][0] * m[2][2];
    
    if (showDetails) {
      steps.push('Diagonales hacia la IZQUIERDA (↙):');
      steps.push('Multiplicar elementos de cada diagonal:');
      steps.push(`  d4: ${m[0][2]} × ${m[1][1]} × ${m[2][0]} = ${formatNumber(d4, useFractions)}`);
      steps.push(`  d5: ${m[0][0]} × ${m[1][2]} × ${m[2][1]} = ${formatNumber(d5, useFractions)}`);
      steps.push(`  d6: ${m[0][1]} × ${m[1][0]} × ${m[2][2]} = ${formatNumber(d6, useFractions)}`);
      steps.push('');
      steps.push(`  Suma izquierda = ${formatNumber(d4, useFractions)} + ${formatNumber(d5, useFractions)} + ${formatNumber(d6, useFractions)} = ${formatNumber(d4 + d5 + d6, useFractions)}`);
      steps.push('');
    }
    
    const det = (d1 + d2 + d3) - (d4 + d5 + d6);
    
    if (showDetails) {
      steps.push('Calcular determinante:');
      steps.push(`  det = (suma derecha) - (suma izquierda)`);
      steps.push(`  det = ${formatNumber(d1 + d2 + d3, useFractions)} - ${formatNumber(d4 + d5 + d6, useFractions)} = ${formatNumber(det, useFractions)}`);
      steps.push('');
      steps.push('════════════════════════════════════════════');
      steps.push(`  RESULTADO: det = ${formatNumber(det, useFractions)}`);
      steps.push('════════════════════════════════════════════');
    }
    
    return det;
  };

  const calculateDeterminantCofactors = (matrix: Matrix, level: number, steps: string[]): number => {
    const n = matrix.length;
    
    if (n === 1) {
      return matrix[0][0];
    }
    
    if (n === 2) {
      return calculateDeterminant2x2(matrix, steps, level === 0);
    }
    
    if (level === 0) {
      steps.push('═══════════════════════════════════════════');
      steps.push('   EXPANSIÓN POR COFACTORES');
      steps.push('════════════════════════════════════════════');
      steps.push('');
      steps.push('Expandiendo por la primera fila');
      steps.push('Matriz:');
      steps.push(formatMatrix(matrix));
      steps.push('');
      steps.push('Fórmula: det(A) = Σ (-1)^(i+j) * a[i][j] * det(M[i][j])');
      steps.push('donde M[i][j] es el menor obtenido eliminando fila i y columna j');
      steps.push('');
    }
    
    let det = 0;
    let stepNum = 1;
    
    for (let j = 0; j < n; j++) {
      if (level === 0 && matrix[0][j] !== 0) {
        steps.push(`Cofactor C(0,${j}):`);
        steps.push(`  Elemento: a[0][${j}] = ${matrix[0][j]}`);
        steps.push(`  Signo: (-1)^(0+${j}) = ${Math.pow(-1, j) > 0 ? '+' : '-'}`);
      }
      
      const minor = getMinor(matrix, 0, j);
      const minorDet = calculateDeterminantCofactors(minor, level + 1, []);
      
      if (level === 0 && matrix[0][j] !== 0) {
        steps.push(`  Menor M(0,${j}):`);
        steps.push(formatMatrix(minor).split('\n').map(line => '    ' + line).join('\n'));
        steps.push(`  det(M(0,${j})) = ${formatNumber(minorDet, useFractions)}`);
        steps.push(`  Contribución: ${Math.pow(-1, j) > 0 ? '+' : '-'}${matrix[0][j]} × ${formatNumber(minorDet, useFractions)} = ${formatNumber(Math.pow(-1, j) * matrix[0][j] * minorDet, useFractions)}`);
        steps.push('');
        stepNum++;
      }
      
      const cofactor = Math.pow(-1, j) * matrix[0][j];
      det += cofactor * minorDet;
    }
    
    if (level === 0) {
      steps.push('════════════════════════════════════════════');
      steps.push(`  RESULTADO: det = ${formatNumber(det, useFractions)}`);
      steps.push('════════════════════════════════════════════');
    }
    
    return det;
  };

  const getMinor = (matrix: Matrix, row: number, col: number): Matrix => {
    return matrix
      .filter((_, i) => i !== row)
      .map(r => r.filter((_, j) => j !== col));
  };

  const formatMatrix = (matrix: number[][]): string => {
    return matrix.map(row => 
      '[ ' + row.map(v => formatNumber(v, useFractions, 2).padStart(8)).join(' ') + ' ]'
    ).join('\n');
  };

  const handleCalculate = async () => {
  setError('');
  setResult(null);

  if (!selectedMatrix) {
    setError('Seleccione una matriz');
    return;
  }

  const variable = variables.find(v => v.name === selectedMatrix);
  if (!variable || !variable.matrix) {
    setError('Matriz no encontrada');
    return;
  }

  if (variable.rows !== variable.cols) {
    setError('La matriz debe ser cuadrada');
    return;
  }

  if (method === 'sarrus' && variable.rows !== 3) {
    setError('El método de Sarrus solo funciona para matrices 3×3');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/determinants/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        matrix: variable.matrix,
        method,
      }),
    });

    const data = await res.json();

    if (data.error) {
      setError(data.error);
    }

    if (typeof data.determinant === 'number') {
      setResult({
        determinant: data.determinant,
        steps: data.steps ?? [],
      });
    } else {
      setResult(null);
    }
  } catch (err) {
    console.error(err);
    setError('Error al conectarse al backend.');
  }
};

  const availableMatrices = variables.filter(v => v.matrix !== null && v.rows === v.cols);

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8 pb-6 border-b border-purple-500/20">
          <div className="flex items-center gap-3 mb-2">
            <Sigma className="w-8 h-8 text-purple-400" />
            <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Determinantes
            </h2>
          </div>
          <p className="text-purple-300/70">Calcule determinantes usando diferentes métodos</p>
        </div>

        {availableMatrices.length === 0 && (
          <div className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 border border-yellow-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-yellow-500/10">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div>
                <p className="text-yellow-200 mb-2">No hay matrices cuadradas definidas</p>
                <p className="text-sm text-yellow-300/70">
                  Defina al menos una matriz cuadrada (n×n) en el sidebar para calcular determinantes.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Selección de Matriz</h3>
              
              <div className="mb-6">
                <label className="block text-sm mb-2 text-purple-300/70">Calcular Determinante de...</label>
                <div className="grid grid-cols-5 gap-2">
                  {['A', 'B', 'C', 'D', 'E'].map((name) => {
                    const variable = variables.find(v => v.name === name);
                    const isSquare = variable?.matrix && variable.rows === variable.cols;
                    const isAvailable = variable?.matrix !== null;

                    return (
                      <button
                        key={name}
                        onClick={() => isSquare && setSelectedMatrix(name as 'A' | 'B' | 'C' | 'D' | 'E')}
                        disabled={!isSquare}
                        className={`px-4 py-3 rounded-lg border transition-all duration-200 ${
                          selectedMatrix === name
                            ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                            : isSquare
                            ? 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40'
                            : 'bg-[#0d0d12]/30 text-purple-600/30 border-purple-500/10 cursor-not-allowed'
                        }`}
                      >
                        <div>{name}</div>
                        {isAvailable && (
                          <div className="text-xs mt-1 opacity-70">
                            {variable.rows}×{variable.cols}
                          </div>
                        )}
                        {!isAvailable && (
                          <div className="text-xs mt-1">-</div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="block text-sm mb-2 text-purple-300/70">Método de Cálculo</label>
                <div className="space-y-2">
                  <button
                    onClick={() => setMethod('cofactors')}
                    className={`w-full px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                      method === 'cofactors'
                        ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                        : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40'
                    }`}
                  >
                    <div className="mb-1">Expansión por Cofactores</div>
                    <div className="text-xs opacity-70">Método general para cualquier dimensión</div>
                  </button>
                  
                  <button
                    onClick={() => setMethod('sarrus')}
                    disabled={selectedMatrix && variables.find(v => v.name === selectedMatrix)?.rows !== 3}
                    className={`w-full px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                      method === 'sarrus'
                        ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                        : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 disabled:bg-[#0d0d12]/30 disabled:text-purple-600/30 disabled:cursor-not-allowed'
                    }`}
                  >
                    <div className="mb-1">Regla de Sarrus</div>
                    <div className="text-xs opacity-70">Solo para matrices 3×3</div>
                  </button>
                  
                  <button
                    onClick={() => setMethod('cramer')}
                    disabled={selectedMatrix && variables.find(v => v.name === selectedMatrix)?.rows !== 2 && variables.find(v => v.name === selectedMatrix)?.rows !== 3}
                    className={`w-full px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                      method === 'cramer'
                        ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                        : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 disabled:bg-[#0d0d12]/30 disabled:text-purple-600/30 disabled:cursor-not-allowed'
                    }`}
                  >
                    <div className="mb-1">Cramer</div>
                    <div className="text-xs opacity-70">Para matrices 2×2 o 3×3</div>
                  </button>
                </div>
              </div>

              <button
                onClick={handleCalculate}
                disabled={!selectedMatrix}
                className="w-full mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 disabled:from-gray-600 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-purple-500/30 disabled:shadow-none disabled:opacity-50"
              >
                <Calculator className="w-4 h-4" />
                Calcular Determinante
              </button>
            </div>
          </div>

          <div className="space-y-6">
            {error && (
              <div className="bg-gradient-to-br from-red-900/20 to-red-800/10 border border-red-500/30 rounded-xl p-6 shadow-lg shadow-red-500/10">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400" />
                  <p className="text-red-200">{error}</p>
                </div>
              </div>
            )}

            {result && (
              <>
                <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
                  <h3 className="text-lg mb-4 text-purple-300">Resultado</h3>
                  <div className="bg-gradient-to-r from-purple-900/30 to-cyan-900/30 border border-purple-500/30 rounded-lg p-4">
                    <p className="text-sm text-purple-300/70 mb-1">Determinante:</p>
                    <p className="text-4xl text-cyan-300 font-mono">
                      {formatNumber(result.determinant!, useFractions)}
                    </p>
                    {result.determinant === 0 && (
                      <p className="text-sm text-yellow-400 mt-2">
                        ⚠️ Matriz singular (no tiene inversa)
                      </p>
                    )}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
                  <h3 className="text-lg mb-4 text-purple-300">Procedimiento Detallado</h3>
                  <div className="bg-[#0d0d12]/50 rounded-lg p-4 font-mono text-xs overflow-auto max-h-[600px] space-y-1 border border-purple-500/20">
                    {result.steps.map((step, i) => (
                      <div key={i} className="whitespace-pre text-purple-200/80">
                        {step}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {!result && !error && (
              <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-8 shadow-lg shadow-purple-500/10">
                <div className="text-center text-purple-400/30">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Los resultados aparecerán aquí</p>
                  <p className="text-sm mt-2">Seleccione una matriz y un método</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}