import { useState, useEffect } from 'react';
import { Matrix, MatrixVariable } from '../App';
import { Save, X, Dices, Grid3x3, Zap } from 'lucide-react';

interface MatrixDefinitionProps {
  variable: 'A' | 'B' | 'C' | 'D' | 'E';
  currentMatrix: MatrixVariable;
  onSave: (name: 'A' | 'B' | 'C' | 'D' | 'E', matrix: Matrix, rows: number, cols: number) => void;
  onClose: () => void;
}

export function MatrixDefinition({ variable, currentMatrix, onSave, onClose }: MatrixDefinitionProps) {
  const [rows, setRows] = useState(currentMatrix.rows || 3);
  const [cols, setCols] = useState(currentMatrix.cols || 3);
  const [matrix, setMatrix] = useState<Matrix>(
    currentMatrix.matrix || Array(3).fill(null).map(() => Array(3).fill(0))
  );

  useEffect(() => {
    if (currentMatrix.matrix) {
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
          // Permitir string vacío o valores numéricos (incluyendo negativos)
          if (value === '' || value === '-') {
            return 0;
          }
          const parsed = parseFloat(value);
          return isNaN(parsed) ? 0 : parsed;
        }
        return c;
      })
    );
    setMatrix(newMatrix);
  };

  const handleSave = () => {
    onSave(variable, matrix, rows, cols);
    onClose();
  };

  const fillRandom = () => {
    const newMatrix = matrix.map(row => 
      row.map(() => Math.floor(Math.random() * 20) - 10)
    );
    setMatrix(newMatrix);
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

  return (
    <div className="h-full bg-[#0a0a0f]">
      <div className="max-w-6xl mx-auto p-8">
        {/* Header con gradiente */}
        <div className="flex items-center justify-between mb-8 pb-6 border-b border-purple-500/20">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Grid3x3 className="w-8 h-8 text-purple-400" />
              <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                Definir Matriz {variable}
              </h2>
            </div>
            <p className="text-purple-300/70">Configure las dimensiones e ingrese los valores de la matriz</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-purple-400 hover:text-purple-300 hover:bg-purple-900/30 rounded-lg transition-all duration-200 border border-purple-500/20"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

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
              <button
                onClick={fillRandom}
                className="px-4 py-2 text-sm bg-gradient-to-r from-cyan-600/80 to-purple-600/80 text-white rounded-lg hover:from-cyan-500/80 hover:to-purple-500/80 transition-all duration-200 border border-cyan-500/30 flex items-center gap-2 shadow-lg shadow-cyan-500/20"
              >
                <Dices className="w-3.5 h-3.5" />
                Aleatorio
              </button>
            </div>
          </div>
        </div>

        {/* Grid de Entrada */}
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