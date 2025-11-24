import { useState } from 'react';
import { Trash2, AlertCircle, CheckCircle2, Box, Download } from 'lucide-react';
import { MatrixVariable } from '../App';

const API_BASE = 'http://localhost:8000';

type Vector = number[];

interface VectorLabProps {
  useFractions: boolean;
  variables: MatrixVariable[];
}

export function VectorLab({ useFractions, variables }: VectorLabProps) {
  const [vectors, setVectors] = useState<Vector[]>([]);
  const [dimension, setDimension] = useState(3);
  const [result, setResult] = useState<{
    type: 'independence' | 'combination' | 'base' | null;
    isIndependent?: boolean;
    isBasis?: boolean;
    details: string[];
  }>({ type: null, details: [] });

  const importGlobalVector = (name: 'A' | 'B' | 'C' | 'D' | 'E') => {
    const variable = variables.find(v => v.name === name);
    if (!variable) return;

    let vectorToImport: number[] | null = null;

    if (variable.isVector && variable.vector) {
      vectorToImport = variable.vector;
    } else if (variable.matrix) {
      if (variable.cols === 1) {
        vectorToImport = variable.matrix.map(row => row[0]);
      } else if (variable.rows === 1) {
        vectorToImport = variable.matrix[0];
      }
    }

    if (vectorToImport) {
      if (vectorToImport.length !== dimension) {
        setDimension(vectorToImport.length);
        const newVectors = vectors.map(v => {
          if (v.length < vectorToImport!.length) {
            return [...v, ...Array(vectorToImport!.length - v.length).fill(0)];
          } else if (v.length > vectorToImport!.length) {
            return v.slice(0, vectorToImport!.length);
          }
          return v;
        });
        setVectors([...newVectors, vectorToImport]);
      } else {
        setVectors([...vectors, vectorToImport]);
      }
      setResult({ type: null, details: [] });
    }
  };

  const removeVector = (index: number) => {
    setVectors(vectors.filter((_, i) => i !== index));
    setResult({ type: null, details: [] });
  };

  const clearAllVectors = () => {
    setVectors([]);
    setResult({ type: null, details: [] });
  };

  const checkIndependence = async () => {
  if (vectors.length === 0) {
    setResult({
      type: 'independence',
      isIndependent: false,
      details: ['No hay vectores para analizar'],
    });
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/vectors/independence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vectors }),
    });

    const data = await res.json();
    const isIndependent = data.solution_type === 'unique' && !data.error;

    setResult({
      type: 'independence',
      isIndependent,
      details: data.steps ?? [],
    });
  } catch (err) {
    console.error(err);
    setResult({
      type: 'independence',
      isIndependent: false,
      details: ['Error al conectarse al backend'],
    });
  }
};

  const checkBasis = async () => {
  if (vectors.length === 0) {
    setResult({
      type: 'base',
      isBasis: false,
      details: ['No hay vectores para analizar'],
    });
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/vectors/basis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vectors }),
    });

    const data = await res.json();
    const isBasis = !data.error;

    setResult({
      type: 'base',
      isBasis,
      details: data.steps ?? [],
    });
  } catch (err) {
    console.error(err);
    setResult({
      type: 'base',
      isBasis: false,
      details: ['Error al conectarse al backend'],
    });
  }
};

  const gaussianElimination = (matrix: number[][]): number[][] => {
    const m = matrix.length;
    const n = matrix[0]?.length || 0;
    
    let currentRow = 0;
    for (let col = 0; col < n && currentRow < m; col++) {
      let pivotRow = currentRow;
      for (let row = currentRow + 1; row < m; row++) {
        if (Math.abs(matrix[row][col]) > Math.abs(matrix[pivotRow][col])) {
          pivotRow = row;
        }
      }

      if (Math.abs(matrix[pivotRow][col]) < 0.0001) {
        continue;
      }

      if (pivotRow !== currentRow) {
        [matrix[currentRow], matrix[pivotRow]] = [matrix[pivotRow], matrix[currentRow]];
      }

      const pivot = matrix[currentRow][col];
      for (let j = 0; j < n; j++) {
        matrix[currentRow][j] /= pivot;
      }

      for (let row = currentRow + 1; row < m; row++) {
        const factor = matrix[row][col];
        for (let j = 0; j < n; j++) {
          matrix[row][j] -= factor * matrix[currentRow][j];
        }
      }

      currentRow++;
    }

    return matrix;
  };

  const formatMatrix = (matrix: number[][]): string => {
    return matrix.map(row => 
      '[ ' + row.map(v => v.toFixed(2).padStart(8)).join(' ') + ' ]'
    ).join('\n');
  };

  const availableVectors = variables.filter(v => 
    (v.isVector && v.vector) ||
    (v.matrix && (v.cols === 1 || v.rows === 1))
  );

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8 pb-6 border-b border-purple-500/20">
          <div className="flex items-center gap-3 mb-2">
            <Box className="w-8 h-8 text-purple-400" />
            <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Laboratorio de Vectores
            </h2>
          </div>
          <p className="text-purple-300/70">Analice independencia lineal y bases vectoriales usando vectores globales</p>
        </div>

        {availableVectors.length === 0 && (
          <div className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 border border-yellow-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-yellow-500/10">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div>
                <p className="text-yellow-200 mb-2">No hay vectores globales definidos</p>
                <p className="text-sm text-yellow-300/70 mb-3">
                  Para trabajar en el Laboratorio de Vectores, primero debe definir vectores en la memoria global.
                </p>
                <p className="text-sm text-yellow-300/70">
                  • Vaya a "Definir Variables" en el sidebar<br />
                  • Seleccione un slot (A-E)<br />
                  • Cambie el modo a "Vector" o defina una matriz columna (n×1) o fila (1×n)
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm text-purple-300/90 uppercase tracking-wider">Configuración</h3>
                <span className="text-xs text-purple-400/70 bg-purple-900/20 px-3 py-1 rounded-full border border-purple-500/20">
                  Espacio: ℝ{dimension}
                </span>
              </div>
              
              <p className="text-sm text-purple-300/70 mb-2">
                La dimensión del espacio se ajusta automáticamente al importar vectores.
              </p>
            </div>

            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <div className="flex items-center gap-2 mb-4">
                <Download className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm text-cyan-300/90 uppercase tracking-wider">Importar Vectores Globales</h3>
              </div>
              
              <p className="text-sm text-cyan-300/70 mb-4">
                Seleccione vectores desde la memoria global (A-E) para agregar al análisis:
              </p>

              <div className="grid grid-cols-5 gap-2 mb-4">
                {(['A', 'B', 'C', 'D', 'E'] as const).map((name) => {
                  const variable = variables.find(v => v.name === name);
                  const isAvailable = variable && (
                    (variable.isVector && variable.vector) ||
                    (variable.matrix && (variable.cols === 1 || variable.rows === 1))
                  );

                  return (
                    <button
                      key={name}
                      onClick={() => isAvailable && importGlobalVector(name)}
                      disabled={!isAvailable}
                      className={`px-3 py-3 rounded-lg border transition-all duration-200 ${
                        isAvailable
                          ? 'bg-cyan-900/30 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/50 hover:scale-105'
                          : 'bg-[#0d0d12]/30 text-cyan-600/30 border-cyan-500/10 cursor-not-allowed'
                      }`}
                      title={isAvailable ? `Importar ${variable.isVector ? 'vector' : 'matriz'} ${name}` : `Slot ${name} vacío`}
                    >
                      <div className="font-bold text-lg">{name}</div>
                      {isAvailable && variable && (
                        <div className="text-xs mt-1 opacity-70">
                          {variable.isVector ? `ℝ${variable.vectorSize}` : 
                           variable.cols === 1 ? `${variable.rows}×1` : `1×${variable.cols}`}
                        </div>
                      )}
                      {!isAvailable && (
                        <div className="text-xs mt-1">vacío</div>
                      )}
                    </button>
                  );
                })}
              </div>

              <div className="bg-cyan-900/10 border border-cyan-500/20 rounded-lg p-3">
                <p className="text-xs text-cyan-400/70">
                  💡 <span className="font-semibold">Tip:</span> Puede importar vectores (tipo Vector) o matrices columna/fila (n×1 o 1×n)
                </p>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm text-purple-300/90 uppercase tracking-wider">Vectores Importados</h3>
                {vectors.length > 0 && (
                  <button
                    onClick={clearAllVectors}
                    className="px-3 py-1.5 text-xs bg-red-900/30 border border-red-500/30 text-red-300 rounded-lg hover:bg-red-900/50 transition-all duration-200"
                  >
                    Limpiar Todo
                  </button>
                )}
              </div>

              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                {vectors.map((vector, i) => (
                  <div key={i} className="bg-[#0d0d12]/50 border border-purple-500/30 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-purple-300 flex items-center gap-2">
                        <span className="bg-purple-900/40 px-2 py-0.5 rounded text-xs">v<sub>{i + 1}</sub></span>
                        <span className="text-xs text-purple-400/60">ℝ{vector.length}</span>
                      </span>
                      <button
                        onClick={() => removeVector(i)}
                        className="p-1 text-purple-400/50 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      {vector.map((component, j) => (
                        <div
                          key={j}
                          className="w-16 px-2 py-1 bg-purple-950/30 border border-purple-500/30 rounded text-center text-sm text-purple-100 font-mono"
                        >
                          {component.toFixed(2)}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                {vectors.length === 0 && (
                  <div className="text-center py-12 text-purple-400/30">
                    <Download className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No hay vectores importados</p>
                    <p className="text-sm mt-2">Importe vectores globales para comenzar</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Herramientas de Análisis</h3>
              <div className="space-y-2">
                <button
                  onClick={checkIndependence}
                  disabled={vectors.length === 0}
                  className="w-full px-4 py-2.5 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 disabled:from-gray-600 disabled:to-gray-500 disabled:cursor-not-allowed disabled:opacity-50 text-sm shadow-lg shadow-purple-500/20"
                >
                  Verificar Independencia Lineal
                </button>
                <button
                  onClick={checkBasis}
                  disabled={vectors.length === 0}
                  className="w-full px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 transition-all duration-200 disabled:from-gray-600 disabled:to-gray-500 disabled:cursor-not-allowed disabled:opacity-50 text-sm shadow-lg shadow-cyan-500/20"
                >
                  Verificar si forman Base
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {result.type === 'independence' && (
              <div className={`border rounded-xl p-6 shadow-lg ${
                result.isIndependent
                  ? 'bg-gradient-to-br from-green-900/20 to-emerald-800/10 border-green-500/30 shadow-green-500/10'
                  : 'bg-gradient-to-br from-red-900/20 to-red-800/10 border-red-500/30 shadow-red-500/10'
              }`}>
                <div className="flex items-center gap-3 mb-4">
                  {result.isIndependent ? (
                    <>
                      <CheckCircle2 className="w-6 h-6 text-green-400" />
                      <h3 className="text-lg text-green-300">Linealmente Independientes (LI)</h3>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-6 h-6 text-red-400" />
                      <h3 className="text-lg text-red-300">Linealmente Dependientes (LD)</h3>
                    </>
                  )}
                </div>
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 font-mono text-xs overflow-auto max-h-[500px] space-y-2 border border-purple-500/20">
                  {result.details.map((detail, i) => (
                    <div key={i} className={`whitespace-pre ${result.isIndependent ? 'text-green-200/80' : 'text-red-200/80'}`}>
                      {detail}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.type === 'base' && (
              <div className={`border rounded-xl p-6 shadow-lg ${
                result.isBasis
                  ? 'bg-gradient-to-br from-green-900/20 to-emerald-800/10 border-green-500/30 shadow-green-500/10'
                  : 'bg-gradient-to-br from-red-900/20 to-red-800/10 border-red-500/30 shadow-red-500/10'
              }`}>
                <div className="flex items-center gap-3 mb-4">
                  {result.isBasis ? (
                    <>
                      <CheckCircle2 className="w-6 h-6 text-green-400" />
                      <h3 className="text-lg text-green-300">Es una Base de ℝ{dimension}</h3>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-6 h-6 text-red-400" />
                      <h3 className="text-lg text-red-300">No es una Base</h3>
                    </>
                  )}
                </div>
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 font-mono text-xs overflow-auto max-h-[500px] space-y-2 border border-purple-500/20">
                  {result.details.map((detail, i) => (
                    <div key={i} className={`whitespace-pre ${result.isBasis ? 'text-green-200/80' : 'text-red-200/80'}`}>
                      {detail}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!result.type && (
              <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-8 shadow-lg shadow-purple-500/10">
                <div className="text-center text-purple-400/30">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Los resultados del análisis aparecerán aquí</p>
                  <p className="text-sm mt-2">Importe vectores y seleccione una herramienta</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}