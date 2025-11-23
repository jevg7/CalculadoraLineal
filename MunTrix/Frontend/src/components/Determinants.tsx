import { useState } from 'react';
import { MatrixVariable, Matrix } from '../App';
import { Calculator, AlertCircle, Sigma } from 'lucide-react';
import { formatNumber } from '../utils/fractions';
import { postJson } from '../api';

interface DeterminantsProps {
  variables: MatrixVariable[];
  useFractions: boolean;
}

type Method = 'cofactors' | 'sarrus' | 'lu';

export function Determinants({ variables, useFractions }: DeterminantsProps) {
  const [selectedMatrix, setSelectedMatrix] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [method, setMethod] = useState<Method>('cofactors');
  const [result, setResult] = useState<{
    determinant: number;
    steps: string[];
  } | null>(null);
  const [error, setError] = useState<string>('');

  const handleCalculate = async () => {
    setError('');
    setResult(null);

    if (!selectedMatrix) {
      setError('Seleccione una matriz');
      return;
    }

    const variable = variables.find(v => v.name === selectedMatrix);
    if (!variable?.matrix) {
      setError('La matriz seleccionada no está definida');
      return;
    }

    if (variable.rows !== variable.cols) {
      setError('La matriz debe ser cuadrada para calcular el determinante');
      return;
    }

    try {
      const data = await postJson<{
        determinant: number;
        steps: string[];
      }>('/api/determinant', {
        matrix: variable.matrix,
        method, 
      });

      setResult({
        determinant: data.determinant,
        steps: data.steps,
      });
    } catch (err) {
      console.error(err);
      setError('Error al comunicarse con el servidor.');
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
          {/* Panel Izquierdo: Configuración */}
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

            {result && (
              <div className="bg-gradient-to-br from-purple-900/30 via-purple-800/20 to-cyan-900/20 border border-purple-400/40 rounded-xl p-6 shadow-lg shadow-purple-500/20">
                <h3 className="text-sm mb-3 text-purple-300/90 uppercase tracking-wider">Resultado</h3>
                <div className="bg-[#0d0d12]/50 rounded-lg p-6 text-center border border-purple-500/30">
                  <div className="text-sm text-purple-400/70 mb-2">det({selectedMatrix})</div>
                  <div className="text-5xl text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-cyan-300">
                    {formatNumber(result.determinant, useFractions)}
                  </div>
                </div>
                
                {Math.abs(result.determinant) < 0.0001 && (
                  <div className="mt-4 bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 border border-yellow-500/30 rounded-lg p-3">
                    <p className="text-sm text-yellow-200">
                      ⚠️ Determinante ≈ 0: La matriz es singular (no invertible)
                    </p>
                  </div>
                )}
                
                {Math.abs(result.determinant) >= 0.0001 && (
                  <div className="mt-4 bg-gradient-to-br from-green-900/20 to-emerald-800/10 border border-green-500/30 rounded-lg p-3">
                    <p className="text-sm text-green-200">
                      ✓ Determinante ≠ 0: La matriz es invertible
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Panel Derecho: Procedimiento */}
          <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
            <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Procedimiento Detallado</h3>
            
            {error && (
              <div className="bg-gradient-to-br from-red-900/20 to-red-800/10 border border-red-500/30 rounded-xl p-4 mb-4 shadow-lg shadow-red-500/10">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
                  <p className="text-red-200">{error}</p>
                </div>
              </div>
            )}

            {result ? (
              <div className="bg-[#0d0d12]/50 rounded-lg p-4 font-mono text-xs overflow-auto max-h-[600px] space-y-3 border border-purple-500/20">
                {result.steps.map((step, i) => (
                  <div key={i} className="whitespace-pre text-purple-200/80">
                    {step}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-[#0d0d12]/30 rounded-lg p-8 text-center text-purple-400/30 border border-purple-500/10">
                <Calculator className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Los pasos del cálculo aparecerán aquí</p>
                <p className="text-sm mt-2">Seleccione una matriz y un método</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}