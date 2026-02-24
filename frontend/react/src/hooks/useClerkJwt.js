import { useAuth } from '@clerk/react-router';

// Hook customizado para obter o JWT do usuário Clerk.
// Retorna a função fetchJwt (busca o JWT atual), o userId e o status de autenticação.
// Útil para acessar o token diretamente em componentes ou hooks.
export function useClerkJwt() {
  const { getToken, userId, isSignedIn } = useAuth();

  // Retorna o JWT atual do usuário Clerk
  const fetchJwt = async () => {
    if (!isSignedIn) return null;
    return await getToken();
  };

  return { fetchJwt, userId, isSignedIn };
}
