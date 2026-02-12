import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SsoCallbackRedirect = () => { 
  const navigate = useNavigate();

  useEffect(() => {
    navigate('/editais', { replace: true });
  }, [navigate]);

  return null;
};

export default SsoCallbackRedirect;
