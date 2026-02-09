import { useAuth as useClerkAuth } from '@clerk/clerk-react';

export function useClerkApi() {
  const { getToken } = useClerkAuth();

  const fetchWithClerk = async (url, options = {}) => {
    const token = await getToken();
    const res = await fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (!res.ok) throw new Error('Erro na requisição');
    return res.json();
  };

  return { fetchWithClerk };
}
