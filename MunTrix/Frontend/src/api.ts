const API_URL = 'http://localhost:5000';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export function postJson<TResponse, TBody = any>(
  path: string,
  body: TBody
): Promise<TResponse> {
  return request<TResponse>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function getJson<TResponse>(path: string): Promise<TResponse> {
  return request<TResponse>(path, { method: 'GET' });
}