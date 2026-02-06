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
  Link,
  Navigate,
  useNavigate,
  useParams,
  useLocation,
} from 'react-router-dom'
import './App.css'

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

const HomeRedirect = () => {
  const { authStatus } = useAuth()
  if (authStatus === 'authenticated') {
    return <Navigate to="/editais" replace />
  }
  return <Navigate to="/login" replace />
}

const LoginPage = () => {
  const { authStatus, login, setMessage } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', password: '' })

  useEffect(() => {
    if (authStatus === 'authenticated') {
      navigate('/editais', { replace: true })
    }
  }, [authStatus, navigate])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await login(form)
      navigate('/editais')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid">
      <form className="card" onSubmit={handleSubmit}>
        <h2>Login</h2>
        <label>
          Usuário
          <input
            value={form.username}
            onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
            placeholder="usuario"
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            placeholder="••••••"
            required
          />
        </label>
        <button className="btn" type="submit" disabled={loading}>
          Entrar
        </button>
        <p className="helper">
          Não tem conta? <Link to="/users/new">Criar usuário</Link>
        </p>
      </form>
    </div>
  )
}

const CreateUserPage = () => {
  const { createUser, setMessage } = useAuth()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ name: '', username: '', email: '', password: '', confirm: '' })

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await createUser(form)
      setMessage('Usuário criado com sucesso.')
      setForm({ name: '', username: '', email: '', password: '', confirm: '' })
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid">
      <form className="card" onSubmit={handleSubmit}>
        <h2>Novo usuário</h2>
        <label>
          Nome
          <input
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="Nome completo"
            required
          />
        </label>
        <label>
          Usuário
          <input
            value={form.username}
            onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
            placeholder="novo.usuario"
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
            placeholder="email@exemplo.com"
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            placeholder="Mínimo 6 caracteres"
            required
          />
        </label>
        <label>
          Confirmar senha
          <input
            type="password"
            value={form.confirm}
            onChange={(event) => setForm((prev) => ({ ...prev, confirm: event.target.value }))}
            placeholder="Repita a senha"
            required
          />
        </label>
        <button className="btn" type="submit" disabled={loading}>
          Criar usuário
        </button>
        <p className="helper">
          Já tem conta? <Link to="/login">Fazer login</Link>
        </p>
      </form>
    </div>
  )
}

const EditaisPage = () => {
  const { statusInfo, refreshStatus, setMessage } = useAuth()
  const [loading, setLoading] = useState(false)
  const [editais, setEditais] = useState([])
  const [search, setSearch] = useState('')

  const loadEditais = useCallback(async () => {
    try {
      const data = await fetchJson('/api/editais')
      setEditais(data.data || [])
    } catch (err) {
      setMessage(err.message)
    }
  }, [setMessage])

  useEffect(() => {
    loadEditais()
  }, [loadEditais])

  const handleTriggerUpdate = async () => {
    setLoading(true)
    setMessage('')
    try {
      const data = await fetchJson('/api/trigger-update', { method: 'POST' })
      setMessage(data.message || 'Atualização iniciada.')
      await refreshStatus()
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredEditais = useMemo(() => {
    if (!search) return editais
    const term = search.toLowerCase()
    return editais.filter((edital) => {
      const processo = edital?.processo || ''
      const cnpj = getEditalCnpj(edital)
      const razaoSocial = getEditalRazaoSocial(edital)
      const objeto = getEditalObjeto(edital)
      return (
        (processo || '').toLowerCase().includes(term) ||
        (cnpj || '').toLowerCase().includes(term) ||
        (razaoSocial || '').toLowerCase().includes(term) ||
        (objeto || '').toLowerCase().includes(term) ||
        String(edital?.valorTotalEstimado ?? '').toLowerCase().includes(term)
      )
    })
  }, [editais, search])

  // Helper to format date string
  const formatDateTime = (dateString) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '—';
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="stack">
      <div className="card card--inline">
        <div>
          <h2>Status</h2>
          <p>Total de editais: {statusInfo?.total_editais ?? editais.length}</p>
          <p>Última atualização: {formatDateTime(statusInfo?.last_update)}</p>
        </div>
        <div className="actions">
          <button className="btn" onClick={handleTriggerUpdate} disabled={loading}>
            Atualizar agora
          </button>
          <a className="btn btn--ghost" href="/download/editais.csv">
            Baixar CSV
          </a>
          <a className="btn btn--ghost" href="/download/editais.xlsx">
            Baixar XLSX
          </a>
        </div>
      </div>

      <div className="card">
        <div className="table__toolbar">
          <div>
            <h2>Editais</h2>
            <p>Total carregado: {filteredEditais.length}</p>
          </div>
          <input
            className="search"
            placeholder="Buscar por processo, CNPJ, razão social ou objeto"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="table">
          <div className="table__head">
            <span>CNPJ</span>
            <span>Razão social</span>
            <span>Objeto</span>
            <span>Valor estimado</span>
          </div>
          {filteredEditais.map((edital, index) => {
            const chave = getEditalKey(edital)
            const objeto = getEditalObjeto(edital)
            const cnpj = formatCNPJ(getEditalCnpj(edital))
            const razaoSocial = getEditalRazaoSocial(edital)
            const valorEstimado = edital?.valorTotalEstimado
            const key = chave || edital.id || edital.numero || index
            const content = (
              <>
                <span>{cnpj || '—'}</span>
                <span>{razaoSocial || '—'}</span>
                <span>{objeto || '—'}</span>
                <span>{formatCurrencyBRL(valorEstimado)}</span>
              </>
            )
            if (chave) {
              return (
                <Link className="table__row table__row--link" key={key} to={`/edital/${chave}`}>
                  {content}
                </Link>
              )
            }
            return (
              <div className="table__row" key={key}>
                {content}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

const EditalDetailPage = () => {
  const { editalKey } = useParams()
  const { setMessage } = useAuth()
  const [loading, setLoading] = useState(false)
  const [edital, setEdital] = useState(null)
  const [itens, setItens] = useState([])

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const editalData = await fetchJson(`/api/editais/${editalKey}`)
        setEdital(editalData.data)
        const itensData = await fetchJson(`/api/editais/${editalKey}/itens`)
        setItens(itensData.data || [])
      } catch (err) {
        setMessage(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [editalKey, setMessage])

  return (
    <div className="stack">
      <div className="card">
        <div className="card__title">
          <div>
            <h2>Detalhe do edital</h2>
            <p>{editalKey}</p>
          </div>
          <Link to="/editais" className="btn btn--ghost">
            Voltar
          </Link>
        </div>
        {loading && <p>Carregando detalhes...</p>}
          {!loading && edital && (
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">CNPJ</span>
                <span className="detail-value">{formatCNPJ(edital?.orgaoEntidade?.cnpj || edital?.cnpjOrgao)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Razão Social</span>
                <span className="detail-value">{edital?.orgaoEntidade?.razaoSocial || '—'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Data Abertura Proposta</span>
                <span className="detail-value">{formatDateBR(edital?.dataAberturaProposta)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Data Encerramento Proposta</span>
                <span className="detail-value">{formatDateBR(edital?.dataEncerramentoProposta)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Objeto da Compra</span>
                <span className="detail-value">{edital?.objetoCompra || edital?.objeto || '—'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Informação Complementar</span>
                <span className="detail-value">{edital?.informacaoComplementar || '—'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Valor Total Estimado</span>
                <span className="detail-value">{formatCurrencyBRL(edital?.valorTotalEstimado)}</span>
              </div>
            </div>
          )}
      </div>

      <div className="card">
        <h2>Itens</h2>
        <p>Total de itens: {itens.length}</p>
        <div className="table table--fullwidth">
          <div className="table__head" style={{ display: 'flex', width: '100%' }}>
            <span style={{ flex: 1, textAlign: 'left' }}>Descrição</span>
            <span style={{ flex: 1, textAlign: 'center' }}>Quantidade</span>
            <span style={{ flex: 1, textAlign: 'left' }}>Valor Unitário Estimado</span>
            <span style={{ flex: 1, textAlign: 'center' }}>Unidade</span>
          </div>
          {itens.map((item, index) => (
            <div className="table__row" key={item.id || item.numero || index} style={{ display: 'flex', width: '100%' }}>
              <span style={{ flex: 1, textAlign: 'left' }}>{item.descricao || item.item || '—'}</span>
              <span style={{ flex: 1, textAlign: 'center' }}>{item.quantidade || item.qtd || '—'}</span>
              <span style={{ flex: 1, textAlign: 'left' }}>{typeof item.valorUnitarioEstimado !== 'undefined' ? formatCurrencyBRL(item.valorUnitarioEstimado) : '—'}</span>
              <span style={{ flex: 1, textAlign: 'center' }}>{item.unidade || item.un || '—'}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const NotFoundPage = () => (
  <div className="card">
    <h2>Página não encontrada</h2>
    <p>Verifique a URL ou retorne ao início.</p>
    <Link className="btn" to="/editais">
      Ir para editais
    </Link>
  </div>
)

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomeRedirect />} />
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

export default App
