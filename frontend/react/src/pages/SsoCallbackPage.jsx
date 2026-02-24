
// Página de callback para autenticação SSO.
// Aguarda autenticação do Clerk e redireciona para editais se autenticado.
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@clerk/react-router';

const SsoCallbackPage = () => {
  const navigate = useNavigate();
  const { isLoaded, isSignedIn } = useAuth();

  // Efeito: ao autenticar via SSO, redireciona para editais
  React.useEffect(() => {
    if (!isLoaded) return;
    if (isSignedIn) {
      navigate('/editais');
    }
  }, [isLoaded, isSignedIn, navigate]);

  return (
    <div className="grid">
      <div className="card">
        <div className="actions">
          <h2>Processando autenticação...</h2>
          {!isLoaded && <p>Aguardando Clerk...</p>}
          {isLoaded && !isSignedIn && <p>Erro: não autenticado pelo Clerk.</p>}
        </div>
      </div>
    </div>
  );
};

export default SsoCallbackPage;
