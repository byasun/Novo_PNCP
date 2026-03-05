import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SignIn, useAuth } from '@clerk/clerk-react';
import { useClerkApi } from '../hooks/useClerkApi';

// Página de login do sistema.
// Exibe o componente de autenticação Clerk e, ao autenticar, registra o usuário e redireciona para editais.
const LoginPage = () => {
  const { fetchWithClerk } = useClerkApi();
  const { authStatus } = useAuth();
  const navigate = useNavigate();

  // Efeito: ao autenticar, registra usuário Clerk no backend e redireciona
  React.useEffect(() => {
    if (authStatus === 'authenticated') {
      fetchWithClerk('/api/register-clerk-user', { method: 'POST' })
        .then(res => {
          console.log('Usuário Clerk registrado:', res);
        })
        .catch(err => {
          console.error('Erro ao registrar Clerk:', err);
        });
      navigate('/editais');
    }
  }, [authStatus, navigate, fetchWithClerk]);

  return (
    <div className="grid">
      <div className="card">
        <div className="actions">
          <SignIn routing="path" path="/login" />
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
