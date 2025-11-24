import { MatrixVariable, ModuleType } from '../App';
import { Calculator, Grid3x3, ListChecks, Box, Sigma, Trash2, Edit2, Sparkles, Binary, Hash, ChevronLeft, ChevronRight } from 'lucide-react';

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

export function Sidebar({ variables, onEditVariable, onClearVariable, activeModule, onModuleChange, useFractions, onToggleFractions, isCollapsed, onToggleCollapse }: SidebarProps) {
  const modules = [
    { id: 'operations' as ModuleType, label: 'Operaciones', icon: Calculator },
    { id: 'systems' as ModuleType, label: 'Sistemas Lineales', icon: ListChecks },
    { id: 'vectors' as ModuleType, label: 'Lab. Vectores', icon: Box },
    { id: 'determinants' as ModuleType, label: 'Determinantes', icon: Sigma },
    { id: 'numerical' as ModuleType, label: 'Conceptos Numéricos', icon: Hash },
  ];

  return (
    <aside className={`bg-[#0d0d12] border-r border-purple-500/20 flex flex-col shadow-2xl transition-all duration-300 ease-in-out relative ${isCollapsed ? 'w-16' : 'w-80'}`}>
      {/* Botón de colapsar/expandir */}
      <button
        onClick={onToggleCollapse}
        className="absolute -right-3 top-6 z-10 w-6 h-6 bg-gradient-to-r from-purple-600 to-purple-500 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/30 hover:from-purple-500 hover:to-purple-400 transition-all duration-200 border-2 border-[#0a0a0f]"
        title={isCollapsed ? "Expandir sidebar" : "Colapsar sidebar"}
      >
        {isCollapsed ? (
          <ChevronRight className="w-3.5 h-3.5 text-white" />
        ) : (
          <ChevronLeft className="w-3.5 h-3.5 text-white" />
        )}
      </button>

      {!isCollapsed ? (
        <>
          {/* Header con efecto de brillo */}
          <div className="p-6 border-b border-purple-500/20 bg-gradient-to-br from-purple-900/20 to-transparent">
            <div className="flex items-center gap-3 mb-2">
              <Sparkles className="w-6 h-6 text-purple-400" />
              <h1 className="text-3xl text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-purple-300 to-cyan-400">
                MunTrix
              </h1>
            </div>
            <p className="text-sm text-purple-300/70">Calculadora de Álgebra Lineal</p>
            
            {/* Toggle de Fracciones */}
            <div className="mt-4 flex items-center justify-between p-2 bg-purple-900/20 rounded-lg border border-purple-500/20">
              <div className="flex items-center gap-2">
                <Binary className="w-4 h-4 text-purple-400" />
                <span className="text-xs text-purple-300">Fracciones</span>
              </div>
              <button
                onClick={onToggleFractions}
                className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                  useFractions ? 'bg-purple-600' : 'bg-purple-900/50'
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform duration-300 ${
                    useFractions ? 'transform translate-x-6' : ''
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Navegación de Módulos - Siempre visible arriba */}
          <div className="p-4 border-b border-purple-500/20 bg-[#16161d]/50">
            <h2 className="text-xs mb-3 text-purple-300/70 uppercase tracking-wider flex items-center gap-2">
              <Grid3x3 className="w-3.5 h-3.5" />
              Módulos
            </h2>
            <nav className="space-y-1.5">
              {modules.map((module) => {
                const Icon = module.icon;
                return (
                  <button
                    key={module.id}
                    onClick={() => onModuleChange(module.id)}
                    className={`w-full px-3 py-2 rounded-lg text-left flex items-center gap-3 transition-all duration-200 group ${
                      activeModule === module.id
                        ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/30'
                        : 'text-purple-200/70 hover:bg-purple-900/30 hover:text-purple-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${activeModule === module.id ? 'text-white' : 'text-purple-400/70 group-hover:text-purple-300'}`} />
                    <span className="text-sm">{module.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Memoria de Variables - Con scroll */}
          <div className="flex-1 overflow-y-auto p-4">
            <h2 className="text-xs mb-4 text-purple-300/70 uppercase tracking-wider">
              Memoria de Variables
            </h2>
            <div className="space-y-3">
              {variables.map((variable) => (
                <div
                  key={variable.name}
                  className="border border-purple-500/30 rounded-xl p-3 bg-gradient-to-br from-[#1e1e2e]/80 to-[#16161d]/80 hover:border-purple-500/50 transition-all duration-200 backdrop-blur-sm shadow-lg"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-lg text-purple-100">
                        Matriz {variable.name}
                      </span>
                      {variable.matrix && (
                        <span className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30">
                          {variable.rows}×{variable.cols}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Vista previa con efecto de brillo */}
                  <div className="mb-3 min-h-[70px] flex items-center justify-center bg-[#0d0d12]/50 rounded-lg border border-purple-500/20">
                    {variable.matrix ? (
                      <div className="text-xs p-2 max-w-full overflow-hidden">
                        {variable.rows <= 3 && variable.cols <= 3 ? (
                          // Mostrar matriz completa si es pequeña
                          <div className="inline-flex flex-col gap-1.5">
                            {variable.matrix.map((row, i) => (
                              <div key={i} className="flex gap-3">
                                {row.map((val, j) => (
                                  <span key={j} className="w-11 text-center text-purple-200 font-mono">
                                    {val.toFixed(1)}
                                  </span>
                                ))}
                              </div>
                            ))}
                          </div>
                        ) : (
                          // Vista reducida para matrices grandes
                          <div className="text-center text-purple-300/70">
                            <div className="mb-1 font-mono">Matriz {variable.rows}×{variable.cols}</div>
                            <div className="text-xs text-purple-400/50">
                              [{variable.matrix[0][0].toFixed(1)}, ...]
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-purple-400/30">Vacío</span>
                    )}
                  </div>

                  {/* Botones de acción con gradientes */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => onEditVariable(variable.name)}
                      className="flex-1 px-3 py-2 text-sm bg-gradient-to-r from-purple-600 to-purple-500 text-white rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all duration-200 flex items-center justify-center gap-1.5 shadow-lg shadow-purple-500/20"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                      {variable.matrix ? 'Editar' : 'Definir'}
                    </button>
                    {variable.matrix && (
                      <button
                        onClick={() => onClearVariable(variable.name)}
                        className="px-3 py-2 text-sm bg-purple-900/30 text-purple-300 rounded-lg hover:bg-purple-800/40 transition-all duration-200 border border-purple-500/20"
                        title="Limpiar"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer decorativo */}
          <div className="p-4 border-t border-purple-500/20 bg-gradient-to-t from-purple-900/10 to-transparent">
            <div className="text-xs text-center text-purple-400/50">
              Powered by Jose Munguia
            </div>
          </div>
        </>
      ) : (
        /* Vista colapsada - Solo iconos */
        <div className="flex-1 flex flex-col items-center py-6 gap-6">
          {/* Logo pequeño */}
          <div className="mb-4">
            <Sparkles className="w-8 h-8 text-purple-400" />
          </div>

          {/* Navegación de módulos colapsada */}
          <nav className="flex flex-col gap-3">
            {modules.map((module) => {
              const Icon = module.icon;
              return (
                <button
                  key={module.id}
                  onClick={() => onModuleChange(module.id)}
                  className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-200 ${
                    activeModule === module.id
                      ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/30'
                      : 'text-purple-400/70 hover:bg-purple-900/30 hover:text-purple-300'
                  }`}
                  title={module.label}
                >
                  <Icon className="w-5 h-5" />
                </button>
              );
            })}
          </nav>
        </div>
      )}
    </aside>
  );
}