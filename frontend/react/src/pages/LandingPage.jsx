import React from 'react';
import { useAuth } from '@clerk/react-router';
import { useNavigate } from 'react-router-dom';

const clerkSignInUrl = import.meta.env.VITE_CLERK_SIGNIN_URL;
const clerkSignUpUrl = import.meta.env.VITE_CLERK_SIGNUP_URL;

const LandingPage = () => {
  const { isSignedIn } = useAuth();
  const navigate = useNavigate();
  React.useEffect(() => {
    console.log('[LandingPage] isSignedIn:', isSignedIn);
    if (isSignedIn) {
      navigate('/editais');
    }
  }, [isSignedIn, navigate]);
  return (
    <div className="grid">
      <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', maxWidth: '1024px', margin: '2rem auto', padding: '1rem 1.2rem' }}>
        <h2>Bem-vindo ao Portal de Editais</h2>
        <p>Acesse editais públicos após autenticação.</p>
        <div className="actions" style={{ width: '100%' }}>
          <a className="btn" href={clerkSignInUrl} target="_blank" rel="noopener noreferrer">Login</a>
          <a className="btn" href={clerkSignUpUrl} target="_blank" rel="noopener noreferrer">Criar usuário</a>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
