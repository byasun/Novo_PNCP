import React from 'react';
import { useClerkApi } from '../hooks/useClerkApi';

export default function SecureClerkExample() {
  const { fetchWithClerk } = useClerkApi();

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
