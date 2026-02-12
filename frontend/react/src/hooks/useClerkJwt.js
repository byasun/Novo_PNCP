import { useAuth } from '@clerk/react-router';

export function useClerkJwt() {
  const { getToken, userId, isSignedIn } = useAuth();

  // Retorna o JWT atual do usuário Clerk
  const fetchJwt = async () => {
    if (!isSignedIn) return null;
    return await getToken();
  };

  return { fetchJwt, userId, isSignedIn };
}
