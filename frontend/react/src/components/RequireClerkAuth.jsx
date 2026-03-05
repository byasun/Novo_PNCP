import React from 'react';
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/react-router';

// Componente de proteção de rota usando Clerk.
// Exibe o conteúdo apenas se o usuário estiver autenticado pelo Clerk.
// Caso contrário, redireciona para a tela de login do Clerk.
export function RequireClerkAuth({ children }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
