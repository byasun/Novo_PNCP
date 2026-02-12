// Formata CNPJ para XX.XXX.XXX/XXXX-XX
const formatCNPJ = (cnpj) => {
  if (!cnpj) return '—';
  const digits = String(cnpj).replace(/\D/g, '');
  if (digits.length !== 14) return cnpj;
  return `${digits.slice(0,2)}.${digits.slice(2,5)}.${digits.slice(5,8)}/${digits.slice(8,12)}-${digits.slice(12,14)}`;
}

// Formata datas para DD/MM/YYYY
const formatDateBR = (dateString) => {
  if (!dateString) return '—';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}


import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { useClerkApi } from './hooks/useClerkApi';
import {
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
} from 'react-router-dom'
import SsoCallbackPage from './pages/SsoCallbackPage';
import SsoCallbackRedirect from './pages/SsoCallbackRedirect';
import './App.css'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import CreateUserPage from './pages/CreateUserPage'
import EditaisPage from './pages/EditaisPage'
import EditalDetailPage from './pages/EditalDetailPage'
import NotFoundPage from './pages/NotFoundPage'

import Header from './components/Header'
import Navbar from './components/Navbar'
import Footer from './components/Footer'

const AuthContext = createContext(null)

const API_BASE = import.meta.env.VITE_API_URL || ''

const normalizedBase = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE

const buildUrl = (path) => {
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (!normalizedBase) return path
  return `${normalizedBase}${path}`
}

const fetchJson = async (path, options = {}) => {
  const res = await fetch(buildUrl(path), {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.message || data.error || 'Erro na requisição')
    err.status = res.status
    throw err
  }
  return data
}

const getEditalKey = (edital) => {
  if (!edital) return ''
  const cnpj = edital?.orgaoEntidade?.cnpj || edital?.cnpjOrgao
  const ano = edital?.anoCompra ?? edital?.ano
  const numero = edital?.numeroCompra ?? edital?.numero
  if (cnpj && (ano || ano === 0) && (numero || numero === 0)) {
    return `${cnpj}_${ano}_${numero}`
  }
  return edital.chave || edital.id || ''
}

const getEditalObjeto = (edital) => edital?.objeto || edital?.objetoCompra || ''

const getEditalModalidade = (edital) => edital?.modalidade || edital?.modalidadeNome || ''

const getEditalCnpj = (edital) => edital?.orgaoEntidade?.cnpj || edital?.cnpjOrgao || ''

const getEditalRazaoSocial = (edital) => edital?.orgaoEntidade?.razaoSocial || ''

const formatCurrencyBRL = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return '-'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(numeric)
}

const useAuth = () => useContext(AuthContext)

const AuthProvider = ({ children }) => {
  const [authStatus, setAuthStatus] = useState('loading');
  const [statusInfo, setStatusInfo] = useState(null);
  const [message, setMessage] = useState('');
  const { fetchWithClerk } = useClerkApi();

  const refreshStatus = useCallback(async () => {
    // Primeiro tenta autenticação local
    try {
      const data = await fetchJson('/api/status');
      setStatusInfo(data);
      setAuthStatus('authenticated');
      return true;
    } catch (err) {
      // Se não autenticado localmente, tenta Clerk
      if (err.status === 401) {
        try {
          const clerkData = await fetchWithClerk('/api/clerk-status');
          setStatusInfo(clerkData);
          setAuthStatus('authenticated');
          return true;
        } catch (clerkErr) {
          setAuthStatus('unauthenticated');
          setStatusInfo(null);
          return false;
        }
      }
      setMessage(err.message);
      return false;
    }
  }, [fetchWithClerk]);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  const login = async (payload) => {
    await fetchJson('/login', { method: 'POST', body: JSON.stringify(payload) });
    await refreshStatus();
  };

  const logout = async () => {
    await fetchJson('/logout', { method: 'POST' });
    setAuthStatus('unauthenticated');
    setStatusInfo(null);
  };

  const createUser = async (payload) => {
    await fetchJson('/users/new', { method: 'POST', body: JSON.stringify(payload) });
  };

  return (
    <AuthContext.Provider
      value={{
        authStatus,
        statusInfo,
        message,
        setMessage,
        refreshStatus,
        login,
        logout,
        createUser,
      }}
    >
      {children}
      <Footer>
        <div style={{ textAlign: 'center', padding: '1rem', fontSize: '0.9em', color: '#888' }}>
          &copy; {new Date().getFullYear()} PNCP - Todos os direitos reservados.
        </div>
      </Footer>
    </AuthContext.Provider>
  );
};

const Layout = ({ children, onLogout }) => {
  const { authStatus, message, setMessage, statusInfo } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (message) {
      setMessage('');
    }
  }, [location.pathname, message, setMessage]);

  return (
    <div className="app">
      <Header>
        <div>
          <p className="app__eyebrow">PNCP</p>
          <h1>Portal de Editais</h1>
        </div>
        {authStatus === 'authenticated' && (
          <Navbar>
            <span>
              {statusInfo?.name || statusInfo?.username || 'Usuário'}
            </span>
            <button className="btn btn--ghost" onClick={onLogout}>
              Sair
            </button>
          </Navbar>
        )}
      </Header>
      {message && <div className="alert">{message}</div>}
      {children}
    </div>
  );
};

const RequireAuth = ({ children }) => {
  const { authStatus } = useAuth()
  if (authStatus === 'loading') {
    return <div className="card">Carregando...</div>
  }
  if (authStatus !== 'authenticated') {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Layout onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/users/new" element={<CreateUserPage />} />
        <Route path="/users/new/sso-callback" element={<SsoCallbackPage />} />
        <Route path="/login/sso-callback" element={<SsoCallbackRedirect />} />
        <Route
          path="/editais"
          element={
            <RequireAuth>
              <EditaisPage />
            </RequireAuth>
          }
        />
        <Route
          path="/edital/:editalKey"
          element={
            <RequireAuth>
              <EditalDetailPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  );
}

export {
  useAuth,
  formatCNPJ,
  getEditalCnpj,
  getEditalRazaoSocial,
  getEditalObjeto,
  getEditalKey,
  formatCurrencyBRL,
  formatDateBR,
  fetchJson,
  AuthProvider
}

export default App
