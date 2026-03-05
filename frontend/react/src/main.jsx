
// Arquivo de entrada principal da aplicação React.
// Responsável por montar o React no DOM e envolver a aplicação com os providers necessários.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { AuthProvider } from './App.jsx';
import { ClerkProvider } from '@clerk/react-router';
import { BrowserRouter } from 'react-router-dom';

// Obtém a chave pública do Clerk para autenticação
const clerkKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

// Monta a aplicação React no elemento root, envolvendo com BrowserRouter, ClerkProvider e AuthProvider
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <ClerkProvider publishableKey={clerkKey}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ClerkProvider>
    </BrowserRouter>
  </StrictMode>,
);
