import { useState } from 'react';
import { MatrixVariable, Matrix } from '../App';
import { Plus, Minus, X as MultiplyIcon, Calculator, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { formatNumber } from '../utils/fractions';

const API_BASE = 'http://localhost:8000';

interface MatrixOperationsProps {
  variables: MatrixVariable[];
  onEditVariable: (name: 'A' | 'B' | 'C' | 'D' | 'E') => void;
  useFractions: boolean;
}

type Operation = 'add' | 'subtract' | 'multiply' | 'scalar' | 'transpose' | 'inverse';

export function MatrixOperations({ variables, onEditVariable, useFractions }: MatrixOperationsProps) {
  const [operation, setOperation] = useState<Operation>('multiply');
  const [firstMatrix, setFirstMatrix] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [secondMatrix, setSecondMatrix] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [scalar, setScalar] = useState<number>(2);
  const [result, setResult] = useState<Matrix | null>(null);
  const [steps, setSteps] = useState<string[]>([]);
  const [error, setError] = useState<string>('');

  const getMatrix = (name: 'A' | 'B' | 'C' | 'D' | 'E' | null): MatrixVariable | null => {
    if (!name) return null;
    return variables.find(v => v.name === name) || null;
  };

  const canPerformOperation = (): boolean => {
    const first = getMatrix(firstMatrix);
    const second = getMatrix(secondMatrix);

    if (operation === 'transpose' || operation === 'inverse') {
      return first !== null && first.matrix !== null;
    }

    if (operation === 'scalar') {
      return first !== null && first.matrix !== null;
    }

    if (!first?.matrix || !second?.matrix) return false;

    if (operation === 'add' || operation === 'subtract') {
      return first.rows === second.rows && first.cols === second.cols;
    }

    if (operation === 'multiply') {
      return first.cols === second.rows;
    }

    return false;
  };

 

const calculateOperation = async () => {
  setError('');
  setSteps([]);

  const first = getMatrix(firstMatrix);
  const second = getMatrix(secondMatrix);

  if (!canPerformOperation() || !first?.matrix) {
    setError('Operación no válida. Verifique las dimensiones de las matrices.');
    return;
  }

  try {
    const body: any = {
      operation,
      a: { data: first.matrix },
    };

    if (operation === 'add' || operation === 'subtract' || operation === 'multiply') {
      if (!second?.matrix) {
        setError('Seleccione una segunda matriz válida.');
        return;
      }
      body.b = { data: second.matrix };
    }

    if (operation === 'scalar') {
      body.scalar = scalar;
    }

    const res = await fetch(`${API_BASE}/matrix/operate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (data.error) {
      setError(data.error);
    }

    setSteps(data.steps ?? []);
    setResult(data.result ?? null);
  } catch (err) {
    console.error(err);
    setError('Error al conectarse al backend.');
  }
};


  const availableMatrices = variables.filter(v => v.matrix !== null);

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8 pb-6 border-b border-purple-500/20">
          <div className="flex items-center gap-3 mb-2">
            <Calculator className="w-8 h-8 text-purple-400" />
            <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Operaciones Matriciales
            </h2>
          </div>
          <p className="text-purple-300/70">Construya operaciones usando las variables guardadas en memoria</p>
        </div>

        {availableMatrices.length === 0 && (
          <div className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 border border-yellow-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-yellow-500/10">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div>
                <p className="text-yellow-200 mb-2">No hay matrices definidas</p>
                <p className="text-sm text-yellow-300/70">
                  Defina al menos una matriz en el sidebar para comenzar a realizar operaciones.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-6">
          {/* Panel Izquierdo: Constructor de Operaciones */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Tipo de Operación</h3>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setOperation('add')}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    operation === 'add'
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 hover:border-purple-400/50'
                  }`}
                >
                  <Plus className="w-4 h-4 mx-auto mb-1" />
                  <div className="text-xs">Suma</div>
                </button>
                <button
                  onClick={() => setOperation('subtract')}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    operation === 'subtract'
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 hover:border-purple-400/50'
                  }`}
                >
                  <Minus className="w-4 h-4 mx-auto mb-1" />
                  <div className="text-xs">Resta</div>
                </button>
                <button
                  onClick={() => setOperation('multiply')}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    operation === 'multiply'
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 hover:border-purple-400/50'
                  }`}
                >
                  <MultiplyIcon className="w-4 h-4 mx-auto mb-1" />
                  <div className="text-xs">Multiplicar</div>
                </button>
                <button
                  onClick={() => setOperation('scalar')}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    operation === 'scalar'
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 hover:border-purple-400/50'
                  }`}
                >
                  <Calculator className="w-4 h-4 mx-auto mb-1" />
                  <div className="text-xs">Escalar</div>
                </button>
                <button
                  onClick={() => setOperation('transpose')}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    operation === 'transpose'
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 hover:border-purple-400/50'
                  }`}
                >
                  <div className="text-sm mx-auto mb-1">T</div>
                  <div className="text-xs">Transponer</div>
                </button>
                <button
                  onClick={() => setOperation('inverse')}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    operation === 'inverse'
                      ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                      : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40 hover:border-purple-400/50'
                  }`}
                >
                  <div className="text-sm mx-auto mb-1">⁻¹</div>
                  <div className="text-xs">Inversa</div>
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Selección de Matrices</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm mb-2 text-purple-300/70">
                    {operation === 'scalar' ? 'Matriz' : 'Primera Matriz'}
                  </label>
                  <div className="flex gap-2">
                    {availableMatrices.map((v) => (
                      <button
                        key={v.name}
                        onClick={() => setFirstMatrix(v.name)}
                        className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                          firstMatrix === v.name
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

                {operation === 'scalar' && (
                  <div>
                    <label className="block text-sm mb-2 text-purple-300/70">Escalar</label>
                    <input
                      type="number"
                      step="0.1"
                      value={scalar}
                      onChange={(e) => setScalar(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 bg-[#0d0d12] border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-purple-100 transition-all duration-200"
                    />
                  </div>
                )}

                {(operation === 'add' || operation === 'subtract' || operation === 'multiply') && (
                  <div>
                    <label className="block text-sm mb-2 text-purple-300/70">Segunda Matriz</label>
                    <div className="flex gap-2">
                      {availableMatrices.map((v) => (
                        <button
                          key={v.name}
                          onClick={() => setSecondMatrix(v.name)}
                          className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                            secondMatrix === v.name
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
              </div>

              <button
                onClick={calculateOperation}
                disabled={!canPerformOperation()}
                className="w-full mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 disabled:from-gray-600 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-purple-500/30 disabled:shadow-none disabled:opacity-50"
              >
                <Calculator className="w-4 h-4" />
                Calcular
              </button>
            </div>
          </div>

          {/* Panel Derecho: Resultado y Pasos */}
          <div className="space-y-6">
            {error && (
              <div className="bg-gradient-to-br from-red-900/20 to-red-800/10 border border-red-500/30 rounded-xl p-4 shadow-lg shadow-red-500/10">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
                  <p className="text-red-200">{error}</p>
                </div>
              </div>
            )}

            {steps.length > 0 && (
              <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
                <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider">Procedimiento Paso a Paso</h3>
                <div className="space-y-2 bg-[#0d0d12]/50 rounded-lg p-4 max-h-[300px] overflow-y-auto">
                  {steps.map((step, i) => (
                    <div key={i} className="text-sm text-cyan-200/80">
                      {i + 1}. {step}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result && (
              <div className="bg-gradient-to-br from-green-900/20 to-emerald-800/10 border border-green-500/30 rounded-xl p-6 shadow-lg shadow-green-500/10">
                <h3 className="text-sm mb-4 text-green-300/90 uppercase tracking-wider">Resultado</h3>
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 overflow-x-auto">
                  <div className="inline-flex flex-col gap-2">
                    {result.map((row, i) => (
                      <div key={i} className="flex gap-3">
                        {row.map((val, j) => (
                          <span key={j} className="w-16 text-center text-green-200 font-mono">
                            {formatNumber(val, useFractions, 2)}
                          </span>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}