import { useState, useEffect } from 'react';
import { Matrix, MatrixVariable, Vector } from '../App';
import { Save, X, Dices, Grid3x3, Zap, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface MatrixDefinitionProps {
  variable: 'A' | 'B' | 'C' | 'D' | 'E';
  currentMatrix: MatrixVariable;
  onSave: (name: 'A' | 'B' | 'C' | 'D' | 'E', matrix: Matrix, rows: number, cols: number) => void;
  onSaveVector: (name: 'A' | 'B' | 'C' | 'D' | 'E', vector: Vector, size: number) => void;
  onClose: () => void;
}

export function MatrixDefinition({ variable, currentMatrix, onSave, onSaveVector, onClose }: MatrixDefinitionProps) {
  const [mode, setMode] = useState<'matrix' | 'vector'>(currentMatrix.isVector ? 'vector' : 'matrix');
  const [rows, setRows] = useState(currentMatrix.rows || 3);
  const [cols, setCols] = useState(currentMatrix.cols || 3);
  const [matrix, setMatrix] = useState<(number | string)[][]>(
    currentMatrix.matrix || Array(3).fill(null).map(() => Array(3).fill(0))
  );
  const [isRolling, setIsRolling] = useState(false);
  
  // Estado para vectores
  const [vectorSize, setVectorSize] = useState(currentMatrix.vectorSize || 3);
  const [vector, setVector] = useState<(number | string)[]>(
    currentMatrix.vector || Array(3).fill(0)
  );

  useEffect(() => {
    if (currentMatrix.isVector && currentMatrix.vector) {
      setMode('vector');
      setVectorSize(currentMatrix.vectorSize);
      setVector(currentMatrix.vector);
    } else if (currentMatrix.matrix) {
      setMode('matrix');
      setRows(currentMatrix.rows);
      setCols(currentMatrix.cols);
      setMatrix(currentMatrix.matrix);
    }
  }, [currentMatrix]);

  const handleDimensionChange = (newRows: number, newCols: number) => {
    const validRows = Math.max(1, Math.min(10, newRows));
    const validCols = Math.max(1, Math.min(10, newCols));
    
    setRows(validRows);
    setCols(validCols);

    // Crear nueva matriz con dimensiones actualizadas
    const newMatrix: Matrix = Array(validRows).fill(null).map((_, i) =>
      Array(validCols).fill(null).map((_, j) => 
        matrix[i]?.[j] ?? 0
      )
    );
    setMatrix(newMatrix);
  };

  const handleCellChange = (row: number, col: number, value: string) => {
    const newMatrix = matrix.map((r, i) =>
      r.map((c, j) => {
        if (i === row && j === col) {
          // Permitir string vacío, '-', o '.' para facilitar la edición
          if (value === '' || value === '-' || value === '.') {
            return value;
          }
          const parsed = parseFloat(value);
          return isNaN(parsed) ? value : parsed;
        }
        return c;
      })
    );
    setMatrix(newMatrix);
  };

  const handleSave = () => {
    if (mode === 'vector') {
      // Convertir strings vacíos a 0 antes de guardar
      const cleanVector = vector.map(v => {
        if (typeof v === 'string') {
          const parsed = parseFloat(v);
          return isNaN(parsed) || v === '' ? 0 : parsed;
        }
        return v;
      });
      onSaveVector(variable, cleanVector, vectorSize);
    } else {
      // Convertir strings vacíos a 0 antes de guardar
      const cleanMatrix = matrix.map(row => 
        row.map(cell => {
          if (typeof cell === 'string') {
            const parsed = parseFloat(cell);
            return isNaN(parsed) || cell === '' ? 0 : parsed;
          }
          return cell;
        })
      );
      onSave(variable, cleanMatrix, rows, cols);
    }
    onClose();
  };

  const fillRandom = () => {
    setIsRolling(true);
    const newMatrix = matrix.map(row => 
      row.map(() => Math.floor(Math.random() * 20) - 10)
    );
    setMatrix(newMatrix);
    setTimeout(() => setIsRolling(false), 500);
  };

  const fillIdentity = () => {
    if (rows !== cols) {
      alert('La matriz identidad debe ser cuadrada (n×n)');
      return;
    }
    const newMatrix = matrix.map((row, i) =>
      row.map((_, j) => (i === j ? 1 : 0))
    );
    setMatrix(newMatrix);
  };

  const fillZeros = () => {
    const newMatrix = matrix.map(row => row.map(() => 0));
    setMatrix(newMatrix);
  };

  const handleVectorSizeChange = (newSize: number) => {
    const validSize = Math.max(1, Math.min(10, newSize));
    setVectorSize(validSize);

    // Crear nuevo vector con tamaño actualizado
    const newVector: Vector = Array(validSize).fill(null).map((_, i) => 
      vector[i] ?? 0
    );
    setVector(newVector);
  };

  const handleVectorCellChange = (index: number, value: string) => {
    const newVector = vector.map((c, i) => {
      if (i === index) {
        // Permitir string vacío, '-', o '.' para facilitar la edición
        if (value === '' || value === '-' || value === '.') {
          return value;
        }
        const parsed = parseFloat(value);
        return isNaN(parsed) ? value : parsed;
      }
      return c;
    });
    setVector(newVector);
  };

  const fillRandomVector = () => {
    setIsRolling(true);
    const newVector = vector.map(() => Math.floor(Math.random() * 20) - 10);
    setVector(newVector);
    setTimeout(() => setIsRolling(false), 500);
  };

  const fillZerosVector = () => {
    const newVector = vector.map(() => 0);
    setVector(newVector);
  };

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-6xl mx-auto p-8">
        {/* Header con gradiente */}
        <div className="flex items-center justify-between mb-8 pb-6 border-b border-purple-500/20">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Grid3x3 className="w-8 h-8 text-purple-400" />
              <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                Definir Variable {variable}
              </h2>
            </div>
            <p className="text-purple-300/70">Configure una matriz o un vector para la memoria global</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-purple-400 hover:text-purple-300 hover:bg-purple-900/30 rounded-lg transition-all duration-200 border border-purple-500/20"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Selector de Modo: Matriz / Vector */}
        <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-purple-500/10">
          <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Tipo de Variable</h3>
          <div className="flex gap-3">
            <button
              onClick={() => setMode('matrix')}
              className={`flex-1 px-6 py-4 rounded-lg border text-left transition-all duration-200 ${
                mode === 'matrix'
                  ? 'bg-gradient-to-br from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/30'
                  : 'bg-purple-900/20 text-purple-300 border-purple-500/30 hover:bg-purple-900/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <Grid3x3 className="w-5 h-5" />
                <div>
                  <div className="mb-1">Matriz</div>
                  <div className="text-xs opacity-70">Arreglo bidimensional (m×n)</div>
                </div>
              </div>
            </button>
            
            <button
              onClick={() => setMode('vector')}
              className={`flex-1 px-6 py-4 rounded-lg border text-left transition-all duration-200 ${
                mode === 'vector'
                  ? 'bg-gradient-to-br from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                  : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <ArrowRight className="w-5 h-5" />
                <div>
                  <div className="mb-1">Vector</div>
                  <div className="text-xs opacity-70">Arreglo unidimensional (n)</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Configuración para MATRIZ */}
        {mode === 'matrix' && (
          <>
            {/* Configuración de Dimensiones */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Dimensiones de la Matriz</h3>
              <div className="flex gap-6 items-center">
                <div>
                  <label className="block text-sm mb-2 text-purple-300/70">Filas (m)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={rows}
                    onChange={(e) => handleDimensionChange(parseInt(e.target.value), cols)}
                    className="w-24 px-3 py-2 bg-[#0d0d12] border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-purple-100 transition-all duration-200"
                  />
                </div>
                <div className="text-2xl text-purple-400/50">×</div>
                <div>
                  <label className="block text-sm mb-2 text-purple-300/70">Columnas (n)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={cols}
                    onChange={(e) => handleDimensionChange(rows, parseInt(e.target.value))}
                    className="w-24 px-3 py-2 bg-[#0d0d12] border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-purple-100 transition-all duration-200"
                  />
                </div>
                <div className="flex-1"></div>
                <div className="flex gap-2">
                  <button
                    onClick={fillZeros}
                    className="px-4 py-2 text-sm bg-purple-900/30 text-purple-300 rounded-lg hover:bg-purple-900/50 transition-all duration-200 border border-purple-500/20 flex items-center gap-2"
                  >
                    <Zap className="w-3.5 h-3.5" />
                    Llenar con 0
                  </button>
                  <button
                    onClick={fillIdentity}
                    className="px-4 py-2 text-sm bg-purple-900/30 text-purple-300 rounded-lg hover:bg-purple-900/50 transition-all duration-200 border border-purple-500/20 flex items-center gap-2"
                  >
                    <Grid3x3 className="w-3.5 h-3.5" />
                    Identidad
                  </button>
                  <motion.button
                    onClick={fillRandom}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-4 py-2 text-sm bg-gradient-to-r from-cyan-600/80 to-purple-600/80 text-white rounded-lg hover:from-cyan-500/80 hover:to-purple-500/80 transition-all duration-200 border border-cyan-500/30 flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                  >
                    <motion.div
                      animate={isRolling ? {
                        rotate: [0, -10, 10, -10, 10, 0],
                        y: [0, -4, 0, -2, 0]
                      } : {}}
                      transition={{ duration: 0.5, ease: "easeInOut" }}
                    >
                      <Dices className="w-3.5 h-3.5" />
                    </motion.div>
                    Aleatorio
                  </motion.button>
                </div>
              </div>
            </div>

            {/* Grid de Entrada de Matriz */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-purple-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-purple-500/10">
              <h3 className="text-sm mb-4 text-purple-300/90 uppercase tracking-wider">Grid de Entrada</h3>
              <div className="overflow-x-auto">
                <div className="inline-block min-w-full">
                  <div className="flex flex-col gap-2">
                    {matrix.map((row, i) => (
                      <div key={i} className="flex gap-2">
                        {row.map((cell, j) => (
                          <input
                            key={`${i}-${j}`}
                            type="number"
                            step="0.1"
                            value={cell}
                            onChange={(e) => handleCellChange(i, j, e.target.value)}
                            className="w-20 px-3 py-2 bg-[#0d0d12] border border-purple-500/30 rounded-lg text-center focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-purple-100 font-mono transition-all duration-200 hover:border-purple-400/50"
                          />
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Configuración para VECTOR */}
        {mode === 'vector' && (
          <>
            {/* Configuración de Dimensión del Vector */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider">Dimensión del Vector</h3>
              <div className="flex gap-6 items-center">
                <div>
                  <label className="block text-sm mb-2 text-cyan-300/70">Tamaño (n)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={vectorSize}
                    onChange={(e) => handleVectorSizeChange(parseInt(e.target.value))}
                    className="w-24 px-3 py-2 bg-[#0d0d12] border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-cyan-100 transition-all duration-200"
                  />
                </div>
                <div className="flex-1"></div>
                <div className="flex gap-2">
                  <button
                    onClick={fillZerosVector}
                    className="px-4 py-2 text-sm bg-cyan-900/30 text-cyan-300 rounded-lg hover:bg-cyan-900/50 transition-all duration-200 border border-cyan-500/20 flex items-center gap-2"
                  >
                    <Zap className="w-3.5 h-3.5" />
                    Llenar con 0
                  </button>
                  <motion.button
                    onClick={fillRandomVector}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-4 py-2 text-sm bg-gradient-to-r from-cyan-600/80 to-blue-600/80 text-white rounded-lg hover:from-cyan-500/80 hover:to-blue-500/80 transition-all duration-200 border border-cyan-500/30 flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                  >
                    <motion.div
                      animate={isRolling ? {
                        rotate: [0, -10, 10, -10, 10, 0],
                        y: [0, -4, 0, -2, 0]
                      } : {}}
                      transition={{ duration: 0.5, ease: "easeInOut" }}
                    >
                      <Dices className="w-3.5 h-3.5" />
                    </motion.div>
                    Aleatorio
                  </motion.button>
                </div>
              </div>
            </div>

            {/* Grid de Entrada del Vector */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 mb-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider">Componentes del Vector</h3>
              <div className="flex flex-col gap-2">
                {vector.map((value, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-cyan-300/70 text-sm w-12">v[{i}]</span>
                    <input
                      type="number"
                      step="0.1"
                      value={value}
                      onChange={(e) => handleVectorCellChange(i, e.target.value)}
                      className="w-32 px-3 py-2 bg-[#0d0d12] border border-cyan-500/30 rounded-lg text-center focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-cyan-100 font-mono transition-all duration-200 hover:border-cyan-400/50"
                    />
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Botones de Acción */}
        <div className="flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-6 py-3 text-purple-300 bg-purple-900/30 rounded-lg hover:bg-purple-900/50 transition-all duration-200 border border-purple-500/20"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 flex items-center gap-2 shadow-lg shadow-purple-500/30"
          >
            <Save className="w-4 h-4" />
            Guardar en Memoria {variable}
          </button>
        </div>
      </div>
    </div>
  );
}