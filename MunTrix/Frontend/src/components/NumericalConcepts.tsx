import { useState, useEffect } from 'react';
import { Hash, Binary, AlertCircle, Calculator, Info } from 'lucide-react';
import { postJson, getJson } from '../api';

interface NumericalConceptsProps {
  useFractions: boolean;
}

type Section = 'positional' | 'errors' | 'floating';

interface FloatDemo {
  a: number;
  b: number;
  sum: number;
  expected: number;
  areEqual: boolean;
  sumString: string;
  explanation: string;
}

export function NumericalConcepts({ useFractions }: NumericalConceptsProps) {
  const [activeSection, setActiveSection] = useState<Section>('positional');
  
  // Estado para notación posicional
  const [base10Input, setBase10Input] = useState('84506');
  const [base2Input, setBase2Input] = useState('1111001');
  const [base10Result, setBase10Result] = useState<string[]>([]);
  const [base2Result, setBase2Result] = useState<string[]>([]);

  // Estado para punto flotante 
  const [floatDemo, setFloatDemo] = useState<FloatDemo | null>(null);

  useEffect(() => {
    // Cargar demo de punto flotante
    getJson<FloatDemo>('/api/numerical/floating-demo')
      .then(setFloatDemo)
      .catch(() => setFloatDemo(null));
  }, []);

  const decomposeBase10 = async () => {
    const num = base10Input.trim();

    if (!num) {
      setBase10Result(['Error: Ingrese un número en base 10']);
      return;
    }

    try {
      const data = await postJson<{ steps: string[]; error?: string }>('/api/numerical/base10', {
        number: num,
      });

      if (data.error) {
        setBase10Result([data.error]);
      } else {
        setBase10Result(data.steps);
      }
    } catch (e) {
      console.error(e);
      setBase10Result(['Error al comunicarse con el servidor.']);
    }
  };

  const decomposeBase2 = async () => {
    const num = base2Input.trim();

    if (!num) {
      setBase2Result(['Error: Ingrese un número en base 2']);
      return;
    }

    try {
      const data = await postJson<{ steps: string[]; error?: string }>('/api/numerical/base2', {
        number: num,
      });

      if (data.error) {
        setBase2Result([data.error]);
      } else {
        setBase2Result(data.steps);
      }
    } catch (e) {
      console.error(e);
      setBase2Result(['Error al comunicarse con el servidor.']);
    }
  };

  // Ejemplos de errores numéricos 
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
console.log('Underflow:', underflow);  // 0

// Ejemplo práctico de overflow
const factorial = (n: number): number => {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
};
console.log('200! =', factorial(200));  // Infinity (overflow)`
    },
    model: {
      title: 'Error del Modelo Matemático',
      description: 'Error introducido al simplificar un fenómeno real en un modelo matemático.',
      example: 'Modelar caída libre sin resistencia del aire cuando sí existe',
      code: `// Error del modelo matemático
// Modelo simple: h = h₀ - (1/2)gt²
// Modelo real: incluye resistencia del aire

const g = 9.81;  // gravedad (m/s²)
const h0 = 100;  // altura inicial (m)
const t = 3;     // tiempo (s)

// Modelo simplificado (sin resistencia del aire)
const hSimple = h0 - 0.5 * g * t * t;
console.log('Altura (modelo simple):', hSimple);  // 55.855 m

// En realidad, con resistencia del aire sería mayor
// El error del modelo es la diferencia entre el modelo
// y la realidad física`
    }
  };

  return (
    <div className="h-full bg-[#0a0a0f] overflow-auto">
      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8 pb-6 border-b border-cyan-500/20">
          <div className="flex items-center gap-3 mb-2">
            <Hash className="w-8 h-8 text-cyan-400" />
            <h2 className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
              Conceptos Numéricos
            </h2>
          </div>
          <p className="text-cyan-300/70">Representación de números y errores en computación</p>
        </div>

        {/* Navegación de secciones */}
        <div className="mb-6 flex gap-3">
          <button
            onClick={() => setActiveSection('positional')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'positional'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <Binary className="w-4 h-4" />
            Notación Posicional
          </button>
          <button
            onClick={() => setActiveSection('errors')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'errors'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <AlertCircle className="w-4 h-4" />
            Errores Numéricos
          </button>
          <button
            onClick={() => setActiveSection('floating')}
            className={`px-6 py-3 rounded-lg border transition-all duration-200 flex items-center gap-2 ${
              activeSection === 'floating'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30'
                : 'bg-cyan-900/20 text-cyan-300 border-cyan-500/30 hover:bg-cyan-900/40'
            }`}
          >
            <Calculator className="w-4 h-4" />
            Punto Flotante
          </button>
        </div>

        {/* Sección: Notación Posicional */}
        {activeSection === 'positional' && (
          <div className="grid grid-cols-2 gap-6">
            {/* Base 10 */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider flex items-center gap-2">
                <span className="text-xl">🔢</span>
                Descomposición en Base 10
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
                <Calculator className="w-4 h-4" />
                Descomponer
              </button>

              {base10Result.length > 0 && (
                <div className="mt-4 bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <div className="font-mono text-sm text-cyan-200/90 space-y-1">
                    {base10Result.map((line, i) => (
                      <div key={i} className={line === '' ? 'h-2' : ''}>
                        {line}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ejemplo */}
              <div className="mt-4 bg-gradient-to-br from-cyan-900/20 to-blue-900/10 border border-cyan-500/20 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <div className="text-xs text-cyan-300/80">
                    <div className="mb-1">Ejemplo:</div>
                    <div className="font-mono">84506 = 8×10⁴ + 4×10³ + 5×10² + 0×10¹ + 6×10⁰</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Base 2 */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-sm mb-4 text-cyan-300/90 uppercase tracking-wider flex items-center gap-2">
                <Binary className="w-4 h-4" />
                Descomposición en Base 2
              </h3>
              
              <div className="mb-4">
                <label className="block text-sm mb-2 text-cyan-300/70">Número en Base 2 (Binario)</label>
                <input
                  type="text"
                  value={base2Input}
                  onChange={(e) => setBase2Input(e.target.value)}
                  placeholder="Ej: 1111001"
                  className="w-full px-4 py-2 bg-[#0d0d12]/50 border border-cyan-500/30 rounded-lg text-cyan-100 placeholder-cyan-600/50 focus:outline-none focus:border-cyan-400/50"
                />
              </div>

              <button
                onClick={decomposeBase2}
                className="w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/30"
              >
                <Calculator className="w-4 h-4" />
                Descomponer
              </button>

              {base2Result.length > 0 && (
                <div className="mt-4 bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <div className="font-mono text-sm text-cyan-200/90 space-y-1">
                    {base2Result.map((line, i) => (
                      <div key={i} className={line === '' ? 'h-2' : ''}>
                        {line}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ejemplo */}
              <div className="mt-4 bg-gradient-to-br from-cyan-900/20 to-blue-900/10 border border-cyan-500/20 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <div className="text-xs text-cyan-300/80">
                    <div className="mb-1">Ejemplo:</div>
                    <div className="font-mono">1111001 = 1·2⁶ + 1·2⁵ + 1·2⁴ + 1·2³ + 0·2² + 0·2¹ + 1·2⁰</div>
                    <div className="font-mono mt-1">= 64 + 32 + 16 + 8 + 0 + 0 + 1 = 121</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Sección: Errores Numéricos */}
        {activeSection === 'errors' && (
          <div className="space-y-6">
            {Object.values(errorExamples).map((error, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10"
              >
                <h3 className="text-xl mb-3 text-cyan-300 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  {error.title}
                </h3>
                
                <p className="text-cyan-200/80 mb-4">
                  {error.description}
                </p>

                <div className="bg-gradient-to-br from-blue-900/20 to-cyan-900/10 border border-blue-500/30 rounded-lg p-4 mb-4">
                  <div className="text-sm text-blue-200">
                    <span className="text-blue-300">Ejemplo: </span>
                    {error.example}
                  </div>
                </div>

                <div className="bg-[#0d0d12]/70 rounded-lg p-4 border border-cyan-500/20">
                  <div className="text-xs text-cyan-400/60 mb-2">Código de ejemplo:</div>
                  <pre className="font-mono text-xs text-cyan-200/90 overflow-x-auto whitespace-pre">
                    {error.code}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Sección: Punto Flotante */}
        {activeSection === 'floating' && (
          <div className="space-y-6">
            {/* Demostración principal */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-xl mb-4 text-cyan-300 flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                ¿Por qué 0.1 + 0.2 ≠ 0.3?
              </h3>

              {!floatDemo ? (
                <div className="text-cyan-200/80 text-sm">
                  No se pudo cargar la demostración de punto flotante desde el servidor.
                </div>
              ) : (
                <>
                  {/* Demostración interactiva */}
                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div className="bg-[#0d0d12]/50 rounded-lg p-6 border border-cyan-500/20">
                      <div className="space-y-4 font-mono text-cyan-200">
                        <div>
                          <span className="text-cyan-400">const</span> a = <span className="text-green-300">{floatDemo.a}</span>;
                        </div>
                        <div>
                          <span className="text-cyan-400">const</span> b = <span className="text-green-300">{floatDemo.b}</span>;
                        </div>
                        <div>
                          <span className="text-cyan-400">const</span> sum = a + b;
                        </div>
                        <div className="pt-2 border-t border-cyan-500/20">
                          <div>sum = <span className="text-yellow-300">{floatDemo.sumString}</span></div>
                        </div>
                        <div className="pt-2 border-t border-cyan-500/20">
                          <div>
                            <span className="text-cyan-400">console.log</span>(sum === {floatDemo.expected});
                          </div>
                          <div className="text-2xl mt-2">
                            → <span className={floatDemo.areEqual ? "text-green-400" : "text-red-400"}>
                              {floatDemo.areEqual.toString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-red-900/20 to-orange-900/10 border border-red-500/30 rounded-lg p-6">
                      <div className="flex items-start gap-3 mb-3">
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        <div className="text-red-200">
                          <div className="mb-2">¡La comparación es falsa!</div>
                          <div className="text-sm text-red-300/80">
                            0.1 + 0.2 = {floatDemo.sumString}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Explicación detallada */}
                  <div className="bg-[#0d0d12]/70 rounded-lg p-6 border border-cyan-500/20">
                    <h4 className="text-sm mb-3 text-cyan-300 uppercase tracking-wider">Explicación</h4>
                    <div className="text-sm text-cyan-200/90 space-y-3 whitespace-pre-line">
                      {floatDemo.explanation}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Más ejemplos de problemas de punto flotante */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-xl mb-4 text-cyan-300">Más Ejemplos de Imprecisión</h3>
              
              <div className="space-y-4">
                <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20">
                  <pre className="font-mono text-sm text-cyan-200/90">
{`// Ejemplo 1: Pérdida de precisión
0.1 + 0.1 + 0.1 === 0.3  // false
// Resultado real: 0.30000000000000004

// Ejemplo 2: Asociatividad
(0.1 + 0.2) + 0.3 === 0.1 + (0.2 + 0.3)  // false!

// Ejemplo 3: División
1 / 10 === 0.1  // true (por casualidad en este caso)
// pero internamente 0.1 no es exacto

// Solución recomendada:
function sonIguales(a, b, epsilon = 1e-10) {
  return Math.abs(a - b) < epsilon;
}

sonIguales(0.1 + 0.2, 0.3)  // true`}
                  </pre>
                </div>

                <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/10 border border-green-500/30 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-green-200">
                      <div className="mb-2">Reglas importantes:</div>
                      <ul className="list-disc list-inside space-y-1 text-green-300/80">
                        <li>Nunca comparar flotantes con === o !==</li>
                        <li>Usar un epsilon (tolerancia) para comparaciones</li>
                        <li>Para dinero, usar enteros (centavos) en vez de flotantes</li>
                        <li>Para precisión exacta, considerar librerías como decimal.js</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Representación IEEE 754 */}
            <div className="bg-gradient-to-br from-[#16161d] to-[#1e1e2e] border border-cyan-500/30 rounded-xl p-6 shadow-lg shadow-cyan-500/10">
              <h3 className="text-xl mb-4 text-cyan-300">Representación IEEE 754 (64 bits)</h3>
              
              <div className="bg-[#0d0d12]/50 rounded-lg p-4 border border-cyan-500/20 mb-4">
                <div className="font-mono text-sm text-cyan-200/90 space-y-2">
                  <div className="text-cyan-300">Estructura de un número flotante de 64 bits:</div>
                  <div className="flex gap-2 mt-3">
                    <div className="bg-red-900/30 border border-red-500/30 px-3 py-2 rounded">
                      <div className="text-xs text-red-300 mb-1">Signo</div>
                      <div>1 bit</div>
                    </div>
                    <div className="bg-blue-900/30 border border-blue-500/30 px-3 py-2 rounded">
                      <div className="text-xs text-blue-300 mb-1">Exponente</div>
                      <div>11 bits</div>
                    </div>
                    <div className="bg-green-900/30 border border-green-500/30 px-3 py-2 rounded flex-1">
                      <div className="text-xs text-green-300 mb-1">Mantisa (Fracción)</div>
                      <div>52 bits</div>
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-cyan-300/70">
                    Total: 64 bits (Double precision floating point)
                  </div>
                </div>
              </div>

              <div className="text-sm text-cyan-200/80 space-y-2">
                <p>
                  Debido a esta representación limitada, la mayoría de números decimales 
                  no pueden ser representados exactamente en binario.
                </p>
                <p>
                  Solo fracciones que son sumas de potencias negativas de 2 se pueden 
                  representar exactamente (ej: 0.5, 0.25, 0.125, 0.75).
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
