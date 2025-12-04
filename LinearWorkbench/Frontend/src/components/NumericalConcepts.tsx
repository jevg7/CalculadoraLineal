import { useState } from 'react';
import { 
  Hash, 
  Binary, 
  AlertCircle, 
  Calculator, 
  Info, 
  TrendingDown, 
  BarChart3,
  Divide,     // Nuevo
  Zap,        // Nuevo
  Activity    // Nuevo
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface NumericalConceptsProps {
  useFractions: boolean;
}

type Section = 'positional' | 'errors' | 'floating' | 'error-sources' | 'roots';
type RootMethod = 'bisection' | 'false-position' | 'newton' | 'secant';

export function NumericalConcepts({ useFractions }: NumericalConceptsProps) {
  const [activeSection, setActiveSection] = useState<Section>('positional');
  
  // --- Estados Generales ---
  const [base10Input, setBase10Input] = useState('84506');
  const [base2Input, setBase2Input] = useState('1111001');
  const [base10Result, setBase10Result] = useState<string[]>([]);
  const [base2Result, setBase2Result] = useState<string[]>([]);

  // --- Estados de Raíces (Unificados) ---
  const [rootMethod, setRootMethod] = useState<RootMethod>('bisection');
  const [funcStr, setFuncStr] = useState('x^3 - x - 2');
  // intervalA sirve como 'a' (bisección) o 'x0' (newton/secante)
  const [intervalA, setIntervalA] = useState('1'); 
  // intervalB sirve como 'b' (bisección) o 'x1' (secante)
  const [intervalB, setIntervalB] = useState('2'); 
  const [tolerance, setTolerance] = useState('0.0001');
  const [maxIter, setMaxIter] = useState('50');
  const [rootResults, setRootResults] = useState<string[]>([]);

  // --- Estados de Errores ---
  const [roundoffN, setRoundoffN] = useState('3');
  const [roundoffValue, setRoundoffValue] = useState('0.333333');
  const [truncationX, setTruncationX] = useState('0.5');
  const [truncationTerms, setTruncationTerms] = useState('5');
  const [propagationA, setPropagationA] = useState('10.0');
  const [propagationB, setPropagationB] = useState('0.1');
  const [errorResults, setErrorResults] = useState<string[]>([]);
  const [errorType, setErrorType] = useState<'roundoff' | 'truncation' | 'propagation'>('roundoff');

  // ==========================================
  // LÓGICA: BASES
  // ==========================================

  const decomposeBase10 = async () => {
    setBase10Result([]);
    const num = base10Input.trim();
    if (!/^\d+$/.test(num)) {
      setBase10Result(['Error: Ingrese solo dígitos numéricos']);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/numerical/decompose/base10`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: num }),
      });
      const data = await res.json();
      setBase10Result(data.steps ?? [data.error ?? 'Error desconocido']);
    } catch (err) {
      console.error(err);
      setBase10Result(['Error al conectarse al backend']);
    }
  };

  const decomposeBase2 = async () => {
    setBase2Result([]);
    const num = base2Input.trim();
    if (!/^[01]+$/.test(num)) {
      setBase2Result(['Error: Ingrese solo dígitos binarios (0/1)']);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/numerical/decompose/base2`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: num }),
      });
      const data = await res.json();
      setBase2Result(data.steps ?? [data.error ?? 'Error desconocido']);
    } catch (err) {
      console.error(err);
      setBase2Result(['Error al conectarse al backend']);
    }
  };

  // ==========================================
  // LÓGICA: ERRORES
  // ==========================================

  const errorExamples = {
    inherent: {
      title: 'Error Inherente',
      description: 'Errores presentes en los datos de entrada, causados por mediciones imprecisas o aproximaciones iniciales.',
      example: 'Si medimos π = 3.14, el error inherente es |π - 3.14| ≈ 0.0016',
      code: `// Error inherente en medición de π
const piReal = Math.PI;  // 3.141592653589793
const piMedido = 3.14;   // Medición con 2 decimales
const errorInherente = Math.abs(piReal - piMedido);
console.log('Error inherente:', errorInherente);  // ≈ 0.0016`
    },
    roundoff: {
      title: 'Error de Redondeo',
      description: 'Surge cuando un número con infinitos decimales se representa con precisión finita.',
      example: '1/3 = 0.333... → 0.333 (redondeado)',
      code: `// Error de redondeo
const exacto = 1/3;        // 0.3333333333333333
const redondeado = 0.333;  // Redondeado a 3 decimales
const errorRedondeo = Math.abs(exacto - redondeado);
console.log('Error de redondeo:', errorRedondeo);  // ≈ 0.0003`
    },
    truncation: {
      title: 'Error de Truncamiento',
      description: 'Ocurre al aproximar un proceso matemático infinito con uno finito (ej: series, derivadas).',
      example: 'e^x = 1 + x + x²/2! + ... → 1 + x (truncado en primer orden)',
      code: `// Error de truncamiento en serie de Taylor
// e^x ≈ 1 + x + x²/2! + x³/3! + ...
const x = 0.5;
const exacto = Math.exp(x);     // e^0.5 exacto
const aproximado = 1 + x;       // Solo 2 términos (truncado)
const errorTruncamiento = Math.abs(exacto - aproximado);
console.log('e^0.5 exacto:', exacto);          // 1.6487
console.log('e^0.5 aprox:', aproximado);        // 1.5
console.log('Error truncamiento:', errorTruncamiento);  // ≈ 0.1487`
    },
    overflow: {
      title: 'Overflow y Underflow',
      description: 'Overflow: resultado demasiado grande. Underflow: resultado demasiado pequeño para representarse.',
      example: 'Overflow: 10^400 → Infinity | Underflow: 10^-400 → 0',
      code: `// Overflow: número muy grande
const overflow = Math.pow(10, 400);
console.log('Overflow:', overflow);  // Infinity

// Underflow: número muy pequeño
const underflow = Math.pow(10, -400);
console.log('Underflow:', underflow);  // 0`
    },
    model: {
      title: 'Error del Modelo Matemático',
      description: 'Error introducido al simplificar un fenómeno real en un modelo matemático.',
      example: 'Modelar caída libre sin resistencia del aire cuando sí existe',
      code: `// Modelo simple: h = h₀ - (1/2)gt²
// Modelo real: incluye resistencia del aire`
    }
  };

  const floatingPointDemo = () => {
    const a = 0.1;
    const b = 0.2;
    const sum = a + b;
    const expected = 0.3;
    const areEqual = (sum === expected);
    
    return {
      a, b, sum, expected, areEqual,
      sumString: sum.toString(),
      explanation: `
La computadora no puede representar exactamente 0.1, 0.2 y 0.3 en binario.
En binario, 0.1 es una fracción periódica infinita.
Al sumar 0.1 + 0.2, el resultado es ${sum}, muy cercano pero diferente de 0.3.
      `.trim()
    };
  };

  const floatDemo = floatingPointDemo();

  const demonstrateRoundoff = async () => {
    const n = parseInt(roundoffN);
    const value = parseFloat(roundoffValue);
    if (isNaN(n) || n < 1 || n > 20) return setErrorResults(['Error: n debe estar entre 1 y 20']);
    if (isNaN(value)) return setErrorResults(['Error: Ingrese un valor numérico válido']);

    try {
      const res = await fetch(`${API_BASE}/numerical/errors/roundoff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value, n }),
      });
      const data = await res.json();
      setErrorType('roundoff');
      setErrorResults(data.steps ?? [data.error]);
    } catch (err) { setErrorResults(['Error de conexión']); }
  };

  const demonstrateTruncation = async () => {
    const x = parseFloat(truncationX);
    const maxTerms = parseInt(truncationTerms);
    if (isNaN(x) || isNaN(maxTerms)) return setErrorResults(['Error: Datos inválidos']);

    try {
      const res = await fetch(`${API_BASE}/numerical/errors/truncation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, max_terms: maxTerms }),
      });
      const data = await res.json();
      setErrorType('truncation');
      setErrorResults(data.steps ?? [data.error]);
    } catch (err) { setErrorResults(['Error de conexión']); }
  };

  const demonstratePropagation = async () => {
    const a = parseFloat(propagationA);
    const b = parseFloat(propagationB);
    if (isNaN(a) || isNaN(b)) return setErrorResults(['Error: Datos inválidos']);

    try {
      const res = await fetch(`${API_BASE}/numerical/errors/propagation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ a, b }),
      });
      const data = await res.json();
      setErrorType('propagation');
      setErrorResults(data.steps ?? [data.error]);
    } catch (err) { setErrorResults(['Error de conexión']); }
  };

  // ==========================================
  // LÓGICA: RAÍCES (Métodos)
  // ==========================================

  const solveBisection = async () => {
    const a = parseFloat(intervalA);
    const b = parseFloat(intervalB);
    const tol = parseFloat(tolerance);
    const maxIterations = parseInt(maxIter);
    const func = funcStr.trim();

    if (!func) return setRootResults(['Error: Ingrese una función f(x)']);
    if (isNaN(a) || isNaN(b) || isNaN(tol) || isNaN(maxIterations)) return setRootResults(['Error: Campos numéricos inválidos']);

    try {
      setRootResults(['Calculando...']);
      const res = await fetch(`${API_BASE}/numerical/bisection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expr: func, a, b, tol, max_iter: maxIterations }),
      });
      const data = await res.json();
      
      const steps: string[] = data.steps ?? [];
      if (data.error) steps.push(`\nError: ${data.error}`);
      else if (typeof data.value === 'number') steps.push(`\nRaíz aproximada: x ≈ ${data.value}`);
      
      setRootResults(steps);
    } catch (err) { setRootResults(['Error de conexión']); }
  };

  const solveFalsePosition = async () => {
    const a = parseFloat(intervalA);
    const b = parseFloat(intervalB);
    const tol = parseFloat(tolerance);
    const maxIterations = parseInt(maxIter, 10);
    const func = funcStr.trim();

    if (!func) return setRootResults(['Error: Ingrese una función f(x)']);
    if (isNaN(a) || isNaN(b)) return setRootResults(['Error: Campos numéricos inválidos']);

    try {
      setRootResults(['Calculando...']);
      const res = await fetch(`${API_BASE}/numerical/false-position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expr: func, a, b, tol, max_iter: maxIterations }),
      });
      const data = await res.json();
      
      const steps: string[] = data.steps ?? [];
      if (data.error) steps.push(`\nError: ${data.error}`);
      else if (typeof data.value === 'number') steps.push(`\n(API) Raíz aproximada: x ≈ ${data.value}`);
      
      setRootResults(steps);
    } catch (e) { setRootResults(['Error de conexión']); }
  };

  // Renombrado a solveNewton y adaptado para usar intervalA como x0
  const solveNewton = async () => {
    const x0 = parseFloat(intervalA); // Usamos intervalA como x0
    const tol = parseFloat(tolerance);
    const maxIterations = parseInt(maxIter, 10);
    const func = funcStr.trim();

    if (!func) return setRootResults(['Error: Ingrese una función f(x)']);
    if (isNaN(x0)) return setRootResults(['Error: Ingrese un valor inicial válido (x0)']);

    try {
      setRootResults(['Calculando...']);
      const res = await fetch(`${API_BASE}/numerical/newton-raphson`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expr: func, x0, tol, max_iter: maxIterations }),
      });
      const data = await res.json();
      
      const steps: string[] = data.steps ?? [];
      if (data.error) steps.push(`\nError: ${data.error}`);
      else if (typeof data.value === 'number') steps.push(`\n(API) Raíz aproximada: x ≈ ${data.value}`);
      
      setRootResults(steps);
    } catch (e) { setRootResults(['Error de conexión']); }
  };

  // Adaptado para usar intervalA como x0 y intervalB como x1
  const solveSecant = async () => {
    const x0 = parseFloat(intervalA);
    const x1 = parseFloat(intervalB);
    const tol = parseFloat(tolerance);
    const maxIterations = parseInt(maxIter, 10);
    const func = funcStr.trim();

    if (!func) return setRootResults(['Error: Ingrese una función f(x)']);
    if (isNaN(x0) || isNaN(x1)) return setRootResults(['Error: Ingrese valores iniciales válidos']);

    try {
      setRootResults(['Calculando...']);
      const res = await fetch(`${API_BASE}/numerical/secant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expr: func, x0, x1, tol, max_iter: maxIterations }),
      });
      const data = await res.json();
      
      const steps: string[] = data.steps ?? [];
      if (data.error) steps.push(`\nError: ${data.error}`);
      else if (typeof data.value === 'number') steps.push(`\n(API) Raíz aproximada: x ≈ ${data.value}`);
      
      setRootResults(steps);
    } catch (e) { setRootResults(['Error de conexión']); }
  };

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-7xl mx-auto p-8">
        
        {/* Header */}
        <div className="mb-8 pb-6 border-b border-cyan-500/20">
          <div className="flex items-center gap-3 mb-2">
            <Hash className="w-8 h-8 text-cyan-400" />
            <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
              Métodos Numéricos
            </h2>
          </div>
          <p className="text-cyan-300/70">Representación de números, errores y métodos de resolución</p>
        </div>

        {/* Navegación de secciones */}
        <div className="mb-6 flex gap-3 flex-wrap">
          <button
            onClick={() => setActiveSection('positional')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'positional'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <Binary className="w-4 h-4" /> Notación Posicional
          </button>
          <button
            onClick={() => setActiveSection('errors')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'errors'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <AlertCircle className="w-4 h-4" /> Errores Numéricos
          </button>
          <button
            onClick={() => setActiveSection('floating')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'floating'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <Calculator className="w-4 h-4" /> Punto Flotante
          </button>
          <button
            onClick={() => setActiveSection('error-sources')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'error-sources'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <TrendingDown className="w-4 h-4" /> Fuentes de Error
          </button>
          <button
            onClick={() => setActiveSection('roots')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'roots'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <BarChart3 className="w-4 h-4" /> Raíces de Ecuaciones
          </button>
        </div>

        {/* ======================= SECCIÓN: NOTACIÓN POSICIONAL ======================= */}
        {activeSection === 'positional' && (
          <div className="grid grid-cols-2 gap-6">
            {/* Base 10 */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider flex items-center gap-2">
                <span className="text-xl">🔢</span> Descomposición en Base 10
              </h3>
              <div className="mb-4">
                <label className="block text-sm mb-2 text-cyan-300/70">Número en Base 10</label>
                <input
                  type="text"
                  value={base10Input}
                  onChange={(e) => setBase10Input(e.target.value)}
                  placeholder="Ej: 84506"
                  className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                />
              </div>
              <button
                onClick={decomposeBase10}
                className="w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/30"
              >
                <Calculator className="w-4 h-4" /> Descomponer
              </button>
              {base10Result.length > 0 && (
                <div className="mt-4 bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <div className="font-mono text-sm text-cyan-200/90 space-y-1">
                    {base10Result.map((line, i) => (
                      <div key={i} className={line === '' ? 'h-2' : ''}>{line}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Base 2 */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider flex items-center gap-2">
                <Binary className="w-4 h-4" /> Descomposición en Base 2
              </h3>
              <div className="mb-4">
                <label className="block text-sm mb-2 text-cyan-300/70">Número en Base 2 (Binario)</label>
                <input
                  type="text"
                  value={base2Input}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '' || /^[01]+$/.test(value)) setBase2Input(value);
                  }}
                  placeholder="Ej: 1111001"
                  className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                />
              </div>
              <button
                onClick={decomposeBase2}
                className="w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/30"
              >
                <Calculator className="w-4 h-4" /> Descomponer
              </button>
              {base2Result.length > 0 && (
                <div className="mt-4 bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <div className="font-mono text-sm text-cyan-200/90 space-y-1">
                    {base2Result.map((line, i) => (
                      <div key={i} className={line === '' ? 'h-2' : ''}>{line}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================= SECCIÓN: ERRORES ======================= */}
        {activeSection === 'errors' && (
          <div className="space-y-6">
            {Object.values(errorExamples).map((error, index) => (
              <div key={index} className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
                <h3 className="text-xl mb-3 text-cyan-300 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" /> {error.title}
                </h3>
                <p className="text-cyan-200/80 mb-4">{error.description}</p>
                <div className="bg-gradient-to-br from-blue-900/20 to-cyan-900/10 border border-blue-500/30 rounded-lg p-4 mb-4">
                  <div className="text-sm text-blue-200">
                    <span className="text-blue-300">Ejemplo: </span>{error.example}
                  </div>
                </div>
                <div className="bg-[#0d0d12]/70 rounded-lg p-4 border border-cyan-500/20">
                  <div className="text-xs text-cyan-400/60 mb-2">Código de ejemplo:</div>
                  <pre className="font-mono text-xs text-cyan-200/90 overflow-x-auto whitespace-pre">{error.code}</pre>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ======================= SECCIÓN: PUNTO FLOTANTE ======================= */}
        {activeSection === 'floating' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-xl mb-4 text-cyan-300 flex items-center gap-2">
                <Calculator className="w-5 h-5" /> ¿Por qué 0.1 + 0.2 ≠ 0.3?
              </h3>
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-[#0d0d12]/50 rounded-lg p-6 border border-cyan-500/20">
                  <div className="space-y-4 font-mono text-cyan-200">
                    <div><span className="text-cyan-400">const</span> a = <span className="text-green-300">{floatDemo.a}</span>;</div>
                    <div><span className="text-cyan-400">const</span> b = <span className="text-green-300">{floatDemo.b}</span>;</div>
                    <div><span className="text-cyan-400">const</span> sum = a + b;</div>
                    <div className="pt-2 border-t border-cyan-500/20"><div>sum = <span className="text-yellow-300">{floatDemo.sumString}</span></div></div>
                    <div className="pt-2 border-t border-cyan-500/20">
                      <div><span className="text-cyan-400">console.log</span>(sum === {floatDemo.expected});</div>
                      <div className="text-2xl mt-2">→ <span className={floatDemo.areEqual ? "text-green-400" : "text-red-400"}>{floatDemo.areEqual.toString()}</span></div>
                    </div>
                  </div>
                </div>
                <div className="bg-gradient-to-br from-red-900/20 to-orange-900/10 border border-red-500/30 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-3">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div className="text-red-200">
                      <div className="mb-2">¡La comparación es falsa!</div>
                      <div className="text-sm text-red-300/80">0.1 + 0.2 = {floatDemo.sumString}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-[#0d0d12]/70 rounded-lg p-6 border border-cyan-500/20">
                <h4 className="text-sm mb-3 text-cyan-300 uppercase tracking-wider">Explicación</h4>
                <div className="text-sm text-cyan-200/90 space-y-3 whitespace-pre-line">{floatDemo.explanation}</div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
               <h3 className="text-xl mb-4 text-cyan-300">Representación IEEE 754 (64 bits)</h3>
               <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20 mb-4">
                 <div className="font-mono text-sm text-cyan-200/90 space-y-2">
                    <div className="text-cyan-300">Estructura de un número flotante de 64 bits:</div>
                    <div className="flex gap-2 mt-3">
                      <div className="bg-red-900/30 border border-red-500/30 px-3 py-2 rounded">
                        <div className="text-xs text-red-300 mb-1">Signo</div><div>1 bit</div>
                      </div>
                      <div className="bg-blue-900/30 border border-blue-500/30 px-3 py-2 rounded">
                         <div className="text-xs text-blue-300 mb-1">Exponente</div><div>11 bits</div>
                      </div>
                      <div className="bg-green-900/30 border border-green-500/30 px-3 py-2 rounded flex-1">
                         <div className="text-xs text-green-300 mb-1">Mantisa (Fracción)</div><div>52 bits</div>
                      </div>
                    </div>
                 </div>
               </div>
            </div>
          </div>
        )}

        {/* ======================= SECCIÓN: FUENTES DE ERROR ======================= */}
        {activeSection === 'error-sources' && (
          <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
            <h3 className="text-xl mb-6 text-cyan-300 flex items-center gap-2">
              <TrendingDown className="w-5 h-5" /> Fuentes de Error en Análisis Numérico
            </h3>
            <div className="space-y-6">
              <div>
                <label className="block text-sm mb-3 text-cyan-300/70">Seleccione el tipo de error a demostrar:</label>
                <div className="space-y-2">
                  <button onClick={() => setErrorType('roundoff')} className={`w-full px-4 py-3 rounded-lg border text-left transition-all duration-200 ${errorType === 'roundoff' ? 'bg-gradient-to-br from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg' : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30'}`}>
                    <div className="mb-1">Error de Redondeo</div><div className="text-xs opacity-70">Pérdida de precisión al representar números</div>
                  </button>
                  <button onClick={() => setErrorType('truncation')} className={`w-full px-4 py-3 rounded-lg border text-left transition-all duration-200 ${errorType === 'truncation' ? 'bg-gradient-to-br from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg' : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30'}`}>
                    <div className="mb-1">Error de Truncamiento</div><div className="text-xs opacity-70">Aproximar procesos infinitos con finitos</div>
                  </button>
                  <button onClick={() => setErrorType('propagation')} className={`w-full px-4 py-3 rounded-lg border text-left transition-all duration-200 ${errorType === 'propagation' ? 'bg-gradient-to-br from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg' : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30'}`}>
                    <div className="mb-1">Error de Propagación</div><div className="text-xs opacity-70">Errores que se amplifican</div>
                  </button>
                </div>
              </div>

              <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                 {errorType === 'roundoff' && (
                   <div className="space-y-4">
                     <div><label className="block text-sm mb-2 text-cyan-300/70">Valor a sumar</label><input type="text" value={roundoffValue} onChange={(e) => setRoundoffValue(e.target.value)} className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50" /></div>
                     <div><label className="block text-sm mb-2 text-cyan-300/70">Iteraciones</label><input type="text" value={roundoffN} onChange={(e) => setRoundoffN(e.target.value)} className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50" /></div>
                   </div>
                 )}
                 {errorType === 'truncation' && (
                    <div className="space-y-4">
                      <div><label className="block text-sm mb-2 text-cyan-300/70">Valor x (para e^x)</label><input type="text" value={truncationX} onChange={(e) => setTruncationX(e.target.value)} className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50" /></div>
                      <div><label className="block text-sm mb-2 text-cyan-300/70">Términos</label><input type="text" value={truncationTerms} onChange={(e) => setTruncationTerms(e.target.value)} className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50" /></div>
                    </div>
                 )}
                 {errorType === 'propagation' && (
                    <div className="space-y-4">
                      <div><label className="block text-sm mb-2 text-cyan-300/70">Valor a</label><input type="text" value={propagationA} onChange={(e) => setPropagationA(e.target.value)} className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50" /></div>
                      <div><label className="block text-sm mb-2 text-cyan-300/70">Valor b</label><input type="text" value={propagationB} onChange={(e) => setPropagationB(e.target.value)} className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50" /></div>
                    </div>
                 )}
              </div>

              <button
                onClick={() => {
                  if (errorType === 'roundoff') demonstrateRoundoff();
                  else if (errorType === 'truncation') demonstrateTruncation();
                  else if (errorType === 'propagation') demonstratePropagation();
                }}
                className="w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/30"
              >
                <Calculator className="w-4 h-4" /> Demostrar Error
              </button>

              {errorResults.length > 0 && (
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20 max-h-[500px] overflow-auto">
                   <div className="font-mono text-sm text-cyan-200/90 space-y-1">
                      {errorResults.map((line, i) => (<div key={i} className={line === '' ? 'h-2' : ''}>{line}</div>))}
                   </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================= SECCIÓN: RAÍCES (NUEVA) ======================= */}
        {activeSection === 'roots' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* === Selector de Método (Tabs) === */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider flex items-center gap-2">
                <BarChart3 className="w-4 h-4" /> Seleccione el Método
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <button
                  onClick={() => setRootMethod('bisection')}
                  className={`px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                    rootMethod === 'bisection'
                      ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/20'
                      : 'bg-cyan-900/10 text-cyan-400 border-cyan-500/20 hover:bg-cyan-900/30'
                  }`}
                >
                  <div className="font-semibold text-sm">Método de Bisección</div>
                  <div className="text-xs opacity-70">Intervalo Cerrado [a,b]</div>
                </button>
                
                <button
                  onClick={() => setRootMethod('false-position')}
                  className={`px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                    rootMethod === 'false-position'
                      ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/20'
                      : 'bg-cyan-900/10 text-cyan-400 border-cyan-500/20 hover:bg-cyan-900/30'
                  }`}
                >
                  <div className="font-semibold text-sm">Regla Falsa</div>
                  <div className="text-xs opacity-70">Intervalo Cerrado [a,b]</div>
                </button>
                
                <button
                  onClick={() => setRootMethod('newton')}
                  className={`px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                    rootMethod === 'newton'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/20'
                      : 'bg-purple-900/10 text-purple-300 border-purple-500/20 hover:bg-purple-900/30'
                  }`}
                >
                  <div className="font-semibold text-sm">Newton-Raphson</div>
                  <div className="text-xs opacity-70">Abierto (Requiere Derivada)</div>
                </button>
                
                <button
                  onClick={() => setRootMethod('secant')}
                  className={`px-4 py-3 rounded-lg border text-left transition-all duration-200 ${
                    rootMethod === 'secant'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/20'
                      : 'bg-purple-900/10 text-purple-300 border-purple-500/20 hover:bg-purple-900/30'
                  }`}
                >
                  <div className="font-semibold text-sm">Método de la Secante</div>
                  <div className="text-xs opacity-70">Abierto (2 puntos iniciales)</div>
                </button>
              </div>
            </div>

            {/* === Formulario de Entrada Dinámico === */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-xl mb-6 text-cyan-300 flex items-center gap-2 border-b border-cyan-500/20 pb-2">
                 {rootMethod === 'bisection' && <Divide className="w-5 h-5" />}
                 {rootMethod === 'false-position' && <TrendingDown className="w-5 h-5" />}
                 {rootMethod === 'newton' && <Zap className="w-5 h-5 text-purple-400" />}
                 {rootMethod === 'secant' && <Activity className="w-5 h-5 text-purple-400" />}
                 
                 {rootMethod === 'bisection' && 'Configuración: Bisección'}
                 {rootMethod === 'false-position' && 'Configuración: Regla Falsa'}
                 {rootMethod === 'newton' && <span className="text-purple-300">Configuración: Newton-Raphson</span>}
                 {rootMethod === 'secant' && <span className="text-purple-300">Configuración: Secante</span>}
              </h3>

              <div className="space-y-4">
                {/* Función */}
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <div className="space-y-2">
                    <label className="block text-sm mb-2 text-cyan-300/70">Función f(x)</label>
                    <input
                      type="text"
                      value={funcStr}
                      onChange={(e) => setFuncStr(e.target.value)}
                      placeholder="Ej: x^3 - x - 2"
                      className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50 font-mono"
                    />
                    <div className="text-xs text-cyan-500/40">Sintaxis Python: x**2 para potencias, sin(x), exp(x), etc.</div>
                  </div>
                </div>

                {/* Inputs Variables (Intervalos o Puntos Iniciales) */}
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <div className="space-y-2">
                    <label className="block text-sm mb-2 text-cyan-300/70">
                      {(rootMethod === 'bisection' || rootMethod === 'false-position') && 'Intervalo [a, b]'}
                      {rootMethod === 'newton' && 'Punto inicial (x₀)'}
                      {rootMethod === 'secant' && 'Puntos iniciales (x₀, x₁)'}
                    </label>
                    <div className="flex gap-4">
                      <div className="flex-1">
                        <span className="text-xs text-cyan-500/50 mb-1 block">
                           {(rootMethod === 'bisection' || rootMethod === 'false-position') ? 'Límite inferior (a)' : 'Valor x₀'}
                        </span>
                        <input
                          type="text"
                          value={intervalA}
                          onChange={(e) => setIntervalA(e.target.value)}
                          placeholder="Ej: 1"
                          className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                        />
                      </div>
                      
                      {/* El segundo input se oculta si es Newton */}
                      {rootMethod !== 'newton' && (
                        <div className="flex-1">
                          <span className="text-xs text-cyan-500/50 mb-1 block">
                            {(rootMethod === 'bisection' || rootMethod === 'false-position') ? 'Límite superior (b)' : 'Valor x₁'}
                          </span>
                          <input
                            type="text"
                            value={intervalB}
                            onChange={(e) => setIntervalB(e.target.value)}
                            placeholder="Ej: 2"
                            className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Configuración Extra */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                      <label className="block text-sm mb-2 text-cyan-300/70">Tolerancia</label>
                      <input
                        type="text"
                        value={tolerance}
                        onChange={(e) => setTolerance(e.target.value)}
                        placeholder="Ej: 0.0001"
                        className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                      />
                    </div>
                    <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                      <label className="block text-sm mb-2 text-cyan-300/70">Iteraciones Máx.</label>
                      <input
                        type="text"
                        value={maxIter}
                        onChange={(e) => setMaxIter(e.target.value)}
                        placeholder="Ej: 50"
                        className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                      />
                    </div>
                </div>

                {/* Botón Resolver */}
                <button
                  onClick={() => {
                    if (rootMethod === 'bisection') solveBisection();
                    else if (rootMethod === 'false-position') solveFalsePosition();
                    else if (rootMethod === 'newton') solveNewton();
                    else if (rootMethod === 'secant') solveSecant();
                  }}
                  className={`w-full px-6 py-4 rounded-lg text-white font-bold tracking-wide transition-all duration-200 flex items-center justify-center gap-2 shadow-lg ${
                     (rootMethod === 'newton' || rootMethod === 'secant')
                     ? 'bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 shadow-purple-500/30'
                     : 'bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 shadow-cyan-500/30'
                  }`}
                >
                  <Calculator className="w-5 h-5" />
                  CALCULAR RAÍZ
                </button>

                {/* Resultados */}
                {rootResults.length > 0 && (
                  <div className="mt-4 bg-[#0d0d12]/80 rounded-lg p-4 border border-cyan-500/20 shadow-inner shadow-black/50 max-h-[400px] overflow-auto">
                    <div className="font-mono text-sm text-cyan-200/90 space-y-1">
                      {rootResults.map((line, i) => (
                        <div key={i} className={`${line === '' ? 'h-2' : ''} ${line.includes('RAÍZ') ? 'text-green-400 font-bold border-t border-b border-green-500/20 py-2 my-2' : ''} ${line.includes('ERROR') ? 'text-red-400 font-bold' : ''}`}>
                          {line}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}