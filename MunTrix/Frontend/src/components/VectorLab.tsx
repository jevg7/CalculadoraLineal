import { useState } from 'react';
import { Plus, Trash2, AlertCircle, CheckCircle2, Box } from 'lucide-react';
import { postJson } from '../api';

type Vector = number[];

interface VectorLabProps {
  useFractions: boolean;
}

type ResultType = 'independence' | 'base' | null;

interface AnalysisResult {
  type: ResultType;
  isIndependent?: boolean;
  isBasis?: boolean;
  details: string[];
}

export function VectorLab({ useFractions }: VectorLabProps) {
  const [vectors, setVectors] = useState<Vector[]>([
    [1, 2, 3],
    [2, 4, 6],
    [1, 0, 1]
  ]);
  const [dimension, setDimension] = useState(3);
  const [result, setResult] = useState<AnalysisResult>({ type: null, details: [] });
  const [loading, setLoading] = useState(false);

  const addVector = () => {
    setVectors([...vectors, Array(dimension).fill(0)]);
  };

  const removeVector = (index: number) => {
  setVectors(vectors.filter((_: Vector, i: number) => i !== index));
};

  const updateVector = (index: number, component: number, value: string) => {
  const newVectors = vectors.map((v: Vector, i: number) => {
    if (i === index) {
      const newV = [...v];
      newV[component] = parseFloat(value) || 0;
      return newV;
    }
    return v;
  });
  setVectors(newVectors);
};

  const changeDimension = (newDim: number) => {
  const validDim = Math.max(2, Math.min(10, newDim || 0));
  setDimension(validDim);

  const newVectors = vectors.map((v: Vector): Vector => {
    if (v.length < validDim) {
      return [...v, ...Array(validDim - v.length).fill(0)];
    } else if (v.length > validDim) {
      return v.slice(0, validDim);
    }
    return v;
  });

  setVectors(newVectors);
};

  const checkIndependence = async () => {
    if (vectors.length === 0) {
      setResult({ type: 'independence', details: ['No hay vectores para analizar'] });
      return;
    }

    setLoading(true);
    try {
      const data = await postJson<{
        isIndependent: boolean;
        details: string[];
        error?: string;
      }>('/api/vectors/independence', {
        vectors,
        dimension
      });

      if (data.error) {
        setResult({
          type: 'independence',
          isIndependent: false,
          details: [data.error, ...(data.details || [])]
        });
      } else {
        setResult({
          type: 'independence',
          isIndependent: data.isIndependent,
          details: data.details
        });
      }
    } catch (err) {
      console.error(err);
      setResult({
        type: 'independence',
        isIndependent: false,
        details: ['Error al comunicarse con el servidor.']
      });
    } finally {
      setLoading(false);
    }
  };

  const checkBasis = async () => {
    if (vectors.length === 0) {
      setResult({ type: 'base', details: ['No hay vectores para analizar'] });
      return;
    }

    setLoading(true);
    try {
      const data = await postJson<{
        isBasis: boolean;
        details: string[];
        error?: string;
      }>('/api/vectors/basis', {
        vectors,
        dimension
      });

      if (data.error) {
        setResult({
          type: 'base',
          isBasis: false,
          details: [data.error, ...(data.details || [])]
        });
      } else {
        setResult({
          type: 'base',
          isBasis: data.isBasis,
          details: data.details
        });
      }
    } catch (err) {
      console.error(err);
      setResult({
        type: 'base',
        isBasis: false,
        details: ['Error al comunicarse con el servidor.']
      });
    } finally {
      setLoading(false);
    }
  };

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
          <p className="text-purple-300/70">Analice independencia lineal, combinaciones y bases vectoriales</p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Panel Izquierdo: Entrada de Vectores */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm text-purple-300/90 uppercase tracking-wider">Configuración</h3>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm mb-2 text-purple-300/70">Dimensión del espacio (ℝⁿ)</label>
                <input
                  type="number"
                  min="2"
                  max="10"
                  value={dimension}
                  onChange={(e) => changeDimension(parseInt(e.target.value))}
                  className="w-32 px-3 py-2 bg-[#0d0d12] border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-purple-100 transition-all duration-200"
                />
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm text-purple-300/90 uppercase tracking-wider">Lista de Vectores</h3>
                <button
                  onClick={addVector}
                  className="px-3 py-1.5 text-sm bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 flex items-center gap-1 shadow-lg shadow-purple-500/20"
                >
                  <Plus className="w-4 h-4" />
                  Agregar
                </button>
              </div>

              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                {vectors.map((vector, i) => (
                  <div key={i} className="bg-[#0d0d12]/50 border border-purple-500/30 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-purple-300">v<sub>{i + 1}</sub></span>
                      <button
                        onClick={() => removeVector(i)}
                        className="p-1 text-purple-400/50 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      {vector.map((component, j) => (
                        <input
                          key={j}
                          type="number"
                          step="0.1"
                          value={component}
                          onChange={(e) => updateVector(i, j, e.target.value)}
                          className="w-16 px-2 py-1 bg-[#0a0a0f] border border-purple-500/30 rounded text-center text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-purple-100 font-mono transition-all duration-200"
                          placeholder={`x${j + 1}`}
                        />
                      ))}
                    </div>
                  </div>
                ))}

                {vectors.length === 0 && (
                  <div className="text-center py-8 text-purple-400/30">
                    No hay vectores. Agregue uno para comenzar.
                  </div>
                )}
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Herramientas de Análisis</h3>
              <div className="space-y-2">
                <button
                  onClick={checkIndependence}
                  disabled={vectors.length === 0 || loading}
                  className="w-full px-4 py-2.5 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 disabled:from-gray-600 disabled:to-gray-500 disabled:cursor-not-allowed disabled:opacity-50 text-sm shadow-lg shadow-purple-500/20"
                >
                  {loading ? 'Calculando...' : 'Verificar Independencia Lineal'}
                </button>
                <button
                  onClick={checkBasis}
                  disabled={vectors.length === 0 || loading}
                  className="w-full px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 transition-all duration-200 disabled:from-gray-600 disabled:to-gray-500 disabled:cursor-not-allowed disabled:opacity-50 text-sm shadow-lg shadow-cyan-500/20"
                >
                  {loading ? 'Calculando...' : 'Verificar si forman Base'}
                </button>
              </div>
            </div>
          </div>

          {/* Panel Derecho: Resultados */}
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
                    <div
                      key={i}
                      className={`whitespace-pre ${
                        result.isIndependent ? 'text-green-200/80' : 'text-red-200/80'
                      }`}
                    >
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
                    <div
                      key={i}
                      className={`whitespace-pre ${
                        result.isBasis ? 'text-green-200/80' : 'text-red-200/80'
                      }`}
                    >
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
                  <p className="text-sm mt-2">Agregue vectores y seleccione una herramienta</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
