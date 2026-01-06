const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    next: { revalidate: 60 },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return (await response.json()) as T;
}
