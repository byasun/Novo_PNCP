import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { useClerkApi } from '../hooks/useClerkApi';
import { useAuth } from '@clerk/react-router';

const LoginPage = () => {
  const { fetchWithClerk } = useClerkApi();
  const { isSignedIn } = useAuth();

  React.useEffect(() => {
    if (isSignedIn) {
      fetchWithClerk('/api/register-clerk-user', { method: 'POST' })
        .then(res => {
          console.log('Usuário Clerk registrado:', res);
        })
        .catch(err => {
          console.error('Erro ao registrar Clerk:', err);
        });
    }
  }, [isSignedIn]);

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
