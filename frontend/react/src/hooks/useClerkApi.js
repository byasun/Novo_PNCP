import { useCallback } from 'react';
import { useAuth } from '../App';

// Hook customizado para requisições autenticadas com Clerk.
// Retorna a função fetchWithClerk, que faz fetch incluindo o JWT do usuário Clerk no header Authorization.
// Útil para acessar endpoints protegidos no backend.
export function useClerkApi() {
  const { clerkToken } = useAuth();

    // Memoiza a função para garantir referência estável
    const fetchWithClerk = useCallback(
      async (url, options = {}) => {
        if (!clerkToken) throw new Error('Usuário não autenticado');
        const res = await fetch(url, {
          ...options,
          headers: {
            ...(options.headers || {}),
            Authorization: `Bearer ${clerkToken}`,
            'Content-Type': 'application/json',
          },
        });
        if (!res.ok) throw new Error('Erro na requisição');
        return res.json();
      },
      [clerkToken]
    );

    return fetchWithClerk;
}
