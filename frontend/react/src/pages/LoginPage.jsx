import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { useClerkApi } from '../hooks/useClerkApi';
import { useAuth } from '@clerk/react-router';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const { fetchWithClerk } = useClerkApi();
  const { isSignedIn } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    console.log('[LoginPage] isSignedIn:', isSignedIn);
    if (isSignedIn) {
      fetchWithClerk('/api/register-clerk-user', { method: 'POST' })
        .then(res => {
          console.log('Usuário Clerk registrado:', res);
        })
        .catch(err => {
          console.error('Erro ao registrar Clerk:', err);
        });
      navigate('/editais');
    }
  }, [isSignedIn, navigate, fetchWithClerk]);

  return (
    <div className="grid">
      <div className="card">
        <div className="actions">
          <SignIn routing="path" path="/login" />
        </div>
        <div style={{marginTop: '2rem', color: 'red'}}>
          <strong>Diagnóstico:</strong>
          <pre>{JSON.stringify({ isSignedIn }, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
