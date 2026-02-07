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
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
} from 'react-router-dom'
import './App.css'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import CreateUserPage from './pages/CreateUserPage'
import EditaisPage from './pages/EditaisPage'
import EditalDetailPage from './pages/EditalDetailPage'
import NotFoundPage from './pages/NotFoundPage'

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
  const [authStatus, setAuthStatus] = useState('loading')
  const [statusInfo, setStatusInfo] = useState(null)
  const [message, setMessage] = useState('')

  const refreshStatus = useCallback(async () => {
    try {
      const data = await fetchJson('/api/status')
      setStatusInfo(data)
      setAuthStatus('authenticated')
      return true
    } catch (err) {
      if (err.status === 401) {
        setAuthStatus('unauthenticated')
        setStatusInfo(null)
        return false
      }
      setMessage(err.message)
      return false
    }
  }, [])

  useEffect(() => {
    refreshStatus()
  }, [refreshStatus])

  const login = async (payload) => {
    await fetchJson('/login', { method: 'POST', body: JSON.stringify(payload) })
    await refreshStatus()
  }

  const logout = async () => {
    await fetchJson('/logout', { method: 'POST' })
    setAuthStatus('unauthenticated')
    setStatusInfo(null)
  }

  const createUser = async (payload) => {
    await fetchJson('/users/new', { method: 'POST', body: JSON.stringify(payload) })
  }

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
    </AuthContext.Provider>
  )
}

const Layout = ({ children }) => {
  const { authStatus, logout, message, setMessage, statusInfo } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (message) {
      setMessage('')
    }
  }, [location.pathname, message, setMessage])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="app">
      <header className="app__header">
        <div>
          <p className="app__eyebrow">PNCP</p>
          <h1>Portal de Editais</h1>
        </div>
        {authStatus === 'authenticated' && (
          <div className="nav">
            <span>
              {statusInfo?.name || statusInfo?.username || 'Usuário'}
            </span>
            <button className="btn btn--ghost" onClick={handleLogout}>
              Sair
            </button>
          </div>
        )}
      </header>
      {message && <div className="alert">{message}</div>}
      {children}
    </div>
  )
}

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
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/users/new" element={<CreateUserPage />} />
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
      </AuthProvider>
    </BrowserRouter>
  )
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
  fetchJson
}

export default App
