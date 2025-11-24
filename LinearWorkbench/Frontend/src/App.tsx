import { useState } from 'react';
import { Calculator, Settings, Menu, X, Info, Grid3x3, ListChecks, Sigma, Box, Hash, Divide, Binary } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { MatrixDefinition } from './components/MatrixDefinition';
import { MatrixOperations } from './components/MatrixOperations';
import { LinearSystems } from './components/LinearSystems';
import { VectorLab } from './components/VectorLab';
import { Determinants } from './components/Determinants';
import { NumericalConcepts } from './components/NumericalConcepts';
import AboutSection from './components/AboutSection';

export type Matrix = number[][];
export type Vector = number[];

export interface MatrixVariable {
  name: 'A' | 'B' | 'C' | 'D' | 'E';
  matrix: Matrix | null;
  rows: number;
  cols: number;
  // Nuevo: soporte para vectores
  vector: Vector | null;
  vectorSize: number;
  isVector: boolean; // true si es un vector, false si es matriz
}

export type ModuleType = 'definition' | 'operations' | 'systems' | 'vectors' | 'determinants' | 'numerical' | 'about';

const initialVariables: MatrixVariable[] = [
  { name: 'A', matrix: null, rows: 0, cols: 0, vector: null, vectorSize: 0, isVector: false },
  { name: 'B', matrix: null, rows: 0, cols: 0, vector: null, vectorSize: 0, isVector: false },
  { name: 'C', matrix: null, rows: 0, cols: 0, vector: null, vectorSize: 0, isVector: false },
  { name: 'D', matrix: null, rows: 0, cols: 0, vector: null, vectorSize: 0, isVector: false },
  { name: 'E', matrix: null, rows: 0, cols: 0, vector: null, vectorSize: 0, isVector: false },
];

export default function App() {
  const [variables, setVariables] = useState<MatrixVariable[]>(initialVariables);
  const [activeModule, setActiveModule] = useState<ModuleType>('operations');
  const [editingVariable, setEditingVariable] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [useFractions, setUseFractions] = useState<boolean>(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  const updateVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E', matrix: Matrix, rows: number, cols: number) => {
    setVariables(prev => prev.map(v => 
      v.name === name ? { ...v, matrix, rows, cols, vector: null, vectorSize: 0, isVector: false } : v
    ));
  };

  const updateVector = (name: 'A' | 'B' | 'C' | 'D' | 'E', vector: Vector, size: number) => {
    setVariables(prev => prev.map(v => 
      v.name === name ? { ...v, vector, vectorSize: size, matrix: null, rows: 0, cols: 0, isVector: true } : v
    ));
  };

  const clearVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E') => {
    setVariables(prev => prev.map(v => 
      v.name === name ? { ...v, matrix: null, rows: 0, cols: 0, vector: null, vectorSize: 0, isVector: false } : v
    ));
  };

  const getVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E') => {
    return variables.find(v => v.name === name) || variables[0];
  };

  return (
    <div className="flex h-screen bg-[#0a0a0f] overflow-hidden">
      {/* Sidebar de Memoria de Variables */}
      <Sidebar
        variables={variables}
        onEditVariable={(name) => {
          setEditingVariable(name);
          setActiveModule('definition');
        }}
        onClearVariable={clearVariable}
        activeModule={activeModule}
        onModuleChange={setActiveModule}
        useFractions={useFractions}
        onToggleFractions={() => setUseFractions(!useFractions)}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Área Principal de Contenido */}
      <main className="flex-1 overflow-auto bg-[#0a0a0f] relative min-w-0">
        {/* Botón Acerca de - Esquina superior derecha */}
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveModule('about')}
          className={`absolute top-4 right-4 md:top-6 md:right-6 z-40 px-3 py-2 md:px-4 md:py-2 rounded-lg flex items-center gap-2 transition-all duration-200 shadow-lg ${
            activeModule === 'about'
              ? 'bg-gradient-to-r from-purple-600 to-cyan-600 text-white shadow-purple-500/50'
              : 'bg-gradient-to-r from-purple-900/80 to-cyan-900/80 text-purple-200 hover:from-purple-800/90 hover:to-cyan-800/90 backdrop-blur-sm border border-purple-500/30'
          }`}
        >
          <Info className="w-4 h-4 md:w-5 md:h-5" />
          <span className="text-xs md:text-sm">Acerca de</span>
        </motion.button>

        <AnimatePresence mode="wait">
          {activeModule === 'definition' && (
            <motion.div
              key="definition"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MatrixDefinition
                variable={editingVariable || 'A'}
                currentMatrix={editingVariable ? getVariable(editingVariable) : getVariable('A')}
                onSave={updateVariable}
                onSaveVector={updateVector}
                onClose={() => {
                  setEditingVariable(null);
                  setActiveModule('operations');
                }}
              />
            </motion.div>
          )}

          {activeModule === 'operations' && (
            <motion.div
              key="operations"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MatrixOperations
                variables={variables}
                onEditVariable={(name) => {
                  setEditingVariable(name);
                  setActiveModule('definition');
                }}
                useFractions={useFractions}
              />
            </motion.div>
          )}

          {activeModule === 'systems' && (
            <motion.div
              key="systems"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <LinearSystems
                variables={variables}
                onEditVariable={(name) => {
                  setEditingVariable(name);
                  setActiveModule('definition');
                }}
                useFractions={useFractions}
              />
            </motion.div>
          )}

          {activeModule === 'vectors' && (
            <motion.div
              key="vectors"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <VectorLab useFractions={useFractions} variables={variables} />
            </motion.div>
          )}

          {activeModule === 'determinants' && (
            <motion.div
              key="determinants"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Determinants
                variables={variables}
                useFractions={useFractions}
              />
            </motion.div>
          )}

          {activeModule === 'numerical' && (
            <motion.div
              key="numerical"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <NumericalConcepts useFractions={useFractions} />
            </motion.div>
          )}

          {activeModule === 'about' && (
            <motion.div
              key="about"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <AboutSection />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

interface SidebarProps {
  variables: MatrixVariable[];
  onEditVariable: (name: 'A' | 'B' | 'C' | 'D' | 'E') => void;
  onClearVariable: (name: 'A' | 'B' | 'C' | 'D' | 'E') => void;
  activeModule: ModuleType;
  onModuleChange: (module: ModuleType) => void;
  useFractions: boolean;
  onToggleFractions: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

function Sidebar({
  variables,
  onEditVariable,
  onClearVariable,
  activeModule,
  onModuleChange,
  useFractions,
  onToggleFractions,
  isCollapsed,
  onToggleCollapse
}: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ x: 0, width: isCollapsed ? 70 : 280 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className={`bg-gradient-to-b from-[#0d0d12] to-[#16161d] border-r border-purple-500/30 flex flex-col shadow-2xl shadow-purple-900/50 overflow-hidden ${
        isCollapsed ? 'w-[70px]' : 'w-[280px]'
      }`}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className={`border-b border-purple-500/20 ${isCollapsed ? 'p-3' : 'p-6'}`}
      >
        <div className="flex items-center justify-between mb-2">
          <AnimatePresence mode="wait">
            {!isCollapsed ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2"
              >
                <Calculator className="w-6 h-6 text-purple-400" />
                <h1 className="text-xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                  LinearWorkbench
                </h1>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center w-full"
              >
                <Calculator className="w-6 h-6 text-purple-400" />
              </motion.div>
            )}
          </AnimatePresence>
          {!isCollapsed && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={onToggleCollapse}
              className="p-2 hover:bg-purple-900/30 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 text-purple-400" />
            </motion.button>
          )}
        </div>
        <AnimatePresence>
          {!isCollapsed && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="text-xs text-purple-300/50"
            >
              Calculadora de Álgebra Lineal
            </motion.p>
          )}
        </AnimatePresence>
        {isCollapsed && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleCollapse}
            className="p-2 hover:bg-purple-900/30 rounded-lg transition-colors w-full flex items-center justify-center mt-2"
          >
            <Menu className="w-4 h-4 text-purple-400" />
          </motion.button>
        )}
      </motion.div>

      {/* Módulos */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className={`border-b border-purple-500/20 ${isCollapsed ? 'p-2' : 'p-4'}`}
      >
        <AnimatePresence>
          {!isCollapsed && (
            <motion.h3
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="text-xs mb-3 text-purple-300/70 uppercase tracking-wider"
            >
              Módulos
            </motion.h3>
          )}
        </AnimatePresence>
        <motion.div className="space-y-1">
          {[
            { id: 'operations' as ModuleType, label: 'Operaciones', short: 'Op', icon: Calculator },
            { id: 'systems' as ModuleType, label: 'Sistemas Lineales', short: 'SL', icon: ListChecks },
            { id: 'determinants' as ModuleType, label: 'Determinantes', short: 'Det', icon: Sigma },
            { id: 'vectors' as ModuleType, label: 'Lab. Vectores', short: 'Vec', icon: Box },
            { id: 'numerical' as ModuleType, label: 'Conceptos', short: 'Con', icon: Hash },
          ].map((module, index) => {
            const Icon = module.icon;
            return (
              <motion.button
                key={module.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + index * 0.05 }}
                whileHover={{ scale: 1.02, x: isCollapsed ? 0 : 4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onModuleChange(module.id)}
                title={isCollapsed ? module.label : undefined}
                className={`w-full rounded-lg flex items-center text-sm transition-all duration-200 ${
                  isCollapsed ? 'p-2 justify-center' : 'px-3 py-2 gap-2'
                } ${
                  activeModule === module.id
                    ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/30'
                    : 'text-purple-300/70 hover:bg-purple-900/30 hover:text-purple-200'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {!isCollapsed && <span>{module.label}</span>}
              </motion.button>
            );
          })}
        </motion.div>
      </motion.div>

      {/* Memoria de Variables */}
      <div className="flex-1 overflow-auto p-4">
        <AnimatePresence>
          {!isCollapsed && (
            <motion.h3
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="text-xs mb-3 text-purple-300/70 uppercase tracking-wider"
            >
              Memoria de Variables
            </motion.h3>
          )}
        </AnimatePresence>
        <motion.div className="space-y-2">
          {variables.map((variable, index) => (
            <motion.div
              key={variable.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              whileHover={{ scale: 1.02 }}
              className={`bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border rounded-lg p-3 ${
                variable.matrix || variable.vector
                  ? 'border-purple-500/40 shadow-lg shadow-purple-900/20'
                  : 'border-purple-500/10'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <motion.span
                  whileHover={{ scale: 1.1 }}
                  className={`text-sm font-mono ${
                    variable.matrix || variable.vector ? 'text-purple-300' : 'text-purple-500/30'
                  }`}
                >
                  {variable.name}
                </motion.span>
                {!isCollapsed && (variable.matrix || variable.vector) && (
                  <motion.button
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => onClearVariable(variable.name)}
                    className="text-xs text-red-400/70 hover:text-red-400 transition-colors"
                  >
                    Limpiar
                  </motion.button>
                )}
              </div>

              <AnimatePresence>
                {!isCollapsed && (
                  <>
                    {variable.matrix ? (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-xs text-purple-400/60 mb-2"
                      >
                        Matriz {variable.rows}×{variable.cols}
                      </motion.div>
                    ) : variable.vector ? (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-xs text-cyan-400/60 mb-2"
                      >
                        Vector R{variable.vectorSize}
                      </motion.div>
                    ) : (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-xs text-purple-500/30 mb-2"
                      >
                        Sin definir
                      </motion.div>
                    )}

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => onEditVariable(variable.name)}
                      className="w-full px-2 py-1 text-xs rounded bg-purple-900/30 text-purple-300 hover:bg-purple-900/50 transition-colors"
                    >
                      {variable.matrix || variable.vector ? 'Editar' : 'Definir'}
                    </motion.button>
                  </>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Configuración */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="p-4 border-t border-purple-500/20"
          >
            <div className="flex items-center gap-2 mb-3">
              <Settings className="w-4 h-4 text-purple-400" />
              <span className="text-xs text-purple-300/70 uppercase tracking-wider">
                Configuración
              </span>
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onToggleFractions}
              className={`w-full p-3 rounded-lg flex items-center justify-center gap-2 transition-all duration-500 ${
                useFractions
                  ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/30'
                  : 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white shadow-lg shadow-cyan-500/30'
              }`}
            >
              <AnimatePresence mode="wait">
                {useFractions ? (
                  <motion.div
                    key="fraction"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2, ease: "easeInOut" }}
                    className="flex items-center gap-2"
                  >
                    <Divide className="w-4 h-4" />
                    <span className="text-sm">Fracción</span>
                  </motion.div>
                ) : (
                  <motion.div
                    key="decimal"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2, ease: "easeInOut" }}
                    className="flex items-center gap-2"
                  >
                    <Binary className="w-4 h-4" />
                    <span className="text-sm">Decimal</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.aside>
  );
}