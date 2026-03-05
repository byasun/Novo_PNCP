import React from 'react';
import { useClerkApi } from '../hooks/useClerkApi';

// Exemplo de componente que faz chamada autenticada à API protegida pelo Clerk.
// Demonstra como usar o hook useClerkApi para acessar endpoints protegidos.
export default function SecureClerkExample() {
  const { fetchWithClerk } = useClerkApi();

  // Função para chamar a API protegida e exibir o resultado
  const handleClick = async () => {
    try {
      const data = await fetchWithClerk('/api/secure-clerk');
      alert(JSON.stringify(data, null, 2));
    } catch (err) {
      alert('Erro: ' + err.message);
    }
  };

  return (
    <button onClick={handleClick}>
      Chamar API protegida pelo Clerk
    </button>
  );
}
