import { useState } from 'react';
import { MatrixVariable, Matrix } from '../App';
import { Play, AlertCircle, Download, ListChecks } from 'lucide-react';
import { formatNumber } from '../utils/fractions';
import { postJson } from '../api';

interface LinearSystemsProps {
  variables: MatrixVariable[];
  onEditVariable: (name: 'A' | 'B' | 'C' | 'D' | 'E') => void;
  useFractions: boolean;
}

type SolutionType = 'unique' | 'infinite' | 'none';

interface Solution {
  type: SolutionType;
  solution: number[] | null;
  steps: string[];
}

export function LinearSystems({ variables, onEditVariable, useFractions }: LinearSystemsProps) {
  const [selectedMatrix, setSelectedMatrix] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [customMatrix, setCustomMatrix] = useState<Matrix>([
    [2, 1, -1, 8],
    [-3, -1, 2, -11],
    [-2, 1, 2, -3]
  ]);
  const [useCustom, setUseCustom] = useState(true);
  const [solution, setSolution] = useState<Solution | null>(null);

  const handleSolve = async () => {
    let matrixToSolve: Matrix;

    if (useCustom) {
      matrixToSolve = customMatrix;
    } else {
      const selected = variables.find(v => v.name === selectedMatrix);
      if (!selected?.matrix) {
        return;
      }
      matrixToSolve = selected.matrix;
    }

    try {
      const data = await postJson<Solution>('/api/systems/solve', {
        matrix: matrixToSolve,
      });
      setSolution(data);
    } catch (err) {
      console.error(err);
      setSolution({
        type: 'none',
        solution: null,
        steps: ['Error al comunicarse con el servidor.'],
      });
    }
  };

  const handleCellChange = (row: number, col: number, value: string) => {
    const newMatrix: Matrix = customMatrix.map((r: number[], i: number) =>
  r.map((c: number, j: number) =>
    i === row && j === col ? parseFloat(value) || 0 : c
  )
);

  const loadFromVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E') => {
    const variable = variables.find(v => v.name === name);
    if (variable?.matrix) {
      setCustomMatrix(variable.matrix);
      setUseCustom(true);
    }
  };

  const availableMatrices = variables.filter(v => v.matrix !== null);

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8 pb-6 border-b border-purple-500/20">
          <div className="flex items-center gap-3 mb-2">
            <ListChecks className="w-8 h-8 text-purple-400" />
            <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Sistemas de Ecuaciones Lineales
            </h2>
          </div>
          <p className="text-purple-300/70">Resuelva sistemas usando el método de Gauss-Jordan</p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Panel Izquierdo: Entrada */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Fuente de Datos</h3>
              
              <div className="flex gap-2 mb-4">
                <button
                  onClick={() => setUseCustom(true)}
                  className={`flex-1 px-4 py-2 rounded-lg transition-all duration-200 ${
                    useCustom
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border border-purple-500/30 hover:bg-purple-900/40'
                  }`}
                >
                  Entrada Manual
                </button>
                <button
                  onClick={() => setUseCustom(false)}
                  className={`flex-1 px-4 py-2 rounded-lg transition-all duration-200 ${
                    !useCustom
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border border-purple-500/30 hover:bg-purple-900/40'
                  }`}
                >
                  Desde Memoria
                </button>
              </div>

              {!useCustom && (
                <div className="mb-4">
                  <label className="block text-sm mb-2 text-purple-300/70">Seleccionar Matriz</label>
                  <div className="flex gap-2 flex-wrap">
                    {availableMatrices.map((v) => (
                      <button
                        key={v.name}
                        onClick={() => setSelectedMatrix(v.name)}
                        className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                          selectedMatrix === v.name
                            ? 'bg-gradient-to-br from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                            : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40'
                        }`}
                      >
                        {v.name}
                        <span className="text-xs ml-1 opacity-70">({v.rows}×{v.cols})</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {useCustom && (
                <>
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm text-purple-300/70">Matriz Aumentada [A|b]</label>
                      <div className="flex gap-2">
                        {availableMatrices.map((v) => (
                          <button
                            key={v.name}
                            onClick={() => loadFromVariable(v.name)}
                            className="text-xs px-2 py-1 bg-purple-900/30 text-purple-300 rounded hover:bg-purple-900/50 transition-all duration-200 flex items-center gap-1 border border-purple-500/20"
                            title={`Cargar desde ${v.name}`}
                          >
                            <Download className="w-3 h-3" />
                            {v.name}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-purple-500/30 overflow-x-auto">
                      <div className="flex flex-col gap-2">
                        {customMatrix.map((row, i) => (
                          <div key={i} className="flex gap-2">
                            {row.map((cell, j) => (
                              <input
                                key={`${i}-${j}`}
                                type="number"
                                step="0.1"
                                value={cell}
                                onChange={(e) => handleCellChange(i, j, e.target.value)}
                                className={`w-16 px-2 py-1 bg-[#0a0a0f] border rounded text-center text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-purple-100 font-mono transition-all duration-200 ${
                                  j === row.length - 1 ? 'border-l-2 border-l-cyan-500 border-cyan-500/50' : 'border-purple-500/30'
                                }`}
                              />
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>
                    <p className="text-xs text-purple-400/50 mt-2">
                      La última columna representa el vector de términos independientes
                    </p>
                  </div>
                </>
              )}

              <button
                onClick={handleSolve}
                className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-purple-500/30"
              >
                <Play className="w-4 h-4" />
                Resolver Sistema
              </button>
            </div>

            {solution && solution.type === 'unique' && solution.solution && (
              <div className="bg-gradient-to-br from-green-900/20 to-emerald-800/10 border border-green-500/30 rounded-xl p-6 shadow-lg shadow-green-500/10">
                <h3 className="text-sm mb-4 text-green-300/90 uppercase tracking-wider">Solución Única</h3>
                <div className="space-y-2">
                  {solution.solution.map((val, i) => (
                    <div key={i} className="flex items-center gap-3 text-green-200">
                      <span className="w-8 font-mono">
                        x<sub>{i + 1}</sub>
                      </span>
                      <span>=</span>
                      <span className="px-3 py-1 bg-[#0d0d12]/50 rounded border border-green-500/30 font-mono">
                        {formatNumber(val, useFractions)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {solution && solution.type === 'infinite' && (
              <div className="bg-gradient-to-br from-cyan-900/20 to-cyan-800/10 border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-cyan-400 mt-0.5" />
                  <div>
                    <h3 className="text-sm mb-2 text-cyan-300/90">Infinitas Soluciones</h3>
                    <p className="text-sm text-cyan-200/70">
                      El sistema tiene variables libres. Existen infinitas soluciones.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {solution && solution.type === 'none' && (
              <div className="bg-gradient-to-br from-red-900/20 to-red-800/10 border border-red-500/30 rounded-xl p-6 shadow-lg shadow-red-500/10">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
                  <div>
                    <h3 className="text-sm mb-2 text-red-300/90">Sin Solución</h3>
                    <p className="text-sm text-red-200/70">
                      El sistema es inconsistente. No existe solución.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Panel Derecho: Log de Pasos */}
          <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
            <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Procedimiento (Gauss-Jordan)</h3>
            {solution ? (
              <div className="bg-[#0d0d12]/50 rounded-lg p-4 font-mono text-xs overflow-auto max-h-[600px] space-y-3 border border-purple-500/20">
                {solution.steps.map((step, i) => (
                  <div key={i} className="whitespace-pre text-purple-200/80">
                    {step}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-[#0d0d12]/30 rounded-lg p-8 text-center text-purple-400/30 border border-purple-500/10">
                Los pasos de resolución aparecerán aquí
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
