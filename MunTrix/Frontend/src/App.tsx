import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { MatrixDefinition } from './components/MatrixDefinition';
import { MatrixOperations } from './components/MatrixOperations';
import { LinearSystems } from './components/LinearSystems';
import { VectorLab } from './components/VectorLab';
import { Determinants } from './components/Determinants';
import { NumericalConcepts } from './components/NumericalConcepts';

export type Matrix = number[][];

export interface MatrixVariable {
  name: 'A' | 'B' | 'C' | 'D' | 'E';
  matrix: Matrix | null;
  rows: number;
  cols: number;
}

export type ModuleType = 'definition' | 'operations' | 'systems' | 'vectors' | 'determinants' | 'numerical';

const initialVariables: MatrixVariable[] = [
  { name: 'A', matrix: null, rows: 0, cols: 0 },
  { name: 'B', matrix: null, rows: 0, cols: 0 },
  { name: 'C', matrix: null, rows: 0, cols: 0 },
  { name: 'D', matrix: null, rows: 0, cols: 0 },
  { name: 'E', matrix: null, rows: 0, cols: 0 },
];

export default function App() {
  const [variables, setVariables] = useState<MatrixVariable[]>(initialVariables);
  const [activeModule, setActiveModule] = useState<ModuleType>('operations');
  const [editingVariable, setEditingVariable] = useState<'A' | 'B' | 'C' | 'D' | 'E' | null>(null);
  const [useFractions, setUseFractions] = useState<boolean>(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  const updateVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E', matrix: Matrix, rows: number, cols: number) => {
    setVariables(prev => prev.map(v => 
      v.name === name ? { ...v, matrix, rows, cols } : v
    ));
  };

  const clearVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E') => {
    setVariables(prev => prev.map(v => 
      v.name === name ? { ...v, matrix: null, rows: 0, cols: 0 } : v
    ));
  };

  const getVariable = (name: 'A' | 'B' | 'C' | 'D' | 'E') => {
    return variables.find(v => v.name === name) || variables[0];
  };

  return (
    <div className="flex h-screen bg-[#0a0a0f]">
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
      <main className="flex-1 overflow-auto bg-[#0a0a0f]">
        {activeModule === 'definition' && (
          <MatrixDefinition
            variable={editingVariable || 'A'}
            currentMatrix={editingVariable ? getVariable(editingVariable) : getVariable('A')}
            onSave={updateVariable}
            onClose={() => {
              setEditingVariable(null);
              setActiveModule('operations');
            }}
          />
        )}

        {activeModule === 'operations' && (
          <MatrixOperations
            variables={variables}
            onEditVariable={(name) => {
              setEditingVariable(name);
              setActiveModule('definition');
            }}
            useFractions={useFractions}
          />
        )}

        {activeModule === 'systems' && (
          <LinearSystems
            variables={variables}
            onEditVariable={(name) => {
              setEditingVariable(name);
              setActiveModule('definition');
            }}
            useFractions={useFractions}
          />
        )}

        {activeModule === 'vectors' && (
          <VectorLab useFractions={useFractions} />
        )}

        {activeModule === 'determinants' && (
          <Determinants
            variables={variables}
            useFractions={useFractions}
          />
        )}

        {activeModule === 'numerical' && (
          <NumericalConcepts useFractions={useFractions} />
        )}
      </main>
    </div>
  );
}