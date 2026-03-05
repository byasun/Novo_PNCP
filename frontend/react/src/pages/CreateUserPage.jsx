import { useAuth } from '../App';
import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import { useClerkApi } from '../hooks/useClerkApi';

// Página para criação de usuário Clerk e registro no backend.
// Ao acessar autenticado, registra o usuário Clerk no backend.
// Se não autenticado, redireciona para /editais.
const CreateUserPage = () => {
  const { fetchWithClerk } = useClerkApi();
  const { authStatus } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (authStatus !== 'authenticated') {
      navigate('/editais');
    } else {
      // Registra usuário Clerk no backend
      fetchWithClerk('/api/register-clerk-user', { method: 'POST' })
        .then(res => {
          console.log('Usuário Clerk registrado:', res);
        })
        .catch(err => {
          console.error('Erro ao registrar Clerk:', err);
        });
    }
  }, [authStatus, navigate, fetchWithClerk]);

  return (
    <div className="grid">
      <div className="card">
        <div className="actions">
          <SignUp routing="path" path="/users/new" />
        </div>
      </div>
    </div>
  );
};

export default CreateUserPage;
