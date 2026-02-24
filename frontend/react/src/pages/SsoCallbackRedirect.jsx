
// Página de redirecionamento após callback SSO.
// Redireciona automaticamente para a listagem de editais.
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SsoCallbackRedirect = () => { 
  const navigate = useNavigate();

  // Efeito: redireciona para /editais ao montar
  useEffect(() => {
    navigate('/editais', { replace: true });
  }, [navigate]);

  return null;
};

export default SsoCallbackRedirect;
