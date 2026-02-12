import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import { useClerkApi } from '../hooks/useClerkApi';
import { useAuth } from '@clerk/react-router';

const CreateUserPage = () => {
  const { fetchWithClerk } = useClerkApi();
  const { isSignedIn } = useAuth();

  // Quando usuário está autenticado, registra no backend
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
        <SignUp routing="path" path="/users/new" />
      </div>
    </div>
  );
};

export default CreateUserPage;
