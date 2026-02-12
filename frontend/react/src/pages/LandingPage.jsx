import React from 'react';

const clerkSignInUrl = import.meta.env.VITE_CLERK_SIGNIN_URL;
const clerkSignUpUrl = import.meta.env.VITE_CLERK_SIGNUP_URL;

const LandingPage = () => (
  <div className="grid">
    <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
      <h2>Bem-vindo ao Portal de Editais</h2>
      <p>Acesse editais públicos após autenticação.</p>
      <div className="actions" style={{ width: '100%' }}>
        <a className="btn" href={clerkSignInUrl} target="_blank" rel="noopener noreferrer">Login</a>
        <a className="btn" href={clerkSignUpUrl} target="_blank" rel="noopener noreferrer">Criar usuário</a>
      </div>
    </div>
  </div>
);

export default LandingPage;
