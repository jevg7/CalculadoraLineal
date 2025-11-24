// Función para calcular el máximo común divisor
function gcd(a: number, b: number): number {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b !== 0) {
    const temp = b;
    b = a % b;
    a = temp;
  }
  return a;
}

// Convertir decimal a fracción
export function decimalToFraction(decimal: number, tolerance: number = 0.0001): string {
  if (Math.abs(decimal) < tolerance) return '0';
  if (!isFinite(decimal)) return decimal.toString();

  const sign = decimal < 0 ? '-' : '';
  decimal = Math.abs(decimal);

  // Si es un número entero
  if (Math.abs(decimal - Math.round(decimal)) < tolerance) {
    return sign + Math.round(decimal).toString();
  }

  // Algoritmo de fracciones continuas
  let numerator = 1;
  let denominator = 1;
  let tempDecimal = decimal;

  const maxIterations = 20;
  for (let i = 0; i < maxIterations; i++) {
    const wholePart = Math.floor(tempDecimal);
    const fractionalPart = tempDecimal - wholePart;

    if (fractionalPart < tolerance) {
      numerator = wholePart * numerator + (i > 0 ? 1 : 0);
      break;
    }

    const newNumerator = wholePart * numerator + denominator;
    denominator = numerator;
    numerator = newNumerator;

    tempDecimal = 1 / fractionalPart;

    // Verificar si hemos encontrado una aproximación suficientemente buena
    const approximation = numerator / denominator;
    if (Math.abs(decimal - approximation) < tolerance) {
      break;
    }
  }

  // Simplificar la fracción
  const divisor = gcd(Math.round(decimal * denominator), denominator);
  numerator = Math.round(decimal * denominator) / divisor;
  denominator = denominator / divisor;

  if (denominator === 1) {
    return sign + numerator.toString();
  }

  return sign + numerator + '/' + denominator;
}

// Formatear número según el modo (decimal o fracción)
export function formatNumber(value: number, useFractions: boolean, decimals: number = 4): string {
  if (useFractions) {
    return decimalToFraction(value);
  }
  return value.toFixed(decimals);
}
