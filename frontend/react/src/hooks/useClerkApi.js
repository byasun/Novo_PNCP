import { useAuth as useClerkAuth } from '@clerk/react-router';

export function useClerkApi() {
  const { getToken, isSignedIn } = useClerkAuth();

  const fetchWithClerk = async (url, options = {}) => {
    console.log('[Clerk] isSignedIn:', isSignedIn);
    // Tenta obter o token com template (default)
    let token = await getToken({ template: 'default' });
    if (!token) {
      token = await getToken();
    }
    console.log('[Clerk] JWT obtido:', token);
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
